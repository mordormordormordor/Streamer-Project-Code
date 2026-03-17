from pathlib import Path
from collections import Counter
from typing import Dict, Tuple
import math
import pandas as pd

# Count all tokens in a Counter, returns total number of tokens
def total_tokens(c: Counter) -> int:
    return int(sum(c.values()))

# Load word counts from a .txt file
def load_counts_from_wf_txt(path: str | Path) -> Counter:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    counts = Counter()
    in_wf_section = False

    # Read the file line by line, looking for the "== Word Frequency ==" section
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            line = raw.rstrip("\n") # Remove trailing newline characters

            # Skip empty lines
            if not line.strip():
                continue

            if line.strip() == "== Word Frequency ==":
                in_wf_section = True
                continue
            
            # Ignores "sources: ..."
            if not in_wf_section:
                continue

            # Expected format: "word\tcount"
            parts = line.split("\t")
            if len(parts) < 2:
                continue

            # Extract the word and count
            word = parts[0].strip()
            count_str = parts[1].strip()

            # Skip if the word is empty
            if not word:
                continue

            # Try to convert the count to an integer, skip if it's not a valid number
            try:
                counts[word] = int(count_str)
            except ValueError:
                continue

    return counts


# Compares two corpora as whole word-frequency distributions and returns a single
# Jensen-Shannon distance value measuring how different the distributions are.
def jensen_shannon_distance(counts_a: Counter, counts_b: Counter, alpha: float = 1e-9) -> float:
    # Creates the union of all words appearing in either corpus, ensures both corpora are 
    # compared over the same vocabulary space.
    vocab = set(counts_a) | set(counts_b)
    n_a, n_b = total_tokens(counts_a), total_tokens(counts_b)

    if n_a == 0 or n_b == 0 or len(vocab) == 0:
        return 0.0

    # Number of unique words across both corpora.
    V = len(vocab)

    # Convert counts into probabilities, creates a probability distribution over the shared vocabulary.
    def prob(counts: Counter, n: int) -> Dict[str, float]:
        # Give each word a small probability, ensuring no word has zero probability.
        denom = n + alpha * V
        return {w: (counts.get(w, 0) + alpha) / denom for w in vocab}

    # Compute the probability distributions for both corpora.
    P = prob(counts_a, n_a)
    Q = prob(counts_b, n_b)

    # Compute the average distribution M, which is the midpoint between P and Q.
    M = {w: 0.5 * (P[w] + Q[w]) for w in vocab}

    # KL divergense helper function, computes the KL divergence from distribution A to B, 
    # measures how much information is lost when B is used to approximate A.
    def kl(A: Dict[str, float], B: Dict[str, float]) -> float:
        s = 0.0
        for w in vocab:
            s += A[w] * math.log(A[w] / B[w])
        return s

    # Compare both distributions to the average distribution M, measures how much P and Q differ from their average.
    js = math.sqrt(0.5 * kl(P, M) + 0.5 * kl(Q, M))
    return js

# Wrapper function to compute JSD directly from file paths, loads the counts and then computes the distance.
def jensen_shannon_distance_from_files(
    file_a: str | Path,
    file_b: str | Path,
    alpha: float = 1e-9,
) -> float:
    counts_a = load_counts_from_wf_txt(file_a)
    counts_b = load_counts_from_wf_txt(file_b)
    return jensen_shannon_distance(counts_a, counts_b, alpha=alpha)
