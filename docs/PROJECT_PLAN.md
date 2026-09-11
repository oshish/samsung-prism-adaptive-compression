# Project Plan — Samsung PRISM: Adaptive Compression
**Worklet ID**: 26VI11 | **Department**: CSED | **Program**: Samsung PRISM  
**Project Title**: Adaptive Compression: Intelligent Frame Compression for Memory Optimization  
**Milestone Focus**: Milestone 1 (Weeks 4–7 Foundation)

---

## 1. Executive Summary & Objective
The goal of this project is to build an intelligent frame compression decision engine for memory-constrained environments (such as mobile frame buffers, camera ISPs, and display processors). For every incoming image frame, the system determines the optimal compression strategy:
$$\text{LOSSY} \quad \text{vs} \quad \text{LOSSLESS}$$
The objective function is:
$$\max \text{Storage Savings} \quad \text{subject to} \quad \text{Visual Quality} \ge \text{Acceptable Threshold}$$

Milestone 1 establishes the foundational engineering pipeline:
1. Verified RGB and YUV image preprocessing and validation.
2. Fast, pre-compression feature engineering (zero data leakage).
3. Empirical lossless vs lossy compression benchmarking (sizes, compression ratios, throughput).
4. Rigorous quality evaluation (PSNR, SSIM, low-light artifact and banding detection).
5. Configurable ground-truth label generation.
6. Baseline ML and heuristic classifiers.
7. Real-world system evaluation quantifying storage reduction vs quality preservation.

---

## 2. Team Division of Ownership (Team of 3 Students)

| Student | Core Technical Domain | Primary Modules & Responsibilities | Key Deliverables |
| :--- | :--- | :--- | :--- |
| **Person A** | **ML / DL & Feature Engineering** | `src/features/`<br>`src/models/` | Feature extraction pipeline (luminance, texture, GLCM, edges, noise, entropy), feature distribution analysis, baseline classifiers (Majority, Rule-based, Logistic Regression, Decision Tree, Random Forest), feature importance ranking. |
| **Person B** | **Image Processing & Compression Quality** | `src/preprocessing/`<br>`src/compression/`<br>`src/evaluation/` | Dual color-space engine (RGB ↔ YUV BT.601/BT.709), image validation, lossless (PNG, WebP-LL) and lossy (JPEG, WebP) codecs, rate-distortion benchmarking, PSNR & SSIM metrics, low-light and banding artifact analysis, LPIPS feasibility study. |
| **Person C** | **Dataset, Pipeline, Integration & Deployment** | `src/dataset/`<br>`scripts/`<br>`configs/`<br>`tests/` | Benchmark dataset acquisition (Kodak + edge-case suite), leakage-proof train/val/test splitting, ground-truth label generation engine, CLI workflow scripts, automated test suite (`pytest`), end-to-end integration and system-level memory evaluation. |

---

## 3. Milestone 1 Roadmap & Phases

```
[Phase 0: Architecture & Research] ──► [Phase 1: Environment & Config Setup]
                 │
                 ▼
[Phase 2: Dataset Acquisition & Splitting] ──► [Phase 3: RGB/YUV Preprocessing]
                 │
                 ▼
[Phase 4: Lossless vs Lossy Benchmarking] ──► [Phase 5: Quality & Artifact Metrics]
                 │
                 ▼
[Phase 6: Pre-Compression Feature Extraction] ──► [Phase 7: Ground-Truth Label Engine]
                 │
                 ▼
[Phase 8: Dataset Assembly & Leakage Audit] ──► [Phase 9: Baseline Model Training]
                 │
                 ▼
[Phase 10: System Storage & Quality Evaluation] ──► [Phase 11: End-to-End Pipeline & CLI]
                 │
                 ▼
[Phase 12: Comprehensive Tests, Documentation & Reverse-Learning Guides]
```

---

## 4. Technical Risks & Mitigation

| Technical Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Target Leakage** | Critical | Strict decoupling: all classifier inputs must be computed purely from the uncompressed raw frame. Compression sizes, quality scores, and labels are stored strictly as evaluation targets and asserted via `tests/test_leakage.py`. |
| **Arbitrary Quality Thresholds** | High | Abstract all decision thresholds into `configs/config.yaml`. Track all thresholds as `ASSUMPTION — REQUIRES MENTOR CONFIRMATION`. |
| **Low-Light / Dark Banding Artifacts** | High | Dedicated artifact analyzer computing localized dark-region SSIM ($Y < 40$) and edge gradient retention to prevent aggressive lossy quantization on banding-prone gradients. |
| **Small Benchmark Sample Bias** | Moderate | Supplement canonical Kodak natural images (24 frames) with 6 synthesized stress-test edge-case frames (pure gradients, extreme noise, dense foliage, sharp UI text). |
| **Runtime Overhead of Inference** | Moderate | Milestone 1 focuses on lightweight statistical features ($\mathcal{O}(N)$ passes) and shallow tree/linear baselines that can execute in milliseconds on mobile CPU. |
