from pathlib import Path
import pandas as pd
import sys

from typing import Dict, Union
import matplotlib.axis as maxis
import matplotlib.pyplot as plt
import collections
import collections.abc
import shifterator as sh

from scripts.lexical_metrics import (
    jensen_shannon_distance,
    jensen_shannon_distance_from_files,
    log_odds_with_prior_from_files,
    load_counts_from_wf_txt,
)

from scripts.transcript_wordfreq import (
    merge_word_frequency_txt_files,
    remove_punctuation_tokens,
)

from scripts.transcript_summary import (
    TRANSCRIPTS_NAMES,
)

from scripts.wordshift import (
    unique_counts_file_to_dict,
)

PROJECT_ROOT = Path(__file__).resolve().parents[0]
DATA_DIR = PROJECT_ROOT / "data"
WORDFREQ_DIR = DATA_DIR / "wordfreq"
MERGED_DIR = DATA_DIR / "merged"
RESULTS_DIR = DATA_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

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






# ------- Flags to control which parts of the code to run -------

run_merge_file_creation = False # Set to True to create the merged files

run_jsd_calculation = False # Set to True to run the JSD calculations

save_jsd_results = False # Set to True to save the JSD results to CSV files (and optionally HTML)

print_jsd_values = False # Set to True to print the JSD values

run_create_shift_graphs = True # Set to True to create the JSD shift graphs

print_log_odds_values = False # Set to True to print the log-odds ratio values






# --- Merge Word Frequency Files ---

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





""" REMOVE or KEEP PUNCT WHEN CALC JSD? """
# ------- Jansen-Shannon Distance -------

