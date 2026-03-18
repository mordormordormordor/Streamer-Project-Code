from pathlib import Path

from transcript_summary import (
    speaker_summary_freqs_transcripts_txt,
    TRANSCRIPTS_NAMES,
    TRANSCRIPTS_A,
    TRANSCRIPTS_B,
    TRANSCRIPTS_C,
)
from transcript_1gram import create_1gram_txt
from transcript_wordfreq import (
    speaker_word_frequency_from_transcript,
    merge_word_frequency_txt_files,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"

# Output directories
SUMMARIES_DIR = DATA_DIR / "summaries"
GRAMS1_DIR = DATA_DIR / "one_grams"
WORDFREQ_DIR = DATA_DIR / "wordfreq"
MERGED_DIR = DATA_DIR / "merged"

for d in [
    SUMMARIES_DIR,
    GRAMS1_DIR,
    WORDFREQ_DIR,
    MERGED_DIR,
]:
    d.mkdir(parents=True, exist_ok=True)

# Speaker summaries
for ts in TRANSCRIPTS_NAMES:
    input_path = TRANSCRIPTS_DIR / ts
    output_path = SUMMARIES_DIR / f"{input_path.stem}__sum-freq-ts.txt"

    result = speaker_summary_freqs_transcripts_txt(
        txt_path=input_path,
        lowercase=False,
        out_txt_path=output_path,
    )
    print(f"summary: {result}")

# 1-gram files
for ts in TRANSCRIPTS_NAMES:
    input_path = TRANSCRIPTS_DIR / ts
    output_path = GRAMS1_DIR / f"{input_path.stem}__1gram.txt"

    result = create_1gram_txt(
        txt_path=input_path,
        lowercase=False,
        out_txt_path=output_path,
    )
    print(f"1gram: {result}")

# Speaker A word-frequency files
for ts in TRANSCRIPTS_A:
    input_path = TRANSCRIPTS_DIR / ts
    output_path = WORDFREQ_DIR / f"{input_path.stem}_wf.txt"

    out = speaker_word_frequency_from_transcript(
        transcript_path=input_path,
        speaker="Speaker A",
        lowercase=False,
        out_txt_path=output_path,
    )
    print(f"speaker A wf: {out}")

# Speaker B word-frequency files
for ts in TRANSCRIPTS_B:
    input_path = TRANSCRIPTS_DIR / ts
    output_path = WORDFREQ_DIR / f"{input_path.stem}_wf.txt"

    out = speaker_word_frequency_from_transcript(
        transcript_path=input_path,
        speaker="Speaker B",
        lowercase=False,
        out_txt_path=output_path,
    )
    print(f"speaker B wf: {out}")

# Speaker C word-frequency files
for ts in TRANSCRIPTS_C:
    input_path = TRANSCRIPTS_DIR / ts
    output_path = WORDFREQ_DIR / f"{input_path.stem}_wf.txt"

    out = speaker_word_frequency_from_transcript(
        transcript_path=input_path,
        speaker="Speaker C",
        lowercase=False,
        out_txt_path=output_path,
    )
    print(f"speaker C wf: {out}")


merged_inputs = [
    WORDFREQ_DIR / f"{Path(ts).stem}_wf.txt"
    for ts in TRANSCRIPTS_NAMES
]

merged_path = merge_word_frequency_txt_files(
    merged_inputs,
    out_txt_path=MERGED_DIR / "merged_file.txt",
    strict=True,
)