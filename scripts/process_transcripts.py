from pathlib import Path

from transcript_summary import speaker_summary_freqs_transcripts_txt
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


transcript_names = [

    # "HasanAbi 11-12-2025 PART 2 transcript.txt" #Too much overlap
    "HasanAbi 11-24-2025 transcript.txt",
    "HasanAbi 11-25-2025 transcript.txt",
    # "HasanAbi 11-26-2025 PART 2 transcript.txt",
    # "HasanAbi 11-26-2025 PART 1 transcript.txt",
    # "HasanAbi 11-27-2025 transcript.txt",
    "HasanAbi 11-28-2025 transcript.txt",
    "HasanAbi 11-29-2025 transcript.txt",


    # "HasanAbi 11-30-2025 transcript.txt",
    "HasanAbi 12-1-2025 transcript.txt",
    "HasanAbi 12-2-2025 transcript.txt",
    "HasanAbi 12-3-2025 transcript.txt",
    "HasanAbi 12-4-2025 transcript.txt",
    "HasanAbi 12-6-2025 transcript.txt",

    "HasanAbi 12-8-2025 transcript.txt",
    "HasanAbi 12-9-2025 transcript.txt",
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
    "HasanAbi 1-1-2026 transcript.txt",
    "HasanAbi 1-2-2026 transcript.txt",

    # "HasanAbi 1-3-2026 transcript.txt",
    "HasanAbi 1-5-2026 transcript.txt",
    "HasanAbi 1-6-2026 transcript.txt",
    "HasanAbi 1-7-2026 transcript.txt",
    "HasanAbi 1-8-2026 transcript.txt",
    "HasanAbi 1-9-2026 transcript.txt",
    "HasanAbi 1-12-2026 transcript.txt",
    # "HasanAbi 1-13-2026 transcript.txt",
    # "HasanAbi 1-14-2026 transcript.txt",
    "HasanAbi 1-15-2026 transcript.txt",

    "HasanAbi 1-16-2026 transcript.txt",
    "HasanAbi 1-17-2026 transcript.txt",
    "HasanAbi 1-18-2026 transcript.txt",
    "HasanAbi 1-19-2026 transcript.txt",
    "HasanAbi 1-20-2026 transcript.txt",
    "HasanAbi 1-21-2026 transcript.txt",
    "HasanAbi 1-22-2026 transcript.txt",
    "HasanAbi 1-25-2026 transcript.txt",
    "HasanAbi 1-26-2026 transcript.txt",
    "HasanAbi 1-27-2026 transcript.txt",
]

transcriptsA = [
    "HasanAbi 11-24-2025 transcript.txt",
    "HasanAbi 11-28-2025 transcript.txt",

    "HasanAbi 12-2-2025 transcript.txt",
    "HasanAbi 12-6-2025 transcript.txt",

    "HasanAbi 12-8-2025 transcript.txt",
    "HasanAbi 12-9-2025 transcript.txt",
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

    "HasanAbi 1-1-2026 transcript.txt",
    "HasanAbi 1-6-2026 transcript.txt",
    "HasanAbi 1-8-2026 transcript.txt",
    "HasanAbi 1-16-2026 transcript.txt",
    "HasanAbi 1-17-2026 transcript.txt",
    "HasanAbi 1-19-2026 transcript.txt",
    "HasanAbi 1-22-2026 transcript.txt",
    "HasanAbi 1-25-2026 transcript.txt"
]

transcriptsB = [
    "HasanAbi 11-25-2025 transcript.txt",
    "HasanAbi 11-29-2025 transcript.txt",

    "HasanAbi 12-3-2025 transcript.txt",

    "HasanAbi 12-13-2025 transcript.txt",
    "HasanAbi 12-16-2025 transcript.txt",
    "HasanAbi 12-18-2025 transcript.txt",
    "HasanAbi 12-22-2025 transcript.txt",

    "HasanAbi 1-2-2026 transcript.txt",
    "HasanAbi 1-5-2026 transcript.txt",
    "HasanAbi 1-7-2026 transcript.txt",
    "HasanAbi 1-12-2026 transcript.txt",
    "HasanAbi 1-18-2026 transcript.txt",
    "HasanAbi 1-20-2026 transcript.txt",
    "HasanAbi 1-21-2026 transcript.txt",
    "HasanAbi 1-26-2026 transcript.txt",
    "HasanAbi 1-27-2026 transcript.txt",
]

transcriptsC = [
    "HasanAbi 12-1-2025 transcript.txt",
    "HasanAbi 12-4-2025 transcript.txt",

    "HasanAbi 12-10-2025 transcript.txt",
    "HasanAbi 1-9-2026 transcript.txt",
    "HasanAbi 1-15-2026 transcript.txt",
]


