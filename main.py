from pathlib import Path
import sys
print(sys.executable)

from scripts.lexical_metrics import (
    jensen_shannon_distance_from_files,
)

from scripts.transcript_wordfreq import (
    merge_word_frequency_txt_files,
)

from scripts.transcript_summary import (
    TRANSCRIPTS_NAMES,
    TRANSCRIPTS_A,
    TRANSCRIPTS_B,
    TRANSCRIPTS_C,
)

PROJECT_ROOT = Path(__file__).resolve().parents[0]
DATA_DIR = PROJECT_ROOT / "data"
WORDFREQ_DIR = DATA_DIR / "wordfreq"
MERGED_DIR = DATA_DIR / "merged"

merged_inputs = [
    WORDFREQ_DIR / f"{Path(ts).stem}_wf.txt"
    for ts in TRANSCRIPTS_NAMES
]

merge_file = MERGED_DIR / "merged_file.txt"
subtlex_file = DATA_DIR / "ref_corpora" / "subtlex_us_wf.txt"
opensub_file = DATA_DIR / "ref_corpora" / "opensubtitles2018_wf.txt"

jsd_subtlex = jensen_shannon_distance_from_files(merge_file, subtlex_file)
print("JSD: Merged vs SUBTLEX:", jsd_subtlex)

jsd_opensub = jensen_shannon_distance_from_files(merge_file, opensub_file)
print("JSD: Merged vs OpenSubtitles:", jsd_opensub)

# Merge all the word frequency .txt files into separate merged files, each excluding one of the original files
# This way we can compare each individual transcript's word frequency distribution to the merged distribution 
# of all the other transcripts, to see how similar each one is to the overall "average" distribution.
count=0
for i, wf_path in enumerate(merged_inputs):
    # Create a list of all files except the current one
    other_files = merged_inputs[:i] + merged_inputs[i+1:]
    
    # Extract the name part for the output file
    file_id = wf_path.stem[9:19] 
    
    # Merged files names include the file_id of the excluded file for clarity 
    # (e.g. "merged_file_11-24-2025.txt" excludes "HasanAbi 11-24-2025 transcript.txt")
    merged_path = merge_word_frequency_txt_files(
        other_files,
        out_txt_path=MERGED_DIR / f"merged_file_{file_id}.txt",
        strict=True,
    )

    jsd_subtlex = jensen_shannon_distance_from_files(merged_path, wf_path)
    print(f"JSD: Merged-1 vs {file_id}:    {round(jsd_subtlex, 4)}\n")
    count += 1
print(f"Total comparisons: {count}")