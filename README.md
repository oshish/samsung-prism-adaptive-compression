# Adaptive Compression: Intelligent Frame Compression for Memory Optimization
**Samsung PRISM Student Project**  
**Worklet ID**: 26VI11 | **Department**: CSED  
**Milestone Scope**: Milestone 1 (Foundation & Baseline Implementation)

---

## 1. Project Motivation & Objective
High-resolution imaging in mobile devices (smartphones, cameras, wearables, and smart displays) creates severe memory bandwidth bottlenecks. Transmitting uncompressed 24-bit RGB frame buffers between camera ISPs, GPUs, and LPDDR memory consumes massive bandwidth and battery power.

While lossless compression (e.g. PNG, WebP Lossless) guarantees zero degradation, its compression ratio is modest ($1.5\times$ to $2.5\times$). Lossy compression (e.g. JPEG, WebP Lossy) achieves dramatic memory savings ($5\times$ to $20\times$), but risks introducing objectionable artifacts—particularly in dark regions (shadow blocking), smooth gradients (color banding), and fine textures.

**Core Objective**: Build an intelligent, pre-compression decision system that analyzes incoming uncompressed RGB/YUV image frames and determines the optimal compression domain:
$$\text{LOSSY} \quad \text{or} \quad \text{LOSSLESS}$$
$$\max \text{Memory Savings} \quad \text{subject to} \quad \text{Visual Quality} \ge \text{Acceptable Constraint}$$

---

## 2. Milestone 1 Architecture

```
                       ┌───────────────────────────────┐
                       │    Raw Uncompressed Frame     │
                       │    (RGB / YUV BT.601/709)     │
                       └──────────────┬────────────────┘
                                      │
                                      ▼
                       ┌───────────────────────────────┐
                       │ Pre-Compression Features      │
                       │ • Luminance & Brightness      │
                       │ • Local Variance & GLCM       │
                       │ • Sobel & Laplacian Edges     │
                       │ • Immerkaer Noise Estimate    │
                       │ • Shannon & Color Entropy     │
                       └──────────────┬────────────────┘
                                      │
                                      ▼
                       ┌───────────────────────────────┐
                       │   Intelligent Decision ML     │
                       │ • Random Forest / LogReg      │
                       │ • Rule-Based Heuristic        │
                       └──────────────┬────────────────┘
                                     / \
                                    /   \
                     Decision: LOSSY     Decision: LOSSLESS
                                  /       \
                                 ▼         ▼
                         ┌────────────┐   ┌────────────┐
                         │   Lossy    │   │  Lossless  │
                         │   Codec    │   │   Codec    │
                         └─────┬──────┘   └─────┬──────┘
                                \              /
                                 ▼            ▼
                       ┌───────────────────────────────┐
                       │   Memory Footprint & Quality  │
                       │   (PSNR, SSIM, Dark-SSIM)     │
                       └───────────────────────────────┘
```

---

## 3. Team Responsibilities (Team of 3 Students)

| Student | Role & Domain | Primary Responsibilities |
| :--- | :--- | :--- |
| **Person A** | **ML/DL & Feature Engineering** | Pre-compression feature extractors (`src/features/`), statistical analysis, baseline ML models (Logistic Regression, Decision Tree, Random Forest), feature importance evaluation. |
| **Person B** | **Image Processing & Compression Quality** | Preprocessing (`src/preprocessing/`), RGB ↔ YUV (BT.601/BT.709) color transforms, lossless & lossy codecs (`src/compression/`), PSNR, SSIM, dark-region artifact analysis, banding detection. |
| **Person C** | **Dataset, Pipeline, Integration & Deployment** | Benchmark dataset curation (Kodak + Edge-case suite), leakage-safe train/val/test splitting, ground-truth label generation (`src/dataset/`), CLI runner (`scripts/`), unit tests, and system-level evaluation. |

---

## 4. Repository Structure

