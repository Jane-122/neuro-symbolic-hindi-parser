"""
Bootstrap import paths for reorganized scripts/ subpackages.

Import this module at the top of any script that lives under scripts/
(or run via ``python -m`` from project root) so cross-script imports work
after the directory reorganization.
"""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SRC = _PROJECT_ROOT / "src"
_PIPELINE = _SRC / "pipeline"

_PATHS_TO_ADD = [
    _PROJECT_ROOT,
    _SRC,
    _PIPELINE,
    Path(__file__).resolve().parent,
    _PROJECT_ROOT / "scripts" / "data_prep",
    _PROJECT_ROOT / "scripts" / "evaluation",
    _PROJECT_ROOT / "scripts" / "analysis",
    _PROJECT_ROOT / "scripts" / "experiments",
    _PROJECT_ROOT / "scripts" / "legacy",
]

for _path in _PATHS_TO_ADD:
    _path_str = str(_path)
    if _path_str not in sys.path:
        sys.path.insert(0, _path_str)
