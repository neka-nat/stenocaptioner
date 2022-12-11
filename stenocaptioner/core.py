import json
import os
import re

import whisper
import youtube_dl
from moviepy import editor
from moviepy.video.io.VideoFileClip import VideoFileClip

from .move_funcs import arrive, cascade, typing
from .utils import insert_newlines

_lang_scale = {"en": 2, "ja": 1}


def speech_to_text_segments(url: str, language: str, model_type: str, verbose: bool = True) -> list:
    """Transcribe speech to text segments.

    Args:
        url: URL of the video.
        language: Language of the video.
        model_type: Model type of the video.
        verbose: Whether to print the progress. Defaults to True.

    Returns:
        list: List of text segments.
    """
    model = whisper.load_model(model_type)
    result = model.transcribe(url, verbose=verbose, language=language)
    return result["segments"]


def annotate(
    clip,
    text: str,
    text_color: str,
    language: str,
    background_color: str,
    contour_color: str,
    contour_width: int,
    fontsize: int,
    font: str,
    fadein_duration: float,
    fadeout_duration: float,
    letter_effect: str,
    bottom_margin: float,
):
    n_line = text.count("\n") + 1
    if letter_effect == "none":
        txtclip = editor.TextClip(
            text,
            fontsize=fontsize,
            font=font,
            color=text_color,
            bg_color=background_color,
            stroke_color=contour_color,
            stroke_width=contour_width,
        )
        txt_h = n_line * fontsize + clip.h * bottom_margin
        txtclip = txtclip.set_position(("center", clip.h - txt_h)).set_duration(clip.duration)
        if fadein_duration > 0.0:
            txtclip = txtclip.crossfadein(fadein_duration)
        if fadeout_duration > 0.0:
            txtclip = txtclip.crossfadeout(fadeout_duration)
        cvc = editor.CompositeVideoClip([clip, txtclip])
    elif letter_effect in ["typing", "arrive", "cascade"]:
        func_map = {"typing": typing, "arrive": arrive, "cascade": cascade}
        letters = [
            editor.TextClip(
                s,
                fontsize=fontsize,
                font=font,
                color=text_color,
                bg_color=background_color,
                stroke_color=contour_color,
                stroke_width=contour_width,
            )
            for s in text
            if s != "\n"
        ]
        if fadein_duration > 0.0:
            letters = [letter.crossfadein(fadein_duration) for letter in letters]
        if fadeout_duration > 0.0:
            letters = [letter.crossfadeout(fadeout_duration) for letter in letters]
        text_lines = text.split("\n")
        cnt = 0
        pos = 0
        for letter in letters:
            txt_h = (n_line - cnt) * fontsize + clip.h * bottom_margin
            font_w = fontsize // _lang_scale.get(language, 2)
            letter.screenpos = (pos * font_w - len(text_lines[cnt]) * font_w / 2 + clip.w / 2, clip.h - txt_h)
            if pos == len(text_lines[cnt]) - 1:
                cnt += 1
                pos = 0
            else:
                pos += 1
        letters = [
            letter.set_position(func_map[letter_effect](letter.screenpos, i, 1.0 / len(letters)))
            for i, letter in enumerate(letters)
        ]
        cvc = editor.CompositeVideoClip([clip] + letters)
    else:
        raise ValueError(f"letter_effect {letter_effect} is not supported.")
    return cvc.set_duration(clip.duration)


