# Adaptive Frame Compression: Intelligent Frame Compression for Memory Optimization

**Samsung PRISM Student Project**  
**Worklet ID:** 26VI11  
**Department:** Computer Science & Engineering (CSED)  
**Program:** Samsung PRISM  
**Milestone:** 1 (Steps 1–10 Complete)  
**Team:** 3 Student Researchers  

---

> [!IMPORTANT]
> **Milestone 1 Complete (Steps 1–10):**  
> This repository contains the complete, reproducible end-to-end implementation of **Milestone 1** for the Samsung PRISM Adaptive Compression project:
> 1. ~1,000 diverse image dataset acquired, cleaned, and standardized (Caltech-101, Kodak, Synthetic Stress).
> 2. RGB and ITU-R BT.601 YUV dual color-space representation.
> 3. Modular pre-compression feature extraction (40 features, $\mathcal{O}(N)$ complexity, strict zero target leakage).
> 4. Compression experiments across 6 codec configurations (PNG, WebP Lossless, JPEG at Q=50, 75, 85, 95) with 6,180 empirical trials.
> 5. Quality evaluation across PSNR, SSIM, localized Dark-SSIM ($Y < 40$), Banding risk score, and Edge preservation.
> 6. Empirical ground-truth labeling (`LOSSY` vs `LOSSLESS`), full decision evidence retention, and `ml_dataset.csv`.
> 7. Baseline ML classifiers (Majority Class, Rule-Based Heuristic, Logistic Regression, Decision Tree, Random Forest) evaluated on Train, Val, and Test splits.
> 8. Real-world system memory storage and visual quality tradeoff evaluation.
>
> **Scope Boundary:** In accordance with PRISM instructions, we stop strictly after Step 10 baselines. Deep learning, CNNs, and Milestone 2 optimizations are NOT included.

---

## 1. Project Overview & Motivation

High-resolution imaging in mobile devices (smartphones, cameras, wearables, and smart displays) creates severe memory bandwidth, thermal, and battery bottlenecks. Transmitting uncompressed 24-bit RGB frame buffers between camera ISPs, GPUs, display processors, and LPDDR memory consumes massive power.
* **Lossless compression** (e.g. PNG, WebP Lossless) guarantees perfect mathematical reconstruction, but its compression ratio is modest ($2.5\times$ to $4.0\times$).
* **Lossy compression** (e.g. JPEG, WebP Lossy) achieves massive memory bandwidth savings ($8\times$ to $20\times$), but risks introducing objectionable artifacts—especially shadow blocking in low-light regions ($Y < 40$), color banding in smooth gradients, and texture blurring.

**Core Research Question**:  
*Given an uncompressed input frame, can we intelligently predict before compression whether lossy mode satisfies visual quality while delivering $\ge 25\%$ memory savings, or whether lossless mode is mandatory?*

---

## 2. Key Milestone 1 Results

### 2.1 Out-of-Sample Test Set Classification Performance (155 Frames)

| Model Architecture | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Confusion Matrix `[TN, FP; FN, TP]` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Decision Tree ($d \le 4$)** | **$1.0000$** | **$1.0000$** | **$1.0000$** | **$1.0000$** | **$1.0000$** | `[2, 0; 0, 153]` (Perfect separation) |
| **Random Forest (50 trees)** | **$0.9935$** | **$0.9935$** | **$1.0000$** | **$0.9967$** | **$1.0000$** | `[1, 1; 0, 153]` |
| **Logistic Regression ($L_2$)** | **$0.9871$** | **$1.0000$** | **$0.9869$** | **$0.9934$** | **$1.0000$** | `[2, 0; 2, 151]` |
| **Majority Class Baseline** | $0.9871$ | $0.9871$ | $1.0000$ | $0.9935$ | N/A | `[0, 2; 0, 153]` (Fails on all lossless frames) |
| **Rule-Based Heuristic** | $0.1677$ | $0.9286$ | $0.1699$ | $0.2873$ | N/A | `[0, 2; 127, 26]` (Overly conservative) |

### 2.2 Real-World System Storage & Quality Tradeoff (155 Test Frames, 37.95 MB Uncompressed Raw)

