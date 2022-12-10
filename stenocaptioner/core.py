import json
import os
import re

import whisper
import youtube_dl
from moviepy import editor
from moviepy.video.io.VideoFileClip import VideoFileClip

from .move_funcs import arrive
from .utils import insert_newlines

_lang_scale = {"en": 2, "ja": 1}


def speech_to_text_segments(url: str, language: str, model_type: str, verbose: bool = True) -> list:
    model = whisper.load_model(model_type)
    result = model.transcribe(url, verbose=verbose, language=language)
    return result["segments"]


def move_letters(letters, funcpos):
    return [letter.set_position(funcpos(letter.screenpos, i, len(letters))) for i, letter in enumerate(letters)]


def annotate(
    clip,
    text: str,
    text_color: str,
    fontsize: int,
    font: str,
    fadein_duration: float,
    fadeout_duration: float,
    letter_effect: str,
):
    txtclip = editor.TextClip(text, fontsize=fontsize, font=font, color=text_color)
    n_line = text.count("\n") + 1
    txt_h = n_line * fontsize + clip.h * 0.05
    txtclip = txtclip.set_position(("center", clip.h - txt_h)).set_duration(clip.duration)
    if fadein_duration > 0.0:
        txtclip = txtclip.crossfadein(fadein_duration)
    if fadeout_duration > 0.0:
        txtclip = txtclip.crossfadeout(fadeout_duration)
    if letter_effect == "none":
        cvc = editor.CompositeVideoClip([clip, txtclip])
    elif letter_effect == "arrive":
        letters = [editor.TextClip(s, fontsize=fontsize, font=font, color=text_color) for s in text if s != "\n"]
        text_lines = text.split("\n")
        cnt = 0
        pos = 0
        for letter in letters:
            txt_h = (n_line - cnt) * fontsize + clip.h * 0.05
            letter.screenpos = (pos * fontsize - len(text_lines[cnt]) * fontsize / 2 + clip.w / 2, clip.h - txt_h)
            if pos == len(text_lines[cnt]) - 1:
                cnt += 1
                pos = 0
            else:
                pos += 1
        cvc = editor.CompositeVideoClip([clip] + move_letters(letters, arrive))
    else:
        raise ValueError(f"letter_effect {letter_effect} is not supported.")
    return cvc.set_duration(clip.duration)


def text_to_caption(
    url: str,
    segments: list,
    text_color: str,
    fontsize: int,
    font: str,
    language: str,
    fadein_duration: float,
    fadeout_duration: float,
    letter_effect: str,
):
    video = VideoFileClip(url)

    width = video.w
    max_text_length = width // fontsize * _lang_scale.get(language, 2)

    for seg in segments:
        if len(seg["text"]) // _lang_scale.get(language, 2) * fontsize > width:
            seg["text"] = insert_newlines(seg["text"], max_text_length, language)

    annotated_clips = [
        annotate(
            video.subclip(min(seg["start"], video.duration), min(seg["end"], video.duration)),
            text=seg["text"],
            text_color=text_color,
            fontsize=fontsize,
            font=font,
            fadein_duration=fadein_duration,
            fadeout_duration=fadeout_duration,
            letter_effect=letter_effect,
        )
        for seg in segments
    ]

    final_clip = editor.concatenate_videoclips(annotated_clips)
    prefix_url, ext = os.path.splitext(url)
    final_clip.write_videofile(f"{prefix_url}_captioned{ext}")
    print(f"\n[stenocaptioner] Captioned Video saved as {prefix_url}_captioned{ext}.")


def main(args):
    if re.match("https?://www.youtube.com/", args.url):
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": "%(id)s.%(ext)s",
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("\n[stenocaptioner] This url is a youtube video. Downloading it first...")
            ydl.download([args.url])
            info = ydl.extract_info(args.url, download=False)
            args.url = f"{info['id']}.{info['ext']}"

    print("\n[stenocaptioner] Transcribing speech to text...")
    if args.load_text is None:
        segments = speech_to_text_segments(args.url, language=args.language, model_type=args.model_type)
    else:
        with open(args.load_text, "r") as f:
            segments = json.load(f)
    if args.save_text:
        with open("transcript.json", "w") as f:
            json.dump(segments, f, indent=4)
        print(f"\n[stenocaptioner] Transcribed text saved as transcript.json.")
    print("\n[stenocaptioner] Adding captions to video...")
    text_to_caption(
        args.url,
        segments,
        text_color=args.text_color,
        fontsize=args.fontsize,
        font=args.font,
        language=args.language,
        fadein_duration=args.fadein_duration,
        fadeout_duration=args.fadeout_duration,
        letter_effect=args.letter_effect,
    )


def cli():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("url", type=str)
    parser.add_argument("--language", type=str, default="en")
    parser.add_argument("--model-type", type=str, default="medium")
    parser.add_argument("--text-color", type=str, default="white")
    parser.add_argument("--font", type=str, default="VL-Gothic-Regular")
    parser.add_argument("--fontsize", type=int, default=50)
    parser.add_argument("--fadein-duration", type=float, default=0.0)
    parser.add_argument("--fadeout-duration", type=float, default=0.0)
    parser.add_argument("--save-text", action="store_true")
    parser.add_argument("--load-text", type=str, default=None)
    parser.add_argument("--letter-effect", type=str, default="none", choices=["none", "arrive"])
    args = parser.parse_args()
    main(args)
