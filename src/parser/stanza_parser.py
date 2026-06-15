"""
Stanza Hindi parser wrapper for parser integration v1.

Loads a Hindi Stanza pipeline (tokenize, pos, lemma, depparse) and returns
token rows compatible with the mapper plus verifier pipeline.
"""

_stanza_pipeline = None
STANZA_LANG = "hi"
STANZA_PROCESSORS = "tokenize,pos,lemma,depparse"
DOWNLOAD_ON_MISSING_MODEL = True


def _build_stanza_pipeline():
    """Create the Hindi Stanza pipeline from available local resources."""
    import stanza

    return stanza.Pipeline(
        lang=STANZA_LANG,
        processors=STANZA_PROCESSORS,
        verbose=False,
    )


def _get_stanza_pipeline():
    """Load the Hindi Stanza pipeline once and reuse it."""
    global _stanza_pipeline
    if _stanza_pipeline is None:
        import stanza

        try:
            _stanza_pipeline = _build_stanza_pipeline()
        except Exception:
            if not DOWNLOAD_ON_MISSING_MODEL:
                raise
            stanza.download(
                STANZA_LANG,
                processors=STANZA_PROCESSORS,
                verbose=False,
            )
            _stanza_pipeline = _build_stanza_pipeline()
    return _stanza_pipeline


def parse_sentence_with_stanza(sentence: str, sent_id: str = "sample-s1") -> list[dict]:
    """
    Parse one Hindi sentence with Stanza.

    Args:
        sentence: Raw Hindi sentence text.
        sent_id: Identifier attached to each token row.

    Returns:
        List of token dictionaries with keys:
            sent_id, token_id, text, lemma, upos, xpos, feats, head, deprel
    """
    nlp = _get_stanza_pipeline()
    doc = nlp(sentence)

    rows = []
    for stanza_sentence in doc.sentences:
        for word in stanza_sentence.words:
            rows.append({
                "sent_id": sent_id,
                "token_id": str(word.id),
                "text": word.text,
                "lemma": word.lemma if word.lemma is not None else "",
                "upos": word.upos if word.upos is not None else "",
                "xpos": word.xpos if word.xpos is not None else "",
                "feats": word.feats if word.feats is not None else "",
                "head": str(word.head),
                "deprel": word.deprel if word.deprel is not None else "",
            })
    return rows


if __name__ == "__main__":
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    sample = "राम ने आम खाया।"
    parsed = parse_sentence_with_stanza(sample, sent_id="demo-s1")
    print(f"Parsed {len(parsed)} tokens from: {sample}")
    for row in parsed:
        print(row)
