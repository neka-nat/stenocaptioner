import re


def split_en_sentences(text: str) -> list[str]:
    sentences = []
    for sentence in re.split(r"(?<=[,.?!])", text):
        sentence = sentence.strip()
        if sentence:
            sentences.append(sentence)
    return sentences


def split_ja_sentences(text: str) -> list[str]:
    sentences = []
    for sentence in re.split(r"(?<=[、。？！?!])", text):
        sentence = sentence.strip()
        if sentence:
            sentences.append(sentence)
    return sentences


def tweak_en_lines(lines: list[str]) -> list[str]:
    new_lines = []
    for line in lines:
        if new_lines and line in [",", ".", "?", "!"]:
            new_lines[-1] += line
        else:
            new_lines.append(line)
    return new_lines


def tweak_ja_lines(lines: list[str]) -> list[str]:
    new_lines = []
    for line in lines:
        if new_lines and line in ["、", "。", "？", "！", "?", "!"]:
            new_lines[-1] += line
        else:
            new_lines.append(line)
    return new_lines


def insert_newlines(text: str, max_length: int, language: str) -> str:
    if language == "ja":
        sentences = split_ja_sentences(text)
    else:
        sentences = split_en_sentences(text)

    lines = []
    for sentence in sentences:
        if lines and len(lines[-1]) + len(sentence) < max_length:
            lines[-1] += sentence
        elif len(sentence) > max_length:
            lines.extend([sentence[x : x + max_length] for x in range(0, len(sentence), max_length)])
        else:
            lines.append(sentence)

    if language == "ja":
        lines = tweak_ja_lines(lines)
    else:
        lines = tweak_en_lines(lines)
    return "\n".join(lines)
