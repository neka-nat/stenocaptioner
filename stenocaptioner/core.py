import os
import json
import re

import whisper
import youtube_dl
from moviepy import editor
from moviepy.video.io.VideoFileClip import VideoFileClip

from .utils import insert_newlines

_px_per_pt = 1.33
_lang_scale = {"en": 2, "ja": 1}


def speech_to_text_segments(url: str, language: str, model_type: str, verbose: bool = True) -> list:
    model = whisper.load_model(model_type)
    result = model.transcribe(url, verbose=verbose, language=language)
    return result["segments"]


def annotate(clip, text, text_color, fontsize, font, fade_duration):
    txtclip = editor.TextClip(text, fontsize=fontsize, font=font, color=text_color)
    txtclip = txtclip.set_pos(("center", "bottom"))
    if fade_duration > 0.0:
        txtclip = txtclip.set_duration(clip.duration).crossfadein(fade_duration)
    cvc = editor.CompositeVideoClip([clip, txtclip])
    return cvc.set_duration(clip.duration)


def text_to_caption(
    url: str, segments: list, text_color: str, fontsize: int, font: str, language: str, fade_duration: float
):
    video = VideoFileClip(url)

    width = video.w
    fontsize_px = int(fontsize * _px_per_pt)
    max_text_length = width // fontsize_px * _lang_scale.get(language, 2)

    for seg in segments:
        if len(seg["text"]) // _lang_scale.get(language, 2) * fontsize_px > width:
            seg["text"] = insert_newlines(seg["text"], max_text_length, language, int(max_text_length * 0.1))

    annotated_clips = [
        annotate(
            video.subclip(min(seg["start"], video.duration), min(seg["end"], video.duration)),
            text=seg["text"],
            text_color=text_color,
            fontsize=fontsize,
            font=font,
            fade_duration=fade_duration,
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
        fade_duration=args.fade_duration,
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
    parser.add_argument("--fade-duration", type=float, default=0.0)
    parser.add_argument("--save-text", action="store_true")
    parser.add_argument("--load-text", type=str, default=None)
    args = parser.parse_args()
    main(args)
