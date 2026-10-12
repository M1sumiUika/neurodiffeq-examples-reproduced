# NeuroDiffEq Examples Reproduced

A runnable reproduction and numerical validation of the **2023-04-03 NeuroDiffEq documentation**, with Chinese explanations. This is a software documentation reproduction project, not an original solver or a whole-paper replication.

The project implements 25 independent configurations/snippet groups covering Chapters 1–5: exponential decay, second-order and first-order harmonic oscillators, Lotka–Volterra, Poisson, Laplace, the 1D heat equation with nonhomogeneous Neumann conditions, the nonlinear hexagram-domain PDE, custom solver settings, legacy migration, API snippets, residuals, hard initial conditions, and automatic differentiation.

**Actual status:** 18 training configurations were run to their declared full epoch budgets; 6 passed all predefined numerical criteria. Seven snippet groups passed their checks. Fifteen additional benchmark runs use seeds 42, 43, and 44. Failed numerical acceptance is retained and reported; smoke success is never called numerical reproduction success. Six notebooks were executed in separate kernels.

## Install and run

Validated: Python 3.12.6, NeuroDiffEq distribution 0.7.0, PyTorch 2.6.0, NumPy 1.26.4, SciPy 1.15.2. CPU is the default. The module's `__version__` incorrectly reports `0.6.3-dev`; distribution metadata is recorded separately.

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -e ".[dev]"
python -m ndeq_examples list
python -m ndeq_examples run --example decay --mode smoke
python -m ndeq_examples run --example decay --mode reproduction
python -m ndeq_examples run --chapter 2 --mode reproduction --resume
python -m ndeq_examples run --all --mode smoke
python -m ndeq_examples run --example hard_soft --mode benchmark --variants default soft
python -m ndeq_examples summarize
python -m pytest -q
```

`requirements-lock-cpu.txt` contains the verified isolated CPU environment snapshot. It excludes personal paths. `--resume` skips completed configurations, while `--resume-from <run-directory>` continues a locally generated checkpoint in a new output directory. Benchmark mode requires at least three seeds. Untrusted pickle checkpoints should not be loaded.

Every differential-equation run saves the configuration, environment, runtime, training/validation loss, independent test residuals, condition errors, maximum solution error, RMSE, relative L2 error, raw arrays, and plots. Lotka–Volterra uses a tolerance-checked DOP853 numerical reference. The heat animation is a GIF and needs no FFmpeg. Exact polygon masks and separate boundary evaluation are used for the star.

See [coverage](docs/coverage.md), [errata](docs/errata.md), [migration](docs/api_migration.md), [validation protocol](docs/validation_protocol.md), [actual experiment report](docs/experiment_report.md), and [selected results](results/README.md).

Limitations: one primary reproduction seed; several original epoch budgets do not converge to our criteria; GPU and Linux full training were not locally tested. The supplied `大创1.py` could not be located, so its content and license review remain pending. No GitHub credentials were available; [upload instructions](docs/github_upload.md) are provided. The third-party PDF and private reference files are excluded.

Upstream: [NeuroDiffEq](https://github.com/NeuroDiffGym/neurodiffeq), [documentation](https://neurodiffeq.readthedocs.io/en/latest/), [JOSS paper](https://doi.org/10.21105/joss.01931). See [third-party notices](THIRD_PARTY_NOTICES.md) for attribution and license preservation.