if run_jsd_calculation:

    subtlex_counts = load_counts_from_wf_txt(subtlex_file)
    opensub_counts = load_counts_from_wf_txt(opensub_file)
    merge_file_counts = load_counts_from_wf_txt(merge_file)
    jsd_rows = []
    subtlex_rows = []
    opensub_rows = []
    count=0

    print("Calculating JSD values for each transcript against Merged-1, SUBTLEX, and OpenSubtitles...")
    for wf_path in wordfreq_file_paths:
        file_id = wf_path.stem[9:19]
        merged_path = MERGED_DIR / f"merged_file_{file_id}.txt"

        wf_counts = load_counts_from_wf_txt(wf_path)
        wf_counts_lower = load_counts_from_wf_txt(wf_path, lowercase=True)
        merged_counts = load_counts_from_wf_txt(merged_path)

        comparison_targets = [
            ("Merged-1", merged_counts, jsd_rows),
            (subtlex_file.stem, subtlex_counts, subtlex_rows),
            (opensub_file.stem, opensub_counts, opensub_rows),
        ]
        for ref_name, ref_counts, row_list in comparison_targets:
            if ref_name == opensub_file.stem:
                transcript_wf = wf_counts_lower
            else:
                transcript_wf = wf_counts
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
            ) = jensen_shannon_distance(transcript_wf, ref_counts)

            row = {
                "ref_file": ref_name,
                "transcript": wf_path.stem[9:19],
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



# ------- Save the JSD results to CSV files (and optionally HTML) -------
if save_jsd_results and not run_jsd_calculation:
    print("Run JSD calculations to save results.")

elif save_jsd_results:
    print("Saving JSD results to CSV files...")

    saved_files = []

    jsd_df = pd.DataFrame(jsd_rows).sort_values("jsd_val", ascending=False).reset_index(drop=True)
    jsd_path = RESULTS_DIR / "jsd_merged.csv"
    jsd_df.to_csv(jsd_path, index=False)
    saved_files.append(jsd_path)

    subtlex_df = pd.DataFrame(subtlex_rows).sort_values("jsd_val", ascending=False).reset_index(drop=True)
    subtlex_path = RESULTS_DIR / "jsd_subtlex.csv"
    subtlex_df.to_csv(subtlex_path, index=False)
    saved_files.append(subtlex_path)

    # opensub_df = pd.DataFrame(opensub_rows).sort_values("jsd_val", ascending=False).reset_index(drop=True)
    # opensub_path = RESULTS_DIR / "jsd_opensub.csv"
    # opensub_df.to_csv(opensub_path, index=False)
    # saved_files.append(opensub_path)

    print("Saved:")
    for path in saved_files:
        print(path)

else:
    print("Skipping saving JSD results.")



# ------- print the JSD values and related statistics for each comparison -------
if run_jsd_calculation and not print_jsd_values:
    print("Run JSD calculations to see the JSD statistics.")
elif print_jsd_values:
    jsd_val, unique_words, shared_words, pct_shared_words, unique_to_a, unique_to_b, pct_shared_of_a, pct_shared_of_b, n_a, n_b = jensen_shannon_distance(merge_file_counts, subtlex_counts)
    print("\nJSD: Merged vs SUBTLEX:")
    print("JSDistance:", round(jsd_val, 4))
    print("Union vocab size:", unique_words)
    print("Percent shared (union):", round(pct_shared_words, 3), "%")
    print("Unique to Merged:", unique_to_a)
    print("Unique to SUBTLEX:", unique_to_b)
    print("Percent of Merged vocab shared:", round(pct_shared_of_a, 3), "%")
    print("Percent of SUBTLEX vocab shared:", round(pct_shared_of_b, 3), "%")
    print("Total tokens A:", n_a)
    print("Total tokens B:", n_b)

    print(f"\nJSD: Merged-1 vs each individual transcript. Total comparisons: {count}")
    print(f"JSDistance: {jsd_df['jsd_val'].min()} - {jsd_df['jsd_val'].max()}")
    print(f"% Shared of Transcript: {jsd_df['pct_shared_of_transcript'].min()}% - {jsd_df['pct_shared_of_transcript'].max()}%")
    print(f"% Shared of Merged-1: {jsd_df['pct_shared_of_merged'].min()}% - {jsd_df['pct_shared_of_merged'].max()}%\n")
    print(jsd_df[['transcript', 'jsd_val', 'shared_words', 'unique_to_transcript', 'pct_shared_words', 'pct_shared_of_transcript', 'pct_shared_of_merged']])

    print(f"\nJSD: SUBTLEX vs each individual transcript. Total comparisons: {count}")
    print(f"JSDistance: {subtlex_df['jsd_val'].min()} - {subtlex_df['jsd_val'].max()}")
    print(f"% Shared of Transcript: {subtlex_df['pct_shared_of_transcript'].min()}% - {subtlex_df['pct_shared_of_transcript'].max()}%")
    print(f"% Shared of SUBTLEX: {subtlex_df['pct_shared_of_subtlex'].min()}% - {subtlex_df['pct_shared_of_subtlex'].max()}%\n")
    print(subtlex_df[['transcript', 'jsd_val', 'shared_words', 'unique_to_transcript', 'pct_shared_words', 'pct_shared_of_transcript', 'pct_shared_of_subtlex']])
else:
    print("Skipping printing JSD statistics.")






# ------- JSD Shift Graphs -------
if not hasattr(maxis.Tick, "label"):
    maxis.Tick.label = property(lambda self: self.label1)

if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping

if run_create_shift_graphs:

    shift_params = {
        "base": 2,
        "weight_1": 0.5,
        "weight_2": 0.5,
        "alpha": 0.8,
    }

    graph_params = {
        "top_n": 50,
        "preserved_placement": True,
        "cumulative_inset": True,
        "text_size_inset": True,
        "width": 14,
        "height": 10,
        "xlabel": "Contribution to JSD",
        "ylabel": "Words",
        "title_fontsize": 16,
        "xlabel_fontsize": 12,
        "ylabel_fontsize": 12,
        "show_total": True,
        "detailed": True,
        "serif": True,
        "tight": True,
        "show_plot": False,
        "dpi": 300,
    }

    # Load the word frequency counts
    merge_file_dict = unique_counts_file_to_dict(merge_file)
    subtlex_file_dict = unique_counts_file_to_dict(subtlex_file)

    # Remove punctuation tokens from both dictionaries to focus the shift graphs on content words
    merge_file_dict = remove_punctuation_tokens(merge_file_dict)
    subtlex_file_dict = remove_punctuation_tokens(subtlex_file_dict)

    # Subtlex vs Merged file
    jsd_shift = sh.JSDivergenceShift(
        type2freq_1=subtlex_file_dict,
        type2freq_2=merge_file_dict,
        **shift_params,
    )
    output_path = RESULTS_DIR / f"jsd_shift_merged_vs_subtlex.png"
    jsd_plot = jsd_shift.get_shift_graph(
        system_names=["SUBTLEX", "Merged"],
        title=f"JSD Shift of HasanAbi Transcripts\nSUBTLEX vs Merged file\nalpha = 0.8",
        **graph_params,
        filename=str(output_path),
    )
    plt.close("all")

    for wf_path in wordfreq_file_paths:

        file_id = wf_path.stem[9:19]
        merged_minus_one_path = MERGED_DIR / f"merged_file_{file_id}.txt"

        merged_minus_one_file_dict = unique_counts_file_to_dict(merged_minus_one_path)
        wf_path_dict = unique_counts_file_to_dict(wf_path)

        merged_minus_one_file_dict = remove_punctuation_tokens(merged_minus_one_file_dict)
        wf_path_dict = remove_punctuation_tokens(wf_path_dict)
        
        jsd_shift = sh.JSDivergenceShift(
            type2freq_1=merged_minus_one_file_dict,
            type2freq_2=wf_path_dict,
            **shift_params,
        )

        output_path = RESULTS_DIR / f"jsd_shift_{file_id}.png"
        
        jsd_plot = jsd_shift.get_shift_graph(
            system_names=["Merged-1", file_id],
            title=f"JSD Shift of HasanAbi Transcripts\nMerged-1 vs {file_id}\nalpha = 0.8",
            **graph_params,
            filename=str(output_path),
        )
        plt.close("all")

    print(f"Created JSD shift graphs for each transcript compared to Merged-1 and saved to {RESULTS_DIR}.")






# ------- Log-Odds Ratios with Prior -------

if print_log_odds_values:
    print("\nLog-odds ratios with prior for Merged vs SUBTLEX:")
    print("\nOverrepresented in Merged vs SUBTLEX:")
    over_subtlex, under_subtlex = log_odds_with_prior_from_files(
        merge_file,
        subtlex_file,
        prior_file=subtlex_file, # define the prior as the reference corpus itself.
        top_n=50,
    )
    print(over_subtlex.head(50))

    top_3_list = [
        ["data/wordfreq/HasanAbi 12-03-2025 transcript_wf.txt","data/merged/merged_file_12-03-2025.txt"],
        ["data/wordfreq/HasanAbi 12-04-2025 transcript_wf.txt","data/merged/merged_file_12-04-2025.txt"],
        ["data/wordfreq/HasanAbi 12-02-2025 transcript_wf.txt","data/merged/merged_file_12-02-2025.txt"],
    ]

    bottom_3_list = [
        ["data/wordfreq/HasanAbi 01-15-2026 transcript_wf.txt","data/merged/merged_file_12-03-2025.txt"],
        ["data/wordfreq/HasanAbi 01-02-2026 transcript_wf.txt","data/merged/merged_file_12-04-2025.txt"],
        ["data/wordfreq/HasanAbi 01-20-2026 transcript_wf.txt","data/merged/merged_file_12-02-2025.txt"],
    ]

    # log-odds for the top 5 transcript with the highest JSD values
    print("\nLog-odds ratios with prior for the top 3 transcripts with the highest JSD values:")
    for wf_path, merged_path in top_3_list:
        over_df, under_df = log_odds_with_prior_from_files(
            wf_path,
            merged_path,
            prior_file=merged_path, # define the prior as the reference corpus itself.
            top_n=50,
            lowercase=False,
        )

        print(f"\nOverrepresented: {wf_path[23:33]} vs Merged-1")
        print(over_df.head(50))

    # log-odds for the top 5 transcript with the highest JSD values
    print("\nLog-odds ratios with prior for the top 3 transcripts with the lowest JSD values:")

    for wf_path, merged_path in bottom_3_list:
        over_df, under_df = log_odds_with_prior_from_files(
            wf_path,
            merged_path,
            prior_file=merged_path, # define the prior as the reference corpus itself.
            top_n=50,
            lowercase=False,
        )
        print(f"\nOverrepresented: {wf_path[23:33]} vs Merged-1")
        print(over_df.head(50))
else:
    print("Skipping Log-Odds calculations.")