def text_to_caption(
    url: str,
    segments: list,
    text_color: str,
    background_color: str,
    contour_color: str,
    contour_width: int,
    fontsize: int,
    font: str,
    language: str,
    fadein_duration: float,
    fadeout_duration: float,
    letter_effect: str,
    side_margin: float,
    bottom_margin: float,
):
    """Add captions to a video.

    Args:
        url: URL of the video.
        segments: List of segments.
        text_color: Color of the text.
        background_color: Color of the background.
        contour_color: Color of the contour.
        contour_width: Width of the contour.
        fontsize: Font size.
        font: Font name.
        language: Language of the text.
        fadein_duration: Duration of the fade-in effect.
        fadeout_duration: Duration of the fade-out effect.
        letter_effect: Effect of the letters.
        side_margin: Margin of the text from the side of the video.
        bottom_margin: Margin of the text from the bottom of the video.
    """

    video = VideoFileClip(url)

    width = video.w
    side_margin = int(side_margin * video.w)
    max_text_length = (width + side_margin) // fontsize * _lang_scale.get(language, 2)

    for seg in segments:
        if len(seg["text"]) // _lang_scale.get(language, 2) * fontsize + side_margin > width:
            seg["text"] = insert_newlines(seg["text"], max_text_length, language)

    annotated_clips = [
        annotate(
            video.subclip(min(seg["start"], video.duration), min(seg["end"], video.duration)),
            text=seg["text"],
            text_color=text_color,
            language=language,
            background_color=background_color,
            contour_color=contour_color,
            contour_width=contour_width,
            fontsize=fontsize,
            font=font,
            fadein_duration=fadein_duration,
            fadeout_duration=fadeout_duration,
            letter_effect=letter_effect,
            bottom_margin=bottom_margin,
        )
        for seg in segments
    ]

    final_clip = editor.concatenate_videoclips(annotated_clips)
    prefix_url, ext = os.path.splitext(url)
    final_clip.write_videofile(f"{prefix_url}_captioned{ext}")
    print(f"\n[stenocaptioner] Captioned Video saved as {prefix_url}_captioned{ext}.")


def main(args):
    total_steps = 2
    current_step = 1
    if re.match("https?://www.youtube.com/", args.url):
        total_steps = 3
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": "%(id)s.%(ext)s",
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print(
                f"\n[stenocaptioner]({current_step}/{total_steps} step) This url is a youtube video. Downloading it first..."
            )
            ydl.download([args.url])
            info = ydl.extract_info(args.url, download=False)
            args.url = f"{info['id']}.{info['ext']}"
            current_step += 1

    print(f"\n[stenocaptioner]({current_step}/{total_steps} step) Transcribing speech to text...")
    if args.load_text is None:
        segments = speech_to_text_segments(args.url, language=args.language, model_type=args.model_type)
    else:
        with open(args.load_text, "r") as f:
            segments = json.load(f)
    current_step += 1
    if args.save_text:
        with open("transcript.json", "w") as f:
            json.dump(segments, f, indent=4)
        print(f"\n[stenocaptioner] Transcribed text saved as transcript.json.")
    print(f"\n[stenocaptioner]({current_step}/{total_steps} step) Adding captions to video...")
    text_to_caption(
        args.url,
        segments,
        text_color=args.text_color,
        background_color=args.background_color,
        contour_color=args.contour_color,
        contour_width=args.contour_width,
        fontsize=args.fontsize,
        font=args.font,
        language=args.language,
        fadein_duration=args.fadein_duration,
        fadeout_duration=args.fadeout_duration,
        letter_effect=args.letter_effect,
        side_margin=args.side_margin,
        bottom_margin=args.bottom_margin,
    )


def cli():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("url", type=str, help="URL of the video.")
    parser.add_argument("--language", type=str, default="en", help="Language of the text.")
    parser.add_argument(
        "--model-type",
        type=str,
        default="medium",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model type.",
    )
    parser.add_argument("--text-color", type=str, default="white", help="Color of the text.")
    parser.add_argument("--background-color", type=str, default="transparent", help="Color of the background.")
    parser.add_argument("--contour-color", type=str, default=None, help="Color of the contour.")
    parser.add_argument("--contour-width", type=int, default=1, help="Width of the contour.")
    parser.add_argument("--font", type=str, default="VL-Gothic-Regular", help="Font name.")
    parser.add_argument("--fontsize", type=int, default=50, help="Font size.")
    parser.add_argument("--fadein-duration", type=float, default=0.0, help="Duration of the fade-in effect.")
    parser.add_argument("--fadeout-duration", type=float, default=0.0, help="Duration of the fade-out effect.")
    parser.add_argument("--save-text", action="store_true", help="Save the transcribed text.")
    parser.add_argument("--load-text", type=str, default=None, help="Load the transcribed text.")
    parser.add_argument(
        "--letter-effect",
        type=str,
        default="none",
        choices=["none", "typing", "arrive", "cascade"],
        help="Effect of the letters.",
    )
    parser.add_argument(
        "--side-margin", type=float, default=0.0, help="Margin of the text from the side of the video."
    )
    parser.add_argument(
        "--bottom-margin", type=float, default=0.05, help="Margin of the text from the bottom of the video."
    )
    args = parser.parse_args()
    main(args)
