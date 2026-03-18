from __future__ import annotations

import os
import re
import tempfile
from collections import Counter
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

SPEAKER_PREFIX = re.compile(r"^\s*(Speaker\s+[^:]+)\s*:\s*(.*)\s*$")

# WORD: letters/digits, allows for internal apostrophes/hyphens
# PUNCT/SYMBOL: any single non-whitespace char that is not part of a word token (e.g. .,!? etc.)
TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*|[^\w\s]", re.UNICODE)


# This script reads a speaker-formatted transcript and produces a .txt output containing:
#   1) SUMMARY of token counts per speaker
#   2) WORD FREQUENCIES per speaker
#   3) TRANSCRIPTS per speaker
def speaker_summary_freqs_transcripts_txt(
    txt_path: Union[str, Path],
    *,
    lowercase: bool = False,
    out_txt_path: Optional[Union[str, Path]] = None,
    top_n: Optional[int] = None,
) -> Path:
    path = Path(txt_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    out_path = (
        Path(out_txt_path)
        if out_txt_path is not None
        else path.with_name(f"{path.stem}__sum-freq-ts.txt")
    )

    counts_by_speaker: Dict[str, Counter] = {}
    blocks_by_speaker: Dict[str, int] = {}
    speaker_order: list[str] = []

    # speaker -> (temp file path, open temp file handle)
    tmp_by_speaker: Dict[str, Tuple[str, object]] = {}

    def get_tmp_writer(speaker: str):
        if speaker in tmp_by_speaker:
            return tmp_by_speaker[speaker][1]

        tf = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            prefix="speaker_",
            suffix=".txt",
        )
        tmp_by_speaker[speaker] = (tf.name, tf)
        return tf

    # Helper to clean text based on options (e.g. lowercase)
    def clean_text(text: str) -> str:
        return text.lower() if lowercase else text

    current_speaker: Optional[str] = None

    # Parse transcript, count tokens, collect cleaned transcript text per speaker
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")
            if not line.strip():
                continue

            m = SPEAKER_PREFIX.match(line)
            if m:
                current_speaker = m.group(1).strip()
                text = m.group(2).strip()

                if current_speaker not in counts_by_speaker:
                    counts_by_speaker[current_speaker] = Counter()
                    blocks_by_speaker[current_speaker] = 0
                    speaker_order.append(current_speaker)

                blocks_by_speaker[current_speaker] += 1
            else:
                if current_speaker is None:
                    continue
                text = line.strip()

            cleaned = clean_text(text)

            cleaned_for_transcript = cleaned.strip()
            if cleaned_for_transcript:
                writer = get_tmp_writer(current_speaker)
                writer.write(cleaned_for_transcript + "\n")

            tokens = TOKEN_RE.findall(cleaned)
            counts_by_speaker[current_speaker].update(tokens)

    # Close temp writers
    for _, tf in tmp_by_speaker.values():
        tf.close()

    total_tokens_all = sum(sum(counter.values()) for counter in counts_by_speaker.values())

    # Write summary, frequencies, and transcripts to output file
    with out_path.open("w", encoding="utf-8") as out:
        out.write(f"=== SUMMARY: {txt_path} ===\n")
        out.write("speaker\tunique_tokens\ttotal_tokens\tpercent_tokens\tblocks\n")

        for speaker in speaker_order:
            counter = counts_by_speaker[speaker]
            total = sum(counter.values())
            unique = len(counter)
            pct = (100.0 * total / total_tokens_all) if total_tokens_all > 0 else 0.0
            blocks = blocks_by_speaker.get(speaker, 0)
            out.write(f"{speaker}\t{unique}\t{total}\t{pct:.2f}\t{blocks}\n")

        out.write("\nNotes:\n")
        out.write("- blocks = number of times that speaker appears as a SPEAKER_PREFIX header.\n")
        out.write("- percent_tokens is computed from tokenized text across all speakers.\n")
        if lowercase:
                out.write(f"- lowercase={'ON'}.\n\n")
        else:
                out.write(f"- lowercase={'OFF'}.\n\n")

        for speaker in speaker_order:
            out.write(f"== {speaker} Word Frequency ==\n")
            items = counts_by_speaker[speaker].most_common()

            if top_n is not None:
                items = items[:top_n]

            for tok, n in items:
                out.write(f"{tok}\t{n}\n")
            out.write("\n")

        for speaker in speaker_order:
            out.write(f"== {speaker} Transcript ==\n")
            tmp_name = tmp_by_speaker.get(speaker, (None, None))[0]
            if tmp_name and os.path.exists(tmp_name):
                with open(tmp_name, "r", encoding="utf-8", errors="replace") as tin:
                    for tline in tin:
                        out.write(tline)
            out.write("\n")

    # Clean up temp files
    for tmp_name, _ in tmp_by_speaker.values():
        try:
            os.remove(tmp_name)
        except OSError:
            pass

    return out_path


