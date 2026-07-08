"""
Smoke test for the Hindi UDPipe parser wrapper.

Usage:
    python scripts/experiments/smoke_test_udpipe.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))
sys.path.insert(0, str(SRC_ROOT / "parser"))

from udpipe_parser import parse_sentence_with_udpipe


SAMPLE_SENTENCE = "राम ने आम खाया।"


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    rows = parse_sentence_with_udpipe(SAMPLE_SENTENCE, sent_id="smoke-s1")
    print(f"Sentence: {SAMPLE_SENTENCE}")
    print(f"Tokens:   {len(rows)}")
    print()
    print(f"{'token':<12} {'head':>4} {'deprel':<12}")
    print("-" * 32)
    for row in rows:
        print(f"{row['text']:<12} {row['head']:>4} {row['deprel']:<12}")


if __name__ == "__main__":
    main()