merged_inputs = [
    # "HasanAbi 11-12-2025 PART 2 transcript.txt_wf" #Too much overlap
    "HasanAbi 11-24-2025 transcript_wf.txt",
    "HasanAbi 11-25-2025 transcript_wf.txt",
    # "HasanAbi 11-26-2025 PART 2 transcript_wf.txt",
    # "HasanAbi 11-26-2025 PART 1 transcript_wf.txt",
    # "HasanAbi 11-27-2025 transcript_wf.txt",
    "HasanAbi 11-28-2025 transcript_wf.txt",
    "HasanAbi 11-29-2025 transcript_wf.txt",

    # "HasanAbi 11-30-2025 transcript_wf.txt",
    "HasanAbi 12-1-2025 transcript_wf.txt",
    "HasanAbi 12-2-2025 transcript_wf.txt",
    "HasanAbi 12-3-2025 transcript_wf.txt",
    "HasanAbi 12-4-2025 transcript_wf.txt",
    "HasanAbi 12-6-2025 transcript_wf.txt",

    "HasanAbi 12-8-2025 transcript_wf.txt",
    "HasanAbi 12-9-2025 transcript_wf.txt",
    "HasanAbi 12-10-2025 transcript_wf.txt",
    "HasanAbi 12-11-2025 transcript_wf.txt",
    "HasanAbi 12-12-2025 transcript_wf.txt",

    "HasanAbi 12-13-2025 transcript_wf.txt",
    "HasanAbi 12-14-2025 transcript_wf.txt",
    # "HasanAbi 12-15-2025 transcript_wf.txt",
    "HasanAbi 12-16-2025 transcript_wf.txt",
    # "HasanAbi 12-17-2025 transcript_wf.txt",
    "HasanAbi 12-18-2025 transcript_wf.txt",
    "HasanAbi 12-19-2025 transcript_wf.txt",
    # "HasanAbi 12-20-2025 transcript_wf.txt",
    "HasanAbi 12-22-2025 transcript_wf.txt",
    # "HasanAbi 12-23-2025 transcript_wf.txt",
    # "HasanAbi 12-24-2025 transcript_wf.txt",

    "HasanAbi 12-25-2025 transcript_wf.txt",
    "HasanAbi 12-26-2025 transcript_wf.txt",
    "HasanAbi 12-27-2025 transcript_wf.txt",
    "HasanAbi 12-28-2025 transcript_wf.txt",
    "HasanAbi 12-29-2025 transcript_wf.txt",
    # "HasanAbi 12-30-2025 transcript_wf.txt",
    "HasanAbi 12-31-2025 transcript_wf.txt",
    "HasanAbi 1-1-2026 transcript_wf.txt",
    "HasanAbi 1-2-2026 transcript_wf.txt",

    # "HasanAbi 1-3-2026 transcript_wf.txt",
    "HasanAbi 1-5-2026 transcript_wf.txt",
    "HasanAbi 1-6-2026 transcript_wf.txt",
    "HasanAbi 1-7-2026 transcript_wf.txt",
    "HasanAbi 1-8-2026 transcript_wf.txt",
    "HasanAbi 1-9-2026 transcript_wf.txt",
    "HasanAbi 1-12-2026 transcript_wf.txt",
    # "HasanAbi 1-13-2026 transcript_wf.txt",
    # "HasanAbi 1-14-2026 transcript_wf.txt",
    "HasanAbi 1-15-2026 transcript_wf.txt",

    "HasanAbi 1-16-2026 transcript_wf.txt",
    "HasanAbi 1-17-2026 transcript_wf.txt",
    "HasanAbi 1-18-2026 transcript_wf.txt",
    "HasanAbi 1-19-2026 transcript_wf.txt",
    "HasanAbi 1-20-2026 transcript_wf.txt",
    "HasanAbi 1-21-2026 transcript_wf.txt",
    "HasanAbi 1-22-2026 transcript_wf.txt",
    "HasanAbi 1-25-2026 transcript_wf.txt",
    "HasanAbi 1-26-2026 transcript_wf.txt",
    "HasanAbi 1-27-2026 transcript_wf.txt",
]

# Speaker summaries
for ts in transcript_names:
    input_path = TRANSCRIPTS_DIR / ts
    output_path = SUMMARIES_DIR / f"{input_path.stem}__sum-freq-ts.txt"

    result = speaker_summary_freqs_transcripts_txt(
        txt_path=input_path,
        lowercase=False,
        out_txt_path=output_path,
    )
    print(f"summary: {result}")

# 1-gram files
for ts in transcript_names:
    input_path = TRANSCRIPTS_DIR / ts
    output_path = GRAMS1_DIR / f"{input_path.stem}__1gram.txt"

    result = create_1gram_txt(
        txt_path=input_path,
        lowercase=False,
        out_txt_path=output_path,
    )
    print(f"1gram: {result}")

# Speaker A word-frequency files
for ts in transcriptsA:
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
for ts in transcriptsB:
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
for ts in transcriptsC:
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
    for ts in transcriptsA
]

merged_path = merge_word_frequency_txt_files(
    merged_inputs,
    out_txt_path=MERGED_DIR / "merged_file.txt",
    strict=True,
)