TRANSCRIPTS_NAMES = [

    # "HasanAbi 11-12-2025 PART 2 transcript.txt" #Too much overlap
    "HasanAbi 11-24-2025 transcript.txt",
    "HasanAbi 11-25-2025 transcript.txt",
    # "HasanAbi 11-26-2025 PART 2 transcript.txt",
    # "HasanAbi 11-26-2025 PART 1 transcript.txt",
    # "HasanAbi 11-27-2025 transcript.txt",
    "HasanAbi 11-28-2025 transcript.txt",
    "HasanAbi 11-29-2025 transcript.txt",

    # "HasanAbi 11-30-2025 transcript.txt",
    "HasanAbi 12-01-2025 transcript.txt",
    "HasanAbi 12-02-2025 transcript.txt",
    "HasanAbi 12-03-2025 transcript.txt",
    "HasanAbi 12-04-2025 transcript.txt",
    "HasanAbi 12-06-2025 transcript.txt",

    "HasanAbi 12-08-2025 transcript.txt",
    "HasanAbi 12-09-2025 transcript.txt",
    "HasanAbi 12-10-2025 transcript.txt",
    "HasanAbi 12-11-2025 transcript.txt",
    "HasanAbi 12-12-2025 transcript.txt",

    "HasanAbi 12-13-2025 transcript.txt",
    "HasanAbi 12-14-2025 transcript.txt",
    # "HasanAbi 12-15-2025 transcript.txt",
    "HasanAbi 12-16-2025 transcript.txt",
    # "HasanAbi 12-17-2025 transcript.txt",
    "HasanAbi 12-18-2025 transcript.txt",
    "HasanAbi 12-19-2025 transcript.txt",
    # "HasanAbi 12-20-2025 transcript.txt",
    "HasanAbi 12-22-2025 transcript.txt",
    # "HasanAbi 12-23-2025 transcript.txt",
    # "HasanAbi 12-24-2025 transcript.txt",

    "HasanAbi 12-25-2025 transcript.txt",
    "HasanAbi 12-26-2025 transcript.txt",
    "HasanAbi 12-27-2025 transcript.txt",
    "HasanAbi 12-28-2025 transcript.txt",
    "HasanAbi 12-29-2025 transcript.txt",
    # "HasanAbi 12-30-2025 transcript.txt",
    "HasanAbi 12-31-2025 transcript.txt",
    "HasanAbi 01-01-2026 transcript.txt",
    "HasanAbi 01-02-2026 transcript.txt",

    # "HasanAbi 01-03-2026 transcript.txt",
    "HasanAbi 01-05-2026 transcript.txt",
    "HasanAbi 01-06-2026 transcript.txt",
    "HasanAbi 01-07-2026 transcript.txt",
    "HasanAbi 01-08-2026 transcript.txt",
    "HasanAbi 01-09-2026 transcript.txt",
    "HasanAbi 01-12-2026 transcript.txt",
    # "HasanAbi 01-13-2026 transcript.txt",
    # "HasanAbi 01-14-2026 transcript.txt",
    "HasanAbi 01-15-2026 transcript.txt",

    "HasanAbi 01-16-2026 transcript.txt",
    "HasanAbi 01-17-2026 transcript.txt",
    "HasanAbi 01-18-2026 transcript.txt",
    "HasanAbi 01-19-2026 transcript.txt",
    "HasanAbi 01-20-2026 transcript.txt",
    "HasanAbi 01-21-2026 transcript.txt",
    "HasanAbi 01-22-2026 transcript.txt",
    "HasanAbi 01-25-2026 transcript.txt",
    "HasanAbi 01-26-2026 transcript.txt",
    "HasanAbi 01-27-2026 transcript.txt",
]

TRANSCRIPTS_A = [
    "HasanAbi 11-24-2025 transcript.txt",
    "HasanAbi 11-28-2025 transcript.txt",

    "HasanAbi 12-02-2025 transcript.txt",
    "HasanAbi 12-06-2025 transcript.txt",

    "HasanAbi 12-08-2025 transcript.txt",
    "HasanAbi 12-09-2025 transcript.txt",
    "HasanAbi 12-11-2025 transcript.txt",
    "HasanAbi 12-12-2025 transcript.txt",
    "HasanAbi 12-14-2025 transcript.txt",
    "HasanAbi 12-19-2025 transcript.txt",

    "HasanAbi 12-25-2025 transcript.txt",
    "HasanAbi 12-26-2025 transcript.txt",
    "HasanAbi 12-27-2025 transcript.txt",
    "HasanAbi 12-28-2025 transcript.txt",
    "HasanAbi 12-29-2025 transcript.txt",
    "HasanAbi 12-31-2025 transcript.txt",

    "HasanAbi 01-01-2026 transcript.txt",
    "HasanAbi 01-06-2026 transcript.txt",
    "HasanAbi 01-08-2026 transcript.txt",
    "HasanAbi 01-16-2026 transcript.txt",
    "HasanAbi 01-17-2026 transcript.txt",
    "HasanAbi 01-19-2026 transcript.txt",
    "HasanAbi 01-22-2026 transcript.txt",
    "HasanAbi 01-25-2026 transcript.txt"
]


TRANSCRIPTS_B = [
    "HasanAbi 11-25-2025 transcript.txt",
    "HasanAbi 11-29-2025 transcript.txt",

    "HasanAbi 12-03-2025 transcript.txt",

    "HasanAbi 12-13-2025 transcript.txt",
    "HasanAbi 12-16-2025 transcript.txt",
    "HasanAbi 12-18-2025 transcript.txt",
    "HasanAbi 12-22-2025 transcript.txt",

    "HasanAbi 01-02-2026 transcript.txt",
    "HasanAbi 01-05-2026 transcript.txt",
    "HasanAbi 01-07-2026 transcript.txt",
    "HasanAbi 01-12-2026 transcript.txt",
    "HasanAbi 01-18-2026 transcript.txt",
    "HasanAbi 01-20-2026 transcript.txt",
    "HasanAbi 01-21-2026 transcript.txt",
    "HasanAbi 01-26-2026 transcript.txt",
    "HasanAbi 01-27-2026 transcript.txt",
]

TRANSCRIPTS_C = [
    "HasanAbi 12-01-2025 transcript.txt",
    "HasanAbi 12-04-2025 transcript.txt",

    "HasanAbi 12-10-2025 transcript.txt",
    "HasanAbi 01-09-2026 transcript.txt",
    "HasanAbi 01-15-2026 transcript.txt",
]