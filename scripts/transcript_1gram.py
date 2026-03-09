from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Union

# SPEAKER_PREFIX matches lines like "Speaker A: Hello world" and captures "Speaker A" and "Hello world"
SPEAKER_PREFIX = re.compile(r"^\s*(Speaker\s+[^:]+)\s*:\s*(.*)\s*$")

# Tokenizer that keeps punctuation as its own token
TOKEN_KEEP_PUNCT = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?|[^\w\s]", re.UNICODE)

# Reads a speaker-formatted transcript and writes a .txt where each token is on its own line 
# and return output path.
# Keeps punctuation as separate tokens and removes speaker prefixes (Speaker A:)
def create_1gram_txt(
    txt_path: Union[str, Path],
    *,
    lowercase: bool = False,
    out_txt_path: Optional[Union[str, Path]] = None,
) -> Path:
    path = Path(txt_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    out_path = (
        Path(out_txt_path)
        if out_txt_path is not None
        else path.with_name(f"{path.stem}__1gram.txt")
    )

    with path.open("r", encoding="utf-8", errors="replace") as f, \
         out_path.open("w", encoding="utf-8") as out:

        for raw_line in f:
            line = raw_line.rstrip("\n")
            if not line.strip():
                continue

            m = SPEAKER_PREFIX.match(line)
            text = m.group(2) if m else line.strip()

            if lowercase:
                text = text.lower()

            for tok in TOKEN_KEEP_PUNCT.findall(text):
                out.write(tok + "\n")

    return out_path