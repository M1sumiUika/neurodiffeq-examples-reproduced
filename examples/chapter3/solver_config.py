"""振子求解器配置；详细公式和配置见 docs/coverage.md 与 configs。"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from ndeq_examples.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["run", "--example", "solver_config", *sys.argv[1:]]))
