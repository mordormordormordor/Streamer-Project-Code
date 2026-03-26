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
print_jsd_values = True # Set to True to print the JSD values

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

# jsd_df.to_html(DATA_DIR / "results" / "jsd_merged.html", index=False)
# subtlex_df.to_html(DATA_DIR / "results" / "jsd_subtlex.html", index=False)
# opensub_df.to_html(DATA_DIR / "results" / "jsd_opensub.html", index=False)
# print(DATA_DIR / "results" / "jsd_merged.html")
# print(DATA_DIR / "results" / "jsd_subtlex.html")
# print(DATA_DIR / "results" / "jsd_opensub.html")

if print_jsd_values:
    jsd_val, unique_words, shared_words, pct_shared_words, unique_to_a, unique_to_b, pct_shared_of_a, pct_shared_of_b, n_a, n_b = jensen_shannon_distance(merge_file_counts, subtlex_counts)
    print("\nMerged vs SUBTLEX:")
    print("JSD:", round(jsd_val, 4))
    print("Union vocab size:", unique_words)
    print("Percent shared (union):", round(pct_shared_words, 3), "%")
    print("Unique to Merged:", unique_to_a)
    print("Unique to SUBTLEX:", unique_to_b)
    print("Percent of Merged vocab shared:", round(pct_shared_of_a, 3), "%")
    print("Percent of SUBTLEX vocab shared:", round(pct_shared_of_b, 3), "%")
    print("Total tokens A:", n_a)
    print("Total tokens B:", n_b)

    jsd_val, unique_words, shared_words, pct_shared_words, unique_to_a, unique_to_b, pct_shared_of_a, pct_shared_of_b, n_a, n_b = jensen_shannon_distance(merge_file_counts, opensub_counts)
    print("\nMerged vs OpenSubtitles:")
    print("JSD:", round(jsd_val, 4))
    print("Union vocab size:", unique_words)
    print("Percent shared (union):", round(pct_shared_words, 3), "%")
    print("Unique to Merged:", unique_to_a)
    print("Unique to OpenSubtitles:", unique_to_b)
    print("Percent of Merged vocab shared:", round(pct_shared_of_a, 3), "%")
    print("Percent of OpenSubtitles vocab shared:", round(pct_shared_of_b, 3), "%")
    print("Total tokens A:", n_a)
    print("Total tokens B:", n_b, "\n")

    print(f"\nJSD: Merged-1 vs each individual transcript. Total comparisons: {count}")
    print(f"JSD: {jsd_df['jsd_val'].min()} - {jsd_df['jsd_val'].max()}")
    print(f"% Shared of Transcript: {jsd_df['pct_shared_of_transcript'].min()}% - {jsd_df['pct_shared_of_transcript'].max()}%")
    print(f"% Shared of Merged-1: {jsd_df['pct_shared_of_merged'].min()}% - {jsd_df['pct_shared_of_merged'].max()}%\n")
    print(jsd_df[['transcript', 'jsd_val', 'shared_words', 'unique_to_transcript', 'pct_shared_words', 'pct_shared_of_transcript', 'pct_shared_of_merged']])

    print(f"\nJSD: SUBTLEX vs each individual transcript. Total comparisons: {count}")
    print(f"JSD: {subtlex_df['jsd_val'].min()} - {subtlex_df['jsd_val'].max()}")
    print(f"% Shared of Transcript: {subtlex_df['pct_shared_of_transcript'].min()}% - {subtlex_df['pct_shared_of_transcript'].max()}%")
    print(f"% Shared of SUBTLEX: {subtlex_df['pct_shared_of_subtlex'].min()}% - {subtlex_df['pct_shared_of_subtlex'].max()}%\n")
    print(subtlex_df[['transcript', 'jsd_val', 'shared_words', 'unique_to_transcript', 'pct_shared_words', 'pct_shared_of_transcript', 'pct_shared_of_subtlex']])

    print(f"\nJSD: OpenSubtitles vs each individual transcript. Total comparisons: {count}:")
    print(f"JSD: {opensub_df['jsd_val'].min()} - {opensub_df['jsd_val'].max()}")
    print(f"% Shared of Transcript: {opensub_df['pct_shared_of_transcript'].min()}% - {opensub_df['pct_shared_of_transcript'].max()}%")
    print(f"% Shared of OpenSubtitles: {opensub_df['pct_shared_of_opensub'].min()}% - {opensub_df['pct_shared_of_opensub'].max()}%\n")
    print(opensub_df[['transcript', 'jsd_val', 'shared_words', 'unique_to_transcript', 'pct_shared_words', 'pct_shared_of_transcript', 'pct_shared_of_opensub']])

# ------- Log-Odds Ratios with Prior -------
over_subtlex, under_subtlex = log_odds_with_prior_from_files(
    merge_file,
    subtlex_file,
    prior_file=subtlex_file, # define the prior as the reference corpus itself.
    top_n=30,
)

# Top 3:
# Merge HasanAbi 12-03-2025 transcript_wf	0.2839
# Merge HasanAbi 12-04-2025 transcript_wf	0.2768
# Merge HasanAbi 12-02-2025 transcript_wf	0.2746
# opensubtitles2018_wf	HasanAbi 12-26-2025 transcript_wf	0.6531
# opensubtitles2018_wf	HasanAbi 01-06-2026 transcript_wf	0.6529
# opensubtitles2018_wf	HasanAbi 12-09-2025 transcript_wf	0.651
# subtlex_us_wf	HasanAbi 12-04-2025 transcript_wf	0.5046
# subtlex_us_wf	HasanAbi 01-01-2026 transcript_wf	0.501
# subtlex_us_wf	HasanAbi 12-28-2025 transcript_wf	0.501

# Bottom 3:
# Merge HasanAbi 01-15-2026 transcript_wf	0.2368
# Merge HasanAbi 01-02-2026 transcript_wf	0.2362
# Merge HasanAbi 01-20-2026 transcript_wf	0.2311
# opensubtitles2018_wf	HasanAbi 01-07-2026 transcript_wf	0.633
# opensubtitles2018_wf	HasanAbi 11-28-2025 transcript_wf	0.6293
# opensubtitles2018_wf	HasanAbi 01-25-2026 transcript_wf	0.6274
# subtlex_us_wf	HasanAbi 01-16-2026 transcript_wf	0.4854
# subtlex_us_wf	HasanAbi 01-08-2026 transcript_wf	0.484
# subtlex_us_wf	HasanAbi 12-27-2025 transcript_wf	0.4818

# JSD increased after lowercasing the OpenSubtitles counts, which makes sense since the transcript word frequencies are also lowercased, 
# so this should make them more similar and thus reduce the distance. However, the JSD values are still quite high, indicating that there are 
# still many differences in the word frequency distributions between the transcripts and the OpenSubtitles reference corpus, even after lowercasing.

# ref_file	transcript	jsd_val	shared_words	pct_shared_words	unique_to_transcript	pct_shared_of_transcript	total_tokens_transcript	unique_to_opensub	pct_shared_of_opensub
# opensubtitles2018_wf	HasanAbi 12-26-2025 transcript_wf	0.6531	4600	14.513	1697	73.051	36604	25398	15.334
# opensubtitles2018_wf	HasanAbi 01-06-2026 transcript_wf	0.6529	3616	11.592	1196	75.145	27348	26382	12.054
# opensubtitles2018_wf	HasanAbi 12-09-2025 transcript_wf	0.651	3588	11.542	1088	76.732	26653	26410	11.961

# opensubtitles2018_wf	HasanAbi 12-04-2025 transcript_wf	0.5016	2749	8.848	1070	71.982	32062	27249	9.164
# opensubtitles2018_wf	HasanAbi 01-18-2026 transcript_wf	0.4982	3472	11.011	1535	69.343	49086	26526	11.574
# opensubtitles2018_wf	HasanAbi 12-03-2025 transcript_wf	0.4976	2585	8.341	995	    72.207	31677	27413	8.617

top_3_list = [
    # Merged-1
    ["data/wordfreq/HasanAbi 12-03-2025 transcript_wf.txt","data/merged/merged_file_12-03-2025.txt"],
    ["data/wordfreq/HasanAbi 12-04-2025 transcript_wf.txt","data/merged/merged_file_12-04-2025.txt"],
    ["data/wordfreq/HasanAbi 12-02-2025 transcript_wf.txt","data/merged/merged_file_12-02-2025.txt"],

    # OpenSubtitles
    ["data/wordfreq/HasanAbi 12-04-2025 transcript_wf.txt","data/ref_corpora/opensubtitles2018_wf.txt"],
    ["data/wordfreq/HasanAbi 01-18-2026 transcript_wf.txt","data/ref_corpora/opensubtitles2018_wf.txt"],
    ["data/wordfreq/HasanAbi 12-03-2025 transcript_wf.txt","data/ref_corpora/opensubtitles2018_wf.txt"],

    # SUBTLEX
    ["data/wordfreq/HasanAbi 12-04-2025 transcript_wf.txt","data/ref_corpora/subtlex_us_wf.txt"],
    ["data/wordfreq/HasanAbi 01-01-2026 transcript_wf.txt","data/ref_corpora/subtlex_us_wf.txt"],
    ["data/wordfreq/HasanAbi 01-25-2026 transcript_wf.txt","data/ref_corpora/subtlex_us_wf.txt"],
]

bottom_3_list = [
    # Merged-1
    ["data/wordfreq/HasanAbi 01-15-2026 transcript_wf.txt","data/merged/merged_file_12-03-2025.txt"],
    ["data/wordfreq/HasanAbi 01-02-2026 transcript_wf.txt","data/merged/merged_file_12-04-2025.txt"],
    ["data/wordfreq/HasanAbi 01-20-2026 transcript_wf.txt","data/merged/merged_file_12-02-2025.txt"],

    # OpenSubtitles
    ["data/wordfreq/HasanAbi 12-27-2025 transcript_wf.txt","data/ref_corpora/opensubtitles2018_wf.txt"],
    ["data/wordfreq/HasanAbi 01-16-2026 transcript_wf.txt","data/ref_corpora/opensubtitles2018_wf.txt"],
    ["data/wordfreq/HasanAbi 01-08-2026 transcript_wf.txt","data/ref_corpora/opensubtitles2018_wf.txt"],

    # SUBTLEX
    ["data/wordfreq/HasanAbi 01-16-2026 transcript_wf.txt","data/ref_corpora/subtlex_us_wf.txt"],
    ["data/wordfreq/HasanAbi 01-08-2026 transcript_wf.txt","data/ref_corpora/subtlex_us_wf.txt"],
    ["data/wordfreq/HasanAbi 12-27-2025 transcript_wf.txt","data/ref_corpora/subtlex_us_wf.txt"],
]


label_list = ["Merged-1", "Merged-1", "Merged-1", "OpenSubtitles", "OpenSubtitles", "OpenSubtitles", "SUBTLEX", "SUBTLEX", "SUBTLEX"]
count = 0
print("\nLog-odds ratios with prior for the top 3 transcripts with the highest JSD values:")
for wf_path, merged_path in top_3_list:
    if label_list[count] == "OpenSubtitles":
        lowercase = True
    else:
        lowercase = False
    # log-odds for the top 5 transcript with the highest JSD values
    over_df, under_df = log_odds_with_prior_from_files(
        wf_path,
        merged_path,
        prior_file=merged_path, # define the prior as the reference corpus itself.
        top_n=30,
        lowercase=lowercase,
    )

    print(f"\nOverrepresented: {wf_path[23:33]} vs {label_list[count]}")
    print(over_df.head(30))
    count += 1

count = 0
print("\nLog-odds ratios with prior for the top 3 transcripts with the lowest JSD values:")
for wf_path, merged_path in bottom_3_list:
    if label_list[count] == "OpenSubtitles":
        lowercase = True
    else:
        lowercase = False
    # log-odds for the top 5 transcript with the highest JSD values
    over_df, under_df = log_odds_with_prior_from_files(
        wf_path,
        merged_path,
        prior_file=merged_path, # define the prior as the reference corpus itself.
        top_n=30,
        lowercase=lowercase,
    )
    print(f"\nOverrepresented: {wf_path[23:33]} vs {label_list[count]}")
    print(over_df.head(30))
    count += 1
