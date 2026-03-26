from pathlib import Path
from typing import Dict, Union
import matplotlib.axis as maxis
import collections
import collections.abc
import shifterator as sh


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if not hasattr(maxis.Tick, "label"):
    maxis.Tick.label = property(lambda self: self.label1)

if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping

def unique_counts_file_to_dict(path: Union[str, Path]) -> Dict[str, int]:
    p = Path(path)
    new_dict: Dict[str, int] = {}
    in_wf_section = False

    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue

        if line.strip() == "== Word Frequency ==":
            in_wf_section = True
            continue

        if not in_wf_section:
            continue

        parts = line.split("\t")
        if len(parts) < 2:
            continue

        word = parts[0].strip()
        count_str = parts[1].strip()

        if not word:
            continue

        try:
            new_dict[word] = int(count_str)
        except ValueError:
            continue

    return new_dict


merged_file_path = PROJECT_ROOT / "data" / "merged" / "merged_file_01-09-2026.txt"
hasan_file_path = PROJECT_ROOT / "data" / "wordfreq" / "HasanAbi 01-09-2026 transcript_wf.txt"

merged_file_dict = unique_counts_file_to_dict(merged_file_path)
HasanAbi_01_09_2026_dict = unique_counts_file_to_dict(hasan_file_path)

jsd_shift = sh.JSDivergenceShift(
    type2freq_1=merged_file_dict,
    type2freq_2=HasanAbi_01_09_2026_dict,
    base=2,
    weight_1=0.5,
    weight_2=0.5,
    alpha=1
)

jsd_shift.get_shift_graph(
    system_names=['merged', '01-09-2026'],
    title='JSD Shift of HasanAbi Transcripts\nmerged vs 01-09-2026',
    cumulative_inset=True,
    text_size_inset=True,
    show_plot=True
)