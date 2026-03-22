from pathlib import Path
import pandas as pd
import sys
print(sys.executable)

from scripts.lexical_metrics import (
    jensen_shannon_distance,
    jensen_shannon_distance_from_files,
    log_odds_with_prior_from_files,
    load_counts_from_wf_txt,
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


wordfreq_file_paths = [
    WORDFREQ_DIR / f"{Path(ts).stem}_wf.txt"
    for ts in TRANSCRIPTS_NAMES
]

merge_wordfreq_file_paths = [
    MERGED_DIR / f"merged_file_{ts[9:19]}.txt"
    for ts in TRANSCRIPTS_NAMES
]

merge_file = MERGED_DIR / "merged_file.txt"
subtlex_file = DATA_DIR / "ref_corpora" / "subtlex_us_wf.txt"
opensub_file = DATA_DIR / "ref_corpora" / "opensubtitles2018_wf.txt"

# --- Merge Word Frequency Files ---

run_merge_file_creation = False # Set to True to create the merged files
run_jsd_calculation = True # Set to True to run the JSD calculations
print_jsd_values = False # Set to True to print the JSD values

# Merge all the word frequency .txt files into separate merged files, each excluding one of the original files
# This way we can compare each individual transcript's word frequency distribution to the merged distribution 
# of all the other transcripts, to see how similar each one is to the overall "average" distribution.
if run_merge_file_creation:
    count = 0

    for i, wf_path in enumerate(wordfreq_file_paths):
        # Create a list of all files except the current one
        other_files = wordfreq_file_paths[:i] + wordfreq_file_paths[i + 1:]

        file_id = wf_path.stem[9:19]

        # Merged files names include the file_id of the excluded file for clarity 
        # (e.g. "merged_file_11-24-2025.txt" excludes "HasanAbi 11-24-2025 transcript.txt")
        merge_word_frequency_txt_files(
            other_files,
            out_txt_path=MERGED_DIR / f"merged_file_{file_id}.txt",
            strict=True,
        )
    print(f"Created {count} leave-one-out merged files.")
else:
    print("Skipping merge file creation.")


# ------- Jansen-Shannon Distance -------

subtlex_counts = load_counts_from_wf_txt(subtlex_file)
opensub_counts = load_counts_from_wf_txt(opensub_file)
merge_file_counts = load_counts_from_wf_txt(merge_file)
jsd_rows = []
subtlex_rows = []
opensub_rows = []
count=0
if run_jsd_calculation:
    print("Calculating JSD values for each transcript against Merged-1, SUBTLEX, and OpenSubtitles...")
    for wf_path in wordfreq_file_paths:
        file_id = wf_path.stem[9:19]
        merged_path = MERGED_DIR / f"merged_file_{file_id}.txt"

        wf_counts = load_counts_from_wf_txt(wf_path)
        merged_counts = load_counts_from_wf_txt(merged_path)

        comparison_targets = [
            ("Merged-1", merged_counts, jsd_rows),
            (subtlex_file.stem, subtlex_counts, subtlex_rows),
            (opensub_file.stem, opensub_counts, opensub_rows),
        ]
        for ref_name, ref_counts, row_list in comparison_targets:
            (
                jsd_val,
                unique_words,
                shared_words,
                pct_shared_words,
                unique_to_a,
                unique_to_b,
                pct_shared_of_a,
                pct_shared_of_b,
                n_a,
                n_b,
            ) = jensen_shannon_distance(wf_counts, ref_counts)

            row = {
                "ref_file": ref_name,
                "transcript": wf_path.stem,
                "jsd_val": round(jsd_val, 4),
                "shared_words": shared_words,
                "pct_shared_words": round(pct_shared_words, 3),
                "unique_to_transcript": unique_to_a,
                "pct_shared_of_transcript": round(pct_shared_of_a, 3),
                "total_tokens_transcript": n_a,
            }

            if ref_name == "Merged-1":
                row.update({
                    "unique_to_merged": unique_to_b,
                    "pct_shared_of_merged": round(pct_shared_of_b, 3),
                    "total_tokens_merged": n_b,
                })
            elif ref_name == subtlex_file.stem:
                row.update({
                    "unique_to_subtlex": unique_to_b,
                    "pct_shared_of_subtlex": round(pct_shared_of_b, 3),
                    "total_tokens_subtlex": n_b,
                })
            elif ref_name == opensub_file.stem:
                row.update({
                    "unique_to_opensub": unique_to_b,
                    "pct_shared_of_opensub": round(pct_shared_of_b, 3),
                    "total_tokens_opensub": n_b,
                })

            row_list.append(row)
            count += 1
else:
    print("Skipping JSD calculations.")

jsd_df = pd.DataFrame(jsd_rows)
jsd_df = jsd_df.sort_values("jsd_val", ascending=False).reset_index(drop=True)
jsd_df.to_html("jsd_merged.html", index=False)
jsd_df.to_html("jsd_merged.html", index=False)

subtlex_df = pd.DataFrame(subtlex_rows)
subtlex_df = subtlex_df.sort_values("jsd_val", ascending=False).reset_index(drop=True)
subtlex_df.to_html("jsd_subtlex.html", index=False)
subtlex_df.to_html("jsd_subtlex.html", index=False)

opensub_df = pd.DataFrame(opensub_rows)
opensub_df = opensub_df.sort_values("jsd_val", ascending=False).reset_index(drop=True)
opensub_df.to_html("jsd_opensub.html", index=False)
opensub_df.to_html("jsd_opensub.html", index=False)


print("Saved:")
jsd_df.to_csv(DATA_DIR / "results" / "jsd_merged.csv", index=False)
subtlex_df.to_csv(DATA_DIR / "results" / "jsd_subtlex.csv", index=False)
opensub_df.to_csv(DATA_DIR / "results" / "jsd_opensub.csv", index=False)
print(DATA_DIR / "results" / "jsd_merged.csv")
print(DATA_DIR / "results" / "jsd_subtlex.csv")
print(DATA_DIR / "results" / "jsd_opensub.csv")

jsd_df.to_html(DATA_DIR / "results" / "jsd_merged.html", index=False)
subtlex_df.to_html(DATA_DIR / "results" / "jsd_subtlex.html", index=False)
opensub_df.to_html(DATA_DIR / "results" / "jsd_opensub.html", index=False)
print(DATA_DIR / "results" / "jsd_merged.html")
print(DATA_DIR / "results" / "jsd_subtlex.html")
print(DATA_DIR / "results" / "jsd_opensub.html")



if print_jsd_values:
    jsd_val, unique_words, shared_words, pct_shared_words, unique_to_a, unique_to_b, pct_shared_of_a, pct_shared_of_b, n_a, n_b = jensen_shannon_distance(merge_file_counts, subtlex_counts)
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

    jsd_val, unique_words, shared_words, pct_shared_words, unique_to_a, unique_to_b, pct_shared_of_a, pct_shared_of_b, n_a, n_b = jensen_shannon_distance(merge_file_counts, opensub_counts)
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

    print(f"\nJSD: Merged-1 vs each individual, transcript, unique/shared vocab stats: {jsd_df['unique_to_merged'].iloc[0]}, Total comparisons: {count}:")
    print(jsd_df.head(count))
    print(f"\nJSD: SUBTLEX vs each individual transcript, unique/shared vocab stats: {subtlex_df['unique_to_subtlex'].iloc[0]}, Total comparisons: {count}:")
    print(subtlex_df.head(count))
    print(f"\nJSD: OpenSubtitles vs each individual transcript, unique/shared vocab stats: {opensub_df['unique_to_opensub'].iloc[0]}, Total comparisons: {count}:")
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