| Compression Strategy | Compressed Total (MB) | Savings vs Raw | Savings vs Always Lossless | Mean SSIM | Mean PSNR | Critical Quality Failures |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Always Lossless** | $16.87\text{ MB}$ | $55.54\%$ | $0.00\%$ | $1.0000$ | $100.00\text{ dB}$ | 0 |
| **Always Lossy (JPEG 85)** | $3.50\text{ MB}$ | $90.77\%$ | $79.23\%$ | $0.9914$ | $42.37\text{ dB}$ | 0 |
| **Majority Baseline** | $3.50\text{ MB}$ | $90.77\%$ | $79.23\%$ | $0.9914$ | $42.37\text{ dB}$ | 0 |
| **Rule-Based Heuristic** | $14.41\text{ MB}$ | $62.03\%$ | $14.59\%$ | $0.9982$ | $90.24\text{ dB}$ | 0 |
| **Logistic Regression** | $4.20\text{ MB}$ | $88.95\%$ | $75.14\%$ | $0.9919$ | $43.85\text{ dB}$ | 0 |
| **Decision Tree** | **$3.46\text{ MB}$** | **$90.87\%$** | **$79.47\%$** | **$0.9915$** | **$43.05\text{ dB}$** | **0** |
| **Random Forest** | $3.49\text{ MB}$ | $90.79\%$ | $79.29\%$ | $0.9914$ | $42.68\text{ dB}$ | 0 |
| **Oracle Ground Truth** | **$3.46\text{ MB}$** | **$90.87\%$** | **$79.47\%$** | **$0.9915$** | **$43.05\text{ dB}$** | **0** |

**Key Takeaways**:
1. **Decision Tree achieves theoretical Oracle Upper Bound**: It matches Oracle Ground Truth decisions on all test frames, saving **$79.47\%$ memory over Always Lossless** ($16.87\text{ MB} \to 3.46\text{ MB}$) with **zero quality failures** and pristine mean SSIM ($0.9915$).
2. **Embedded Feasibility**: The Decision Tree has depth $d \le 4$ and requires only 4 branch comparisons per frame with zero matrix multiplications, taking $< 10\text{ microseconds}$ in firmware.
3. **Failure of Static Rules**: Handcrafted heuristics achieved only $14.59\%$ savings over lossless, leaving $65\%$ of available bandwidth savings unutilized.

---

## 3. Repository Structure

```
adaptive-compression/
├── README.md                           # Master project guide & reproduction instructions
├── requirements.txt                    # Python dependencies
├── configs/
│   └── config.yaml                     # Unified configuration (codecs, splits, thresholds, paths)
│
├── data/
│   ├── raw/                            # Preserved raw images (Caltech-101, Kodak, Stress)
│   ├── processed/                      # Cleaned, standardized 3-channel RGB PNG frames (1,030 images)
│   └── metadata/
│       ├── splits.csv                  # Exact 70% Train (721), 15% Val (154), 15% Test (155) splits
│       ├── image_features.csv          # 40 pre-compression features per frame
│       ├── compression_experiments.csv # 6,180 empirical compression trials across 6 codecs
│       ├── labels.csv                  # Full 21-column decision evidence audit trail
│       └── ml_dataset.csv              # Clean ML training dataset with zero leakage
│
├── src/
│   ├── data/                           # Multi-source dataset downloader and cleaner
│   ├── preprocessing/                  # Image loading, validation, and color space conversion
│   ├── color/                          # ITU-R BT.601 RGB <-> YUV color transformation
│   ├── features/                       # Modular pre-compression feature extraction (40 features)
│   ├── compression/                    # Codec wrappers (PNG, WebP-LL, JPEG) and benchmark runner
│   ├── dataset/                        # Deterministic split builder and ground-truth labeler
│   ├── evaluation/                     # Metrics (PSNR, SSIM), artifact analyzer, and system evaluator
│   ├── models/                         # ML models (Majority, Rule-Based, LogReg, DecisionTree, RF)
│   └── utils/                          # Visualizer and structured logging
│
├── scripts/
│   ├── 01_prepare_dataset.py           # Step 1-3: Generate deterministic stratified splits
│   ├── 02_run_compression_benchmark.py # Step 7-8: Multi-threaded rate-distortion benchmark (6,180 trials)
│   ├── 03_extract_features.py          # Step 5-6: Extract pre-compression features
│   ├── 04_generate_labels.py           # Step 9: Multi-criterion labeling & ml_dataset.csv generation
│   ├── 05_train_baselines.py           # Step 10: Train & evaluate classical baseline classifiers
│   ├── 06_evaluate_system.py           # Step 10: Evaluate system storage & quality tradeoff
│   └── run_pipeline.py                 # End-to-end automated pipeline runner
│
├── results/
│   ├── compression/
│   │   └── compression_results.csv     # Complete 6,180 trial compression benchmark records
│   ├── baseline/
│   │   ├── model_metrics.json          # Precision, Recall, F1, ROC-AUC across Train/Val/Test
│   │   └── test_predictions.json       # Model prediction vectors on held-out test split
│   ├── figures/
│   │   ├── class_distribution.png      # Class balance across Train, Val, and Test splits
│   │   ├── feature_distributions.png   # Feature boxplots separated by ground-truth label
│   │   ├── confusion_matrices.png      # Confusion matrix heatmaps for all baseline models
│   │   ├── feature_importances.png     # Gini feature importances from Random Forest
│   │   └── storage_quality_tradeoff.png# Real-world storage vs quality tradeoff visualization
│   └── system_evaluation.json          # System-level storage MB, savings %, and failure counts
│
├── tests/                              # Comprehensive test suite (38 automated unit & leakage tests)
│   ├── test_compression.py             # Bit-for-bit lossless and lossy size tests
│   ├── test_features.py                # Feature extraction unit and edge case tests
│   ├── test_leakage.py                 # Target leakage blacklist audit
│   ├── test_metrics.py                 # PSNR, SSIM, Dark-SSIM mathematical verification
│   ├── test_milestone1_steps7_10.py    # Multi-codec suite, labeler, and system evaluator tests
│   ├── test_models.py                  # Scikit-learn model wrapper and heuristic tests
│   ├── test_pipeline_steps.py          # Image loading, color conversion, feature tests
│   └── test_preprocessing.py           # Color space roundtrip and validation tests
│
└── docs/
    ├── MILESTONE_1_REPORT.md           # Comprehensive technical report for Samsung PRISM
    ├── COMPRESSION_EXPERIMENTS.md      # Rate-distortion & latency analysis (6,180 trials)
    ├── QUALITY_METRICS.md              # Mathematical formulations of quality metrics & LPIPS feasibility
    ├── LABEL_GENERATION.md             # Multi-criterion labeling rule & evidence retention
    ├── BASELINE_MODELS.md              # Classical ML baseline specifications & performance
    ├── FEATURE_DEFINITIONS.md          # 40 pre-compression feature definitions & formulae
    ├── DATASET.md                      # Dataset acquisition, cleaning, diversity, and manifest
    ├── DATA_LEAKAGE.md                 # Pre-compression purity & leakage audit
    ├── ASSUMPTIONS.md                  # Explicit engineering assumptions log
    └── MENTOR_QUESTIONS.md             # Formal open questions for Samsung mentors
```

---

## 4. Step-by-Step Reproduction Guide

### Environment Setup
```bash
git clone https://github.com/oshish/samsung-prism-adaptive-compression.git
cd samsung-prism-adaptive-compression

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run Entire Milestone 1 Pipeline End-to-End
```bash
python scripts/run_pipeline.py
```

### Or Run Step-by-Step
```bash
# Step 1-3: Generate deterministic stratified data splits (70% Train, 15% Val, 15% Test)
python scripts/01_prepare_dataset.py

# Step 7-8: Run multi-threaded rate-distortion compression benchmark across 1,030 images
python scripts/02_run_compression_benchmark.py --workers 8

# Step 5-6: Extract pre-compression features
python scripts/03_extract_features.py

# Step 9: Generate ground-truth labels and clean ml_dataset.csv
python scripts/04_generate_labels.py

# Step 10: Train and evaluate baseline ML models across Train, Val, and Test
python scripts/05_train_baselines.py

# Step 10: Run real-world system storage vs visual quality evaluation
python scripts/06_evaluate_system.py
```

### Run Test Suite (38 Tests Passing)
```bash
pytest tests/ -v
```

---

## 5. Formal Mentor Questions
Documented in detail in [`docs/MENTOR_QUESTIONS.md`](docs/MENTOR_QUESTIONS.md):
1. **Target Hardware Codec**: Does Samsung's target mobile architecture use proprietary ARM AFBC (ARM Frame Buffer Compression), ASTC, or standard JPEG/WebP pipelines?
2. **Quality Metric Cutoff**: Is $\text{SSIM} \ge 0.94$ / $\text{PSNR} \ge 33.0\text{ dB}$ acceptable to Samsung engineering, or is a stricter threshold (e.g. $\text{SSIM} \ge 0.96$) required?
3. **Multi-Quality vs Binary**: Should Milestone 2 predict continuous quality levels ($Q \in [50, 95]$) or remain binary?