```
adaptive-compression/
├── README.md                           # Project documentation and quickstart
├── requirements.txt                    # Exact pinned dependencies
├── configs/
│   └── config.yaml                     # Centralized experiment parameters
├── data/
│   ├── raw/                            # 30 benchmark frames (Kodak + Stress suite)
│   └── metadata/                       # Manifests, splits, features, and labels
├── src/
│   ├── preprocessing/                  # Validation and RGB ↔ YUV transforms
│   ├── features/                       # Pre-compression feature extraction
│   ├── compression/                    # Lossless and lossy codec wrappers
│   ├── evaluation/                     # PSNR, SSIM, and artifact metrics
│   ├── dataset/                        # Benchmark builder and labeler
│   ├── models/                         # Baseline classifiers and ML wrappers
│   └── utils/                          # Logger and visualizer
├── scripts/
│   ├── 01_prepare_dataset.py           # Ingests benchmark and generates splits
│   ├── 02_run_compression_benchmark.py # Evaluates 300 rate-distortion trials
│   ├── 03_extract_features.py          # Builds feature table
│   ├── 04_generate_labels.py           # Generates empirical ground-truth labels
│   ├── 05_train_baselines.py           # Trains all 5 baseline models
│   ├── 06_evaluate_system.py           # Quantifies net memory and quality impact
│   └── run_pipeline.py                 # One-click end-to-end runner
├── results/
│   ├── baseline/                       # Model metrics and predictions
│   ├── figures/                        # Generated charts and diagrams
│   └── system_evaluation.json          # Net system performance report
├── tests/                              # Comprehensive pytest suite (18 tests)
└── docs/
    ├── PROJECT_PLAN.md                 # Detailed milestone roadmap
    ├── ASSUMPTIONS.md                  # All assumptions with mentor review status
    ├── MENTOR_QUESTIONS.md             # Prioritized questions for mentor meeting
    ├── MILESTONE_1_REPORT.md           # Formal Milestone 1 technical report
    └── learning/                       # 10 reverse-learning guides for students
```

---

## 5. Quickstart & How to Run

### Environment Setup
```bash
# 1. Create and activate virtual environment
uv venv .venv
source .venv/bin/activate

# 2. Install dependencies
uv pip install -r requirements.txt
```

### Run Full Pipeline
```bash
# Runs all 6 steps sequentially from raw data to system evaluation
python scripts/run_pipeline.py --config configs/config.yaml
```

### Run Unit Tests
```bash
pytest tests/ -v
```

---

## 6. Key Scientific Principles

### Empirical Ground-Truth Labeling
We do **not** assume an arbitrary rule like "bright $\to$ lossy". Instead, labels are generated empirically:
1. Every image is compressed losslessly (PNG) to establish $S_{\text{lossless}}$.
2. Every image is compressed with lossy codec (JPEG Q=75) to measure $S_{\text{lossy}}$, $\text{SSIM}$, $\text{PSNR}$, and $\text{Dark-SSIM}$.
3. An image is labeled **LOSSY** if and only if:
   - Visual quality satisfies: $\text{SSIM} \ge 0.95$ and $\text{PSNR} \ge 34.0\text{ dB}$
   - Size reduction is worthwhile: $\frac{S_{\text{lossless}} - S_{\text{lossy}}}{S_{\text{lossless}}} \ge 25\%$
   - Dark-region distortion is safe: $\text{Dark-SSIM} \ge 0.92$
4. Otherwise, it is labeled **LOSSLESS**.

*(All thresholds are configurable in `configs/config.yaml` and tracked under `ASSUMPTION — REQUIRES MENTOR CONFIRMATION`)*.

### Zero Target Leakage
Every feature passed to our classifiers is computed strictly on the uncompressed input frame prior to compression. Features like post-compression file size, compression ratio, and quality scores are blacklisted and verified by automated tests (`tests/test_leakage.py`).

---

## 7. Limitations & Milestone 2 Roadmap
* **Milestone 1 Limitations**:
  - Binary decision formulation (Lossy vs Lossless).
  - Software codecs (JPEG/WebP) used as proxies for hardware frame buffers.
  - Small, high-quality benchmark set (30 frames).
* **Recommended Milestone 2 Scope**:
  - Expand to multi-level adaptive compression (e.g. Lossless, High-Quality Lossy, Aggressive Lossy).
  - Benchmark lightweight Deep Learning / MobileNet backbones against our tabular feature baselines.
  - Test on high-resolution camera burst datasets and mobile UI screenshot sequences.
