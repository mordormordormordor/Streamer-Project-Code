from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Iterable, Optional, Union


SPEAKER_PREFIX = re.compile(r"^\s*(Speaker\s+[^:]+)\s*:\s*(.*)\s*$")

# Tokenizer that keeps punctuation as separate tokens
TOKEN_KEEP_PUNCT = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?|[^\w\s]", re.UNICODE)

_WORD_FREQ_HEADER = re.compile(r"== Word Frequency ==")
_TOKEN_COUNT_LINE_RE = re.compile(r"^(.*?)\t(\d+)\s*$")

# Reads a speaker-formatted transcript and produces a .txt output containing word frequencies 
# for a specified speaker.
def speaker_word_frequency_from_transcript(
    transcript_path: Union[str, Path],
    speaker: str,
    *,
    lowercase: bool = False,
    out_txt_path: Optional[Union[str, Path]] = None,
) -> Path:
    p = Path(transcript_path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")

    target = speaker.strip()
    if not target:
        raise ValueError("speaker cannot be empty (e.g. 'Speaker A').")

    counts = Counter()
    current_speaker: str | None = None

    # Read through the transcript and count tokens for the target speaker
    with p.open("r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip():
                continue

            m = SPEAKER_PREFIX.match(line)
            if m:
                current_speaker = m.group(1).strip()
                text = m.group(2)
            else:
                if current_speaker is None:
                    continue
                text = line.strip()

            if current_speaker != target:
                continue

            if lowercase:
                text = text.lower()

            counts.update(TOKEN_KEEP_PUNCT.findall(text))

    if not counts:
        raise ValueError(f"No tokens found for speaker '{target}'. Check speaker name / file format.")

    out_path = (
        Path(out_txt_path)
        if out_txt_path is not None
        else p.with_name(f"{p.stem}_{target.replace(' ', '_')}_wf.txt")
    )

    # Write the word frequencies to the output file
    with out_path.open("w", encoding="utf-8") as out:
        out.write("sources:\n")
        out.write(f"{p.name}  {target}\n\n")
        out.write("== Word Frequency ==\n")
        for tok, n in counts.most_common():
            out.write(f"{tok}\t{n}\n")

    return out_path

# Reads a speaker-formatted transcript and produces a .txt output containing word frequencies 
# for all speakers, along with summary stats.
# Add later: keep speaker labels next to source transcript name in merged file
def merge_word_frequency_txt_files(
    freq_txt_paths: Iterable[Union[str, Path]],
    *,
    out_txt_path: Optional[Union[str, Path]] = None,
    strict: bool = True,
) -> Path:
    paths = [Path(p) for p in freq_txt_paths]
    if not paths:
        raise ValueError("freq_txt_paths is empty.")

    for p in paths:
        if not p.exists():
            raise FileNotFoundError(f"File not found: {p}")

    merged = Counter()
    sources_used: list[Path] = []

    # For each input file, look for the "== Word Frequency ==" section and parse token/count lines 
    # until the next blank line or end of file.
    for p in paths:
        in_freq_section = False
        saw_header = False

        with p.open("r", encoding="utf-8", errors="replace") as f:
            for raw in f:
                line = raw.rstrip("\n")

                if _WORD_FREQ_HEADER.match(line):
                    in_freq_section = True
                    saw_header = True
                    continue

                if not in_freq_section:
                    continue

                if not line.strip():
                    continue

                m = _TOKEN_COUNT_LINE_RE.match(line)
                if not m:
                    if strict:
                        raise ValueError(f"Malformed token/count line in {p}: {line!r}")
                    continue

                tok = m.group(1)
                n = int(m.group(2))
                if n > 0:
                    merged[tok] += n

        if strict and not saw_header:
            raise ValueError(f"No '== Word Frequency ==' section found in {p}")
        if saw_header:
            sources_used.append(p)

    if not merged:
        raise ValueError("Merged Counter is empty (no token/count lines were parsed).")

    out_path = (
        Path(out_txt_path)
        if out_txt_path is not None
        else paths[0].with_name("merged_file.txt")
    )

    # Write the merged word frequencies to the output file, along with the list of source files used.
    with out_path.open("w", encoding="utf-8") as out:
        out.write("sources:\n")
        for p in sources_used:
            out.write(f"{p.name}\n")
        out.write("\n")
        out.write("== Word Frequency ==\n")
        for tok, n in merged.most_common():
            out.write(f"{tok}\t{n}\n")
    print(f"Merged {len(paths)} files with {len(merged)} unique tokens. Output written to: {out_path}")
    return out_path