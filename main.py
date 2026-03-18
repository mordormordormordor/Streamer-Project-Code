from scripts.lexical_metrics import (
    jensen_shannon_distance_from_files,
)

from scripts.transcript_wordfreq import (
    merge_word_frequency_txt_files,
)

transcript_file = "/Users/sanji/Desktop/Visual Studio/Streamer Project Code/data/wordfreq/HasanAbi 1-2-2026 transcript_wf.txt"
merge_file = "/Users/sanji/Desktop/Visual Studio/Streamer Project Code/data/merged/merged_file.txt"
subtlex_file = "/Users/sanji/Desktop/Visual Studio/Streamer Project Code/data/ref_corpora/subtlex_us_wf.txt"
opensub_file = "/Users/sanji/Desktop/Visual Studio/Streamer Project Code/data/ref_corpora/opensubtitles2018_wf.txt"

jsd_subtlex = jensen_shannon_distance_from_files(transcript_file, subtlex_file)
print("JSD: Transcript vs SUBTLEX:", jsd_subtlex)

jsd_opensub = jensen_shannon_distance_from_files(transcript_file, opensub_file)
print("JSD: Transcript vs OpenSubtitles:", jsd_opensub)

jsd_subtlex = jensen_shannon_distance_from_files(merge_file, subtlex_file)
print("JSD: Merged vs SUBTLEX:", jsd_subtlex)

jsd_opensub = jensen_shannon_distance_from_files(merge_file, opensub_file)
print("JSD: Merged vs OpenSubtitles:", jsd_opensub)
