from pathlib import Path
import sys
print(sys.executable)

from scripts.lexical_metrics import (
    jensen_shannon_distance_from_files,
)

from scripts.transcript_wordfreq import (
    merge_word_frequency_txt_files,
)

PROJECT_ROOT = Path(__file__).resolve().parents[0]
DATA_DIR = PROJECT_ROOT / "data"

# Output directories
WORDFREQ_DIR = DATA_DIR / "wordfreq"
MERGED_DIR = DATA_DIR / "merged"

for d in [
    WORDFREQ_DIR,
    MERGED_DIR,
]:
    d.mkdir(parents=True, exist_ok=True)

merge_file = "/Users/sanji/Desktop/Visual Studio/Streamer Project Code/data/merged/merged_file.txt"
subtlex_file = "/Users/sanji/Desktop/Visual Studio/Streamer Project Code/data/ref_corpora/subtlex_us_wf.txt"
opensub_file = "/Users/sanji/Desktop/Visual Studio/Streamer Project Code/data/ref_corpora/opensubtitles2018_wf.txt"

jsd_subtlex = jensen_shannon_distance_from_files(merge_file, subtlex_file)
print("JSD: Merged vs SUBTLEX:", jsd_subtlex)

jsd_opensub = jensen_shannon_distance_from_files(merge_file, opensub_file)
print("JSD: Merged vs OpenSubtitles:", jsd_opensub)

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

merged_inputs = [
    WORDFREQ_DIR / f"{Path(ts).stem}_wf.txt"
    for ts in transcript_names
]

# Merge all the word frequency .txt files into separate merged files, each excluding one of the original files
# This way we can compare each individual transcript's word frequency distribution to the merged distribution 
# of all the other transcripts, to see how similar each one is to the overall "average" distribution.
for i, wf_path in enumerate(merged_inputs):
    # Create a list of all files except the current one
    other_files = merged_inputs[:i] + merged_inputs[i+1:]
    
    # Extract the name part for the output file
    file_id = wf_path.stem[9:19] 
    
    merged_path = merge_word_frequency_txt_files(
        other_files,
        out_txt_path=MERGED_DIR / f"merged_file_{file_id}.txt",
        strict=True,
    )

    jsd_subtlex = jensen_shannon_distance_from_files(merged_path, wf_path)
    print(f"JSD: Merged-1 vs {file_id}:    {round(jsd_subtlex, 4)}\n")

