# Learning Module 10: End-to-End Pipeline & Reproducibility

## 1. What We Built
In `scripts/run_pipeline.py`, we created a single, reproducible CLI execution workflow that coordinates all phases from raw data to system benchmarking:

```
01_prepare_dataset.py ──► 02_run_compression_benchmark.py ──► 03_extract_features.py
           │
           ▼
04_generate_labels.py ──► 05_train_baselines.py ──► 06_evaluate_system.py
```

## 2. Execution Commands
```bash
# Activate virtual environment
source .venv/bin/activate

# Execute complete pipeline
python scripts/run_pipeline.py --config configs/config.yaml

# Run unit and integration tests
pytest tests/ -v
```

## 3. Directory Outputs
* `data/raw/`: 30 benchmark frames (Kodak + edge-case stress frames).
* `data/metadata/splits.csv`: Partition manifest with deterministic seeds.
* `data/metadata/compression_experiments.csv`: 300 rate-distortion compression trials.
* `data/metadata/features.csv`: 18 pre-compression image features.
* `data/metadata/labels.csv`: Empirical ground-truth decisions with metrics.
* `results/baseline/model_metrics.json`: Test set classification metrics.
* `results/system_evaluation.json`: Net memory and quality impact report.
* `results/figures/`: Publication-quality plots (class distribution, feature distributions, confusion matrices, trade-offs, and feature importances).

## 4. PRISM / Technical Interview Questions
1. *Q: Why is modular CLI pipeline design critical for Samsung PRISM?*  
   **A**: It eliminates manual notebook execution dependencies, ensures absolute reproducibility across team members and mentor evaluations, and prepares the codebase for production CI/CD testing.
