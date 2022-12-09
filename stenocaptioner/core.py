import os
import re

import whisper
import youtube_dl
from moviepy import editor
from moviepy.video.io.VideoFileClip import VideoFileClip


_px_per_pt = 1.33


def speech_to_text_segments(url: str, language: str, model_type: str, verbose: bool = True) -> list:
    model = whisper.load_model(model_type)
    result = model.transcribe(url, verbose=verbose, language=language)
    return result["segments"]


def annotate(clip, text, text_color, fontsize, font):
    txtclip = editor.TextClip(text, fontsize=fontsize, font=font, color=text_color)
    cvc = editor.CompositeVideoClip([clip, txtclip.set_pos(("center", "bottom"))])
    return cvc.set_duration(clip.duration)


def text_to_caption(url: str, segments: list, text_color: str, fontsize: int, font: str, language: str):
    video = VideoFileClip(url)

    width = video.w
    fontsize_px = int(fontsize * _px_per_pt)
    max_text_length = width // fontsize_px

    for seg in segments:
        if len(seg["text"]) * fontsize_px > width:
            split_str = [seg["text"][x : x + max_text_length] for x in range(0, len(seg["text"]), max_text_length)]
            seg["text"] = "\n".join(split_str)

    annotated_clips = [
        annotate(
            video.subclip(seg["start"], seg["end"]),
            text=seg["text"],
            text_color=text_color,
            fontsize=fontsize,
            font=font,
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
    segments = speech_to_text_segments(args.url, language=args.language, model_type=args.model_type)
    print("\n[stenocaptioner] Adding captions to video...")
    text_to_caption(
        args.url, segments, text_color=args.text_color, fontsize=args.fontsize, font=args.font, language=args.language
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
    args = parser.parse_args()
    main(args)
