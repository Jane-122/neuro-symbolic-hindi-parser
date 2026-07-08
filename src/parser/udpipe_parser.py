"""
UDPipe Hindi parser wrapper for parser robustness experiments.

Loads the Hindi-HDTB UD 2.5 UDPipe model and returns token rows compatible
with the Stanza baseline runner and mapper/verifier pipeline.
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parent.parent
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from paths import (
    UDPIPE_HI_MODEL_NAME,
    UDPIPE_HI_MODEL_URL,
    UDPIPE_MODELS_DIR,
    udpipe_hi_model_path,
)


_udpipe_model = None
_udpipe_pipeline = None

DOWNLOAD_ON_MISSING_MODEL = True


def _download_hi_model(destination: Path) -> None:
    """Download the Hindi-HDTB UDPipe model into the local cache."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        UDPIPE_HI_MODEL_URL,
        headers={"User-Agent": "neuro-symbolic-hindi-parser/1.0"},
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        destination.write_bytes(response.read())


def _resolve_model_path(model_path: Path | None = None) -> Path:
    """Return a usable model path, downloading the default model if needed."""
    path = model_path or udpipe_hi_model_path()
    if path.exists():
        return path
    if not DOWNLOAD_ON_MISSING_MODEL:
        raise FileNotFoundError(
            f"UDPipe model not found at {path}. "
            f"Download {UDPIPE_HI_MODEL_NAME} manually or set DOWNLOAD_ON_MISSING_MODEL."
        )
    print(f"Downloading UDPipe model to: {path}")
    _download_hi_model(path)
    return path


def _get_udpipe_pipeline(model_path: Path | None = None):
    """Load the Hindi UDPipe model and pipeline once and reuse them."""
    global _udpipe_model, _udpipe_pipeline

    if _udpipe_pipeline is not None:
        return _udpipe_pipeline

    from ufal.udpipe import Model, Pipeline  # pylint: disable=import-outside-toplevel

    resolved_path = _resolve_model_path(model_path)
    _udpipe_model = Model.load(str(resolved_path))
    if _udpipe_model is None:
        raise RuntimeError(f"Cannot load UDPipe model from {resolved_path}")

    _udpipe_pipeline = Pipeline(
        _udpipe_model,
        "tokenize",
        Pipeline.DEFAULT,
        Pipeline.DEFAULT,
        "conllu",
    )
    return _udpipe_pipeline


def _parse_conllu_text(conllu_text: str, sent_id: str) -> list[dict]:
    """Convert UDPipe CoNLL-U output into Stanza-compatible token rows."""
    rows: list[dict] = []
    current_sent_id = sent_id

    for line in conllu_text.splitlines():
        line = line.rstrip("\n")
        if not line:
            continue
        if line.startswith("# sent_id = "):
            current_sent_id = line[len("# sent_id = "):]
            continue
        if line.startswith("#"):
            continue

        columns = line.split("\t")
        if len(columns) < 8 or "-" in columns[0]:
            continue

        rows.append({
            "sent_id": current_sent_id,
            "token_id": columns[0],
            "text": columns[1],
            "lemma": "" if columns[2] == "_" else columns[2],
            "upos": "" if columns[3] == "_" else columns[3],
            "xpos": "" if columns[4] == "_" else columns[4],
            "feats": "" if columns[5] == "_" else columns[5],
            "head": columns[6],
            "deprel": "" if columns[7] == "_" else columns[7],
        })

    return rows


def parse_sentence_with_udpipe(
    sentence: str,
    sent_id: str = "sample-s1",
    model_path: Path | None = None,
) -> list[dict]:
    """
    Parse one Hindi sentence with UDPipe.

    Args:
        sentence: Raw Hindi sentence text.
        sent_id: Identifier attached to each token row when CoNLL-U has no sent_id.
        model_path: Optional override for the Hindi UDPipe model file.

    Returns:
        List of token dictionaries with keys:
            sent_id, token_id, text, lemma, upos, xpos, feats, head, deprel
    """
    from ufal.udpipe import ProcessingError  # pylint: disable=import-outside-toplevel

    pipeline = _get_udpipe_pipeline(model_path)
    error = ProcessingError()
    conllu_text = pipeline.process(sentence, error)
    if error.occurred():
        raise RuntimeError(f"UDPipe failed to parse sentence: {error.message}")

    rows = _parse_conllu_text(conllu_text, sent_id)
    for row in rows:
        row["sent_id"] = sent_id
    return rows


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    sample = "राम ने आम खाया।"
    parsed = parse_sentence_with_udpipe(sample, sent_id="demo-s1")
    print(f"Parsed {len(parsed)} tokens from: {sample}")
    for row in parsed:
        print(row)
