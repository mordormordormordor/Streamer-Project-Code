from pathlib import Path
import pandas as pd
import sys
print(sys.executable)

from scripts.lexical_metrics import (
    jensen_shannon_distance_from_files,
    log_odds_with_prior_from_files,
)

from scripts.transcript_wordfreq import (
    merge_word_frequency_txt_files,
)

from scripts.transcript_summary import (
    TRANSCRIPTS_NAMES,
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

# ------- Jansen-Shannon Distance -------
jsd_subtlex = jensen_shannon_distance_from_files(merge_file, subtlex_file)

jsd_val, unique_words, shared_words, pct_shared_words, unique_to_a, unique_to_b, pct_shared_of_a, pct_shared_of_b, n_a, n_b = jensen_shannon_distance_from_files(merge_file, subtlex_file)
print("\nMerged vs SUBTLEX:")
print("JSD:", round(jsd_val, 4))
print("Union vocab size:", unique_words)
print("Percent shared (union):", round(pct_shared_words, 3))
print("Unique to Merged:", unique_to_a)
print("Unique to SUBTLEX:", unique_to_b)
print("Percent of Merged vocab shared:", round(pct_shared_of_a, 3))
print("Percent of SUBTLEX vocab shared:", round(pct_shared_of_b, 3))
print("Total tokens A:", n_a)
print("Total tokens B:", n_b)

jsd_val, unique_words, shared_words, pct_shared_words, unique_to_a, unique_to_b, pct_shared_of_a, pct_shared_of_b, n_a, n_b = jensen_shannon_distance_from_files(merge_file, opensub_file)
print("\nMerged vs OpenSubtitles:")
print("JSD:", round(jsd_val, 4))
print("Union vocab size:", unique_words)
print("Percent shared (union):", round(pct_shared_words, 3))
print("Unique to Merged:", unique_to_a)
print("Unique to OpenSubtitles:", unique_to_b)
print("Percent of Merged vocab shared:", round(pct_shared_of_a, 3))
print("Percent of OpenSubtitles vocab shared:", round(pct_shared_of_b, 3))
print("Total tokens A:", n_a)
print("Total tokens B:", n_b, "\n")

# Merge all the word frequency .txt files into separate merged files, each excluding one of the original files
# This way we can compare each individual transcript's word frequency distribution to the merged distribution 
# of all the other transcripts, to see how similar each one is to the overall "average" distribution.
count=0
jsd_rows = []
subtlex_rows = []
opensub_rows = []
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

    list_of_ref_files = [(merged_path, jsd_rows), (subtlex_file, subtlex_rows), (opensub_file, opensub_rows)]
    for ref_file, row_list in list_of_ref_files:
        jsd_val, unique_words, shared_words, pct_shared_words, unique_to_a, unique_to_b, pct_shared_of_a, pct_shared_of_b, n_a, n_b = jensen_shannon_distance_from_files(ref_file, wf_path)
        row_list.append({
            "comparison": f"Merged-1 vs {file_id}" if ref_file == merged_path else f"{ref_file.stem} vs {file_id}",
            "jsd_val": round(jsd_val, 4),
            "shared_words": shared_words,
            "pct_shared_words": round(pct_shared_words, 3),
            "unique_to_merged": unique_to_a,
            "unique_to_transcript": unique_to_b,
            "pct_shared_of_merged": round(pct_shared_of_a, 3),
            "pct_shared_of_transcript": round(pct_shared_of_b, 3),
            "n_merged": n_a,
            "n_transcript": n_b,
        })
    count += 1

jsd_df = pd.DataFrame(jsd_rows)
jsd_df = jsd_df.sort_values("jsd_val", ascending=False).reset_index(drop=True)

sublex_df = pd.DataFrame(subtlex_rows)
sublex_df = sublex_df.sort_values("jsd_val", ascending=False).reset_index(drop=True)

opensub_df = pd.DataFrame(opensub_rows)
opensub_df = opensub_df.sort_values("jsd_val", ascending=False).reset_index(drop=True)

print(f"\nJSD: Merged-1 vs each individual, transcript, unique/shared vocab stats: {jsd_df['unique_to_merged'].iloc[0]}, Total comparisons: {count}:")
print(jsd_df.head(count))
print(f"\nJSD: SUBTLEX vs each individual transcript, unique/shared vocab stats: {sublex_df['unique_to_merged'].iloc[0]}, Total comparisons: {count}:")
print(sublex_df.head(count))
print(f"\nJSD: OpenSubtitles vs each individual transcript, unique/shared vocab stats: {opensub_df['unique_to_merged'].iloc[0]}, Total comparisons: {count}:")
print(opensub_df.head(count))

# ------- Log-Odds Ratios with Prior -------
over_subtlex, under_subtlex = log_odds_with_prior_from_files(
    merge_file,
    subtlex_file,
    prior_file=subtlex_file, # define the prior as the reference corpus itself.
    top_n=30,
)

print("Overrepresented: Merged vs SUBTLEX")
print(over_subtlex.head(30))

print("\nUnderrepresented: Merged vs SUBTLEX")
print(under_subtlex.head(30))


print("\nLog-odds ratios with prior for the top 5 transcripts with the highest JSD values:")
top_5_list = [
    ["data/wordfreq/HasanAbi 12-03-2025 transcript_wf.txt","data/merged/merged_file_12-03-2025.txt"],
    ["data/wordfreq/HasanAbi 12-04-2025 transcript_wf.txt","data/merged/merged_file_12-04-2025.txt"],
    ["data/wordfreq/HasanAbi 12-02-2025 transcript_wf.txt","data/merged/merged_file_12-02-2025.txt"],
    ["data/wordfreq/HasanAbi 01-25-2026 transcript_wf.txt","data/merged/merged_file_01-25-2026.txt"],
    ["data/wordfreq/HasanAbi 12-06-2025 transcript_wf.txt","data/merged/merged_file_12-06-2025.txt"],
]

for wf_path, merged_path in top_5_list:
    # log-odds for the top 5 transcript with the highest JSD values
    over_subtlex, under_subtlex = log_odds_with_prior_from_files(
        wf_path,
        merged_path,
        prior_file=merged_path, # define the prior as the reference corpus itself.
        top_n=30,
    )
    print(f"\nOverrepresented: {wf_path[23:33]} vs Merged-1")
    print(over_subtlex.head(30))
