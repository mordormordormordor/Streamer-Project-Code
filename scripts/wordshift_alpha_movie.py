

from pathlib import Path
import matplotlib.pyplot as plt
import imageio.v2 as imageio
import shifterator as sh

from wordshift import unique_counts_file_to_dict, PROJECT_ROOT

from transcript_wordfreq import (
    remove_punctuation_tokens,
)

merged_file_path = PROJECT_ROOT / "data" / "merged" / "merged_file_01-09-2026.txt"
hasan_file_path = PROJECT_ROOT / "data" / "wordfreq" / "HasanAbi 01-09-2026 transcript_wf.txt"

merged_file_dict = unique_counts_file_to_dict(merged_file_path)
HasanAbi_01_09_2026_dict = unique_counts_file_to_dict(hasan_file_path)

# Folder for frames
FRAMES_DIR = PROJECT_ROOT / "data" / "results" / "frames_alpha_sweep"
FRAMES_DIR.mkdir(parents=True, exist_ok=True)

frame_paths = []

# 101 frames: alpha from 1.0 down to 0.5
for x in range(101):
    alpha_value = 1.0 - (x * 0.005)

    jsd_shift = sh.JSDivergenceShift(
        type2freq_1=merged_file_dict,
        type2freq_2=HasanAbi_01_09_2026_dict,
        base=2,
        weight_1=0.5,
        weight_2=0.5,
        alpha=alpha_value,
    )

    output_path = FRAMES_DIR / f"jsd_shift_HasanAbi_01_09_2026_alpha_{alpha_value:.5f}.png"
    frame_paths.append(output_path)

    jsd_shift.get_shift_graph(
        system_names=["merged", "01-09-2026"],
        title=f"JSD Shift of HasanAbi Transcripts\nmerged vs 01-09-2026\nalpha={alpha_value:.5f}",
        top_n=50,
        preserved_placement=True,
        cumulative_inset=True,
        text_size_inset=True,
        width=14,
        height=10,
        xlabel="Contribution to JSD",
        ylabel="Words",
        title_fontsize=16,
        xlabel_fontsize=12,
        ylabel_fontsize=12,
        show_total=True,
        detailed=True,
        serif=True,
        tight=True,
        show_plot=False,
        dpi=300,
        filename=str(output_path),
    )

    plt.close("all")

# Build video from frames
video_path = FRAMES_DIR / f"jsd_shift_alpha_sweep_HasanAbi_01_09_2026_2.mp4"

with imageio.get_writer(video_path, fps=10, codec="libx264") as writer:
    for frame_path in frame_paths:
        image = imageio.imread(frame_path)
        writer.append_data(image)

print(f"Video saved to: {video_path}")
