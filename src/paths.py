"""
Central path constants for the neuro-symbolic Hindi parser repository.

All scripts and pipeline runners should import paths from here so that
reorganizations only require updating this module.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

# Source packages
SRC = PROJECT_ROOT / "src"
PIPELINE_DIR = SRC / "pipeline"

# Scripts (subfolders added to sys.path via scripts/_bootstrap.py)
SCRIPTS = PROJECT_ROOT / "scripts"
SCRIPTS_DATA_PREP = SCRIPTS / "data_prep"
SCRIPTS_EVALUATION = SCRIPTS / "evaluation"
SCRIPTS_ANALYSIS = SCRIPTS / "analysis"
SCRIPTS_EXPERIMENTS = SCRIPTS / "experiments"
SCRIPTS_LEGACY = SCRIPTS / "legacy"

# Experiments (large pipeline CSVs)
EXPERIMENTS = PROJECT_ROOT / "experiments"
STANZA = EXPERIMENTS / "stanza"
STANZA_BASELINE = STANZA / "baseline"
STANZA_CORRECTED = STANZA / "corrected"
STANZA_COMPARISONS = STANZA / "comparisons"
STANZA_GOLD_UD = STANZA / "gold_ud"
UDPIPE = EXPERIMENTS / "udpipe"
UDPIPE_BASELINE = UDPIPE / "baseline"
UDPIPE_CORRECTED = UDPIPE / "corrected"
UDPIPE_COMPARISONS = UDPIPE / "comparisons"
REJECTED = EXPERIMENTS / "rejected"
REJECTED_DR1 = REJECTED / "dependency_repair_v1"

# Outputs (metrics, alignment, gold labels, error analysis)
OUTPUTS = PROJECT_ROOT / "outputs"
OUTPUTS_ALIGNMENT = OUTPUTS / "alignment"
OUTPUTS_GOLD = OUTPUTS / "gold"
OUTPUTS_METRICS = OUTPUTS / "metrics"
OUTPUTS_ERROR_ANALYSIS = OUTPUTS / "error_analysis"
OUTPUTS_REJECTED = OUTPUTS / "rejected_experiments"
OUTPUTS_REJECTED_DR1 = OUTPUTS_REJECTED / "dependency_repair_v1"

# Docs and notebooks
DOCS = PROJECT_ROOT / "docs"
NOTEBOOKS = PROJECT_ROOT / "notebooks"
LOGS = PROJECT_ROOT / "logs"

# UDPipe model cache (not tracked in git)
UDPIPE_MODELS_DIR = PROJECT_ROOT / "models" / "udpipe"
UDPIPE_HI_MODEL_NAME = "hindi-hdtb-ud-2.5-191206.udpipe"
UDPIPE_HI_MODEL_URL = (
    "https://raw.githubusercontent.com/jwijffels/udpipe.models.ud.2.5/master/"
    "inst/udpipe-ud-2.5-191206/hindi-hdtb-ud-2.5-191206.udpipe"
)


def udpipe_hi_model_path() -> Path:
    """Path to the cached Hindi-HDTB UDPipe 2.5 model file."""
    return UDPIPE_MODELS_DIR / UDPIPE_HI_MODEL_NAME


def ud_conllu(split: str) -> Path:
    """Path to a UD CoNLL-U split file."""
    return DATA_RAW / f"hi_hdtb-ud-{split}.conllu"


def stanza_baseline_all(split: str) -> Path:
    return STANZA_BASELINE / f"stanza_{split}_baseline_all.csv"


def stanza_baseline_meaningful(split: str) -> Path:
    return STANZA_BASELINE / f"stanza_{split}_baseline_meaningful.csv"


def stanza_corrected_all(split: str) -> Path:
    return STANZA_CORRECTED / f"stanza_{split}_corrected_v2_all.csv"


def correction_metrics(split: str) -> Path:
    return OUTPUTS_METRICS / f"{split}_correction_v2_metrics.csv"


def correction_per_karaka(split: str) -> Path:
    return OUTPUTS_METRICS / f"{split}_correction_v2_per_karaka_comparison.csv"


def udpipe_baseline_all(split: str) -> Path:
    return UDPIPE_BASELINE / f"udpipe_{split}_baseline_all.csv"


def udpipe_baseline_meaningful(split: str) -> Path:
    return UDPIPE_BASELINE / f"udpipe_{split}_baseline_meaningful.csv"


def udpipe_corrected_all(split: str) -> Path:
    return UDPIPE_CORRECTED / f"udpipe_{split}_corrected_v2_all.csv"


def udpipe_token_matching_audit(split: str) -> Path:
    return OUTPUTS_METRICS / f"udpipe_{split}_token_matching_audit.csv"


def udpipe_correction_metrics(split: str) -> Path:
    return OUTPUTS_METRICS / f"udpipe_{split}_correction_v2_metrics.csv"


def udpipe_per_karaka_comparison(split: str) -> Path:
    return OUTPUTS_METRICS / f"udpipe_{split}_correction_v2_per_karaka_comparison.csv"


def udpipe_vs_gold_comparison(split: str) -> Path:
    return UDPIPE_COMPARISONS / f"udpipe_{split}_vs_gold_matching.csv"


# Backward-compatible aliases (deprecated; kept for transitional imports)
RESULTS = EXPERIMENTS  # noqa: historical name
OUTPUT = OUTPUTS  # noqa: historical name
