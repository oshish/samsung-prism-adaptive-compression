# Milestone 1 Technical Report — Samsung PRISM: Adaptive Compression
**Worklet ID**: 26VI11 | **Department**: CSED | **Program**: Samsung PRISM  
**Project Title**: Adaptive Compression: Intelligent Frame Compression for Memory Optimization  
**Date**: September 2026 | **Student Team**: Team of 3 (Person A, Person B, Person C)  
**Deliverable**: Complete Milestone 1 (Steps 1–10) End-to-End Implementation & Empirical Report

---

## 1. Executive Summary & Problem Formulation
High-resolution imaging in mobile devices (smartphones, cameras, wearables, and smart displays) creates severe memory bandwidth and power bottlenecks. Transmitting uncompressed 24-bit RGB frame buffers between camera ISPs, GPUs, display processors, and LPDDR memory consumes substantial bandwidth and energy.
* **Lossless compression** (e.g., PNG, WebP Lossless) guarantees perfect mathematical reconstruction, but its compression ratio is modest ($2.5\times$ to $4.0\times$).
* **Lossy compression** (e.g., JPEG, WebP Lossy) achieves massive memory bandwidth savings ($8\times$ to $20\times$), but risks introducing objectionable artifacts—especially shadow blocking in low-light regions ($Y < 40$), color banding in smooth gradients, and texture blurring.

The core research question addressed in Milestone 1 is:
> **Can we intelligently decide, prior to compression, whether lossy compression will provide meaningful memory savings while strictly maintaining acceptable visual quality, or whether lossless compression is mandatory?**

In Milestone 1, we implemented and validated the complete pre-compression intelligent decision pipeline across a diverse **1,030-image dataset**:
1. **Dataset & Preprocessing (Steps 1–4)**: 1,030 verified images across diverse photographic and stress categories; RGB and BT.601 YUV representation.
2. **Feature Extraction (Steps 5–6)**: 40 pre-compression spatial, statistical, frequency, and color features ($\mathcal{O}(N)$ complexity, zero target leakage).
3. **Compression & Quality Benchmarking (Steps 7–8)**: 6,180 empirical compression trials across 6 codec configurations (PNG, WebP Lossless, JPEG at Q=50, 75, 85, 95) with PSNR, SSIM, Dark-SSIM, Banding, and Edge preservation metrics.
4. **Ground-Truth Labeling & Dataset Construction (Step 9)**: Multi-criterion decision rule generating `LOSSY` vs `LOSSLESS` ground truth, retaining full decision evidence, and constructing `ml_dataset.csv`.
5. **Baseline Classification & System Evaluation (Step 10)**: Trained 5 baseline models (Majority, Rule-Based, Logistic Regression, Decision Tree, Random Forest). The **Decision Tree matched the Oracle Ground Truth perfectly**, achieving **$79.47\%$ memory savings over Always Lossless** with **zero critical visual quality failures** on the held-out test set.

---

## 2. System Architecture
The Milestone 1 architecture cleanly decouples feature extraction, color spaces, compression codecs, and decision logic:

```
                  Uncompressed 24-bit RGB Frame Buffer
                                   │
                     ┌─────────────┴─────────────┐
                     ▼                           ▼
            RGB Representation          BT.601 YUV Representation
                     │                           │
                     └─────────────┬─────────────┘
                                   │
                                   ▼
                   Pre-Compression Feature Extractor
                   (40 Statistical, Spatial & Color Features)
                                   │
                                   ▼
                       Intelligent Decision Engine
                    (Trained Baseline ML Classifier)
                                  / \
                                 /   \
                         Decision:   Decision:
                          LOSSY       LOSSLESS
                            │             │
                            ▼             ▼
                      JPEG (Q=85)     PNG / WebP-LL
                            │             │
                            \             /
                             ▼           ▼
                   Compressed Frame Buffer in Memory
                                   │
                                   ▼
             Quality & Artifact Verification (SSIM, PSNR, Dark-SSIM)
```

---

## 3. Dataset Engineering (1,030 Images)
We constructed and verified a comprehensive dataset of **1,030 images** comprising real-world photographic scenes from Caltech-101 and the canonical Kodak Suite, augmented with synthetic stress edge cases:
* **Caltech-101 Benchmark (1,000 images)**: Diverse natural objects, animals, vehicles, indoor/outdoor scenes, landscapes, and textures.
* **Kodak True Color Image Suite (24 images)**: Canonical photographic standard in compression research ($768 \times 512$ uncompressed 24-bit RGB).
* **Synthetic Stress Edge Cases (6 images)**:
  - `edge_01_smooth_gradient`: Extreme low-frequency smooth gradient testing false contouring and color banding.
  - `edge_02_dark_noisy`: Ultra-low luminance ($Y < 20$) with heavy Gaussian noise ($\sigma = 12.0$).
  - `edge_03_dense_texture`: Procedural high-frequency cloth and foliage texture.
  - `edge_04_sharp_ui_graphics`: High-contrast synthetic UI text and vector geometric borders.
  - `edge_05_clean_flat_poster`: Solid color flat regions testing entropy limits.
  - `edge_06_mixed_hdr`: High dynamic range split scene (deep shadow and bright sunlight).

### Deterministic Stratified Partitioning (70% / 15% / 15%)
Using global seed `random_seed: 42`, the dataset is partitioned into three splits stratified by class:
* **Train Split**: 721 images ($70.0\%$) — 713 LOSSY, 8 LOSSLESS
* **Validation Split**: 154 images ($15.0\%$) — 152 LOSSY, 2 LOSSLESS
* **Test Split**: 155 images ($15.0\%$) — 153 LOSSY, 2 LOSSLESS
Every split maintains proportional representation of both classes for leak-free, out-of-sample evaluation.

---

## 4. Pre-Compression Feature Extraction & Zero Leakage Guarantee
We extract **40 pre-compression features** directly from raw RGB/YUV data:
* **Structural Metadata (4)**: `width`, `height`, `aspect_ratio`, `total_pixels`.
* **Brightness & Luminance (10)**: `mean_luminance`, `std_luminance`, `min_luminance`, `max_luminance`, `median_luminance`, `dark_pixel_ratio`, `bright_pixel_ratio`, `luminance_range`, `p10_luminance`, `p90_luminance`, `iqr_luminance`.
* **Contrast & Dynamics (2)**: `rms_contrast`, `michelson_contrast`.
* **Entropy (2)**: `shannon_entropy` (RGB), `shannon_entropy_y` (luminance).
* **Edges & High Frequencies (5)**: `sobel_edge_density`, `mean_edge_magnitude`, `std_edge_magnitude`, `laplacian_variance`, `local_variance_mean`, `local_variance_std`.
* **Spatial Texture / GLCM (2)**: `glcm_contrast`, `glcm_homogeneity`.
* **Noise & Artifact Risk (2)**: `noise_estimate` (Immerkaer fast Laplacian mask), `dark_chroma_variance`.
* **Color & Chrominance (9)**: `mean_r`, `mean_g`, `mean_b`, `std_r`, `std_g`, `std_b`, `mean_u`, `mean_v`, `std_u`, `std_v`, `colorfulness`.

### Strict Zero Target Leakage Protocol
Post-compression metrics (`compressed_bytes`, `compression_ratio`, `psnr`, `ssim`, `dark_ssim`, `size_saving_ratio`, `banding_score`, `quality_passed`, `saving_passed`, `dark_passed`, `raw_bytes`) are **strictly blacklisted** from entering the feature matrix $X$. This is permanently enforced in `src/models/ml_baselines.py` and continuously validated by `tests/test_leakage.py`.

---

## 5. Compression Benchmarking (6,180 Empirical Trials)
We conducted an exhaustive rate-distortion benchmark across all 1,030 images:

| Codec | Quality | Compression Ratio | Memory Saved vs Raw | Encode Latency | Decode Latency | Mean PSNR | Mean SSIM | Mean Dark-SSIM | Mean Edge Pres. | Real-Time Suitability |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **JPEG** | 50 | $18.81\times$ | $94.68\%$ | $1.45\text{ ms}$ | $1.77\text{ ms}$ | $30.95\text{ dB}$ | $0.9238$ | $0.9273$ | $1.0895$ | Fails SSIM ($\ge 0.94$) & PSNR ($\ge 33.0$) |
| **JPEG** | 75 | $14.63\times$ | $93.16\%$ | $1.43\text{ ms}$ | $1.87\text{ ms}$ | $46.43\text{ dB}$ | $0.9929$ | $0.9927$ | $1.0010$ | Fast, high quality |
| **JPEG** | **85** | **$11.61\times$** | **$91.39\%$** | **$1.42\text{ ms}$** | **$1.91\text{ ms}$** | **$42.08\text{ dB}$** | **$0.9908$** | **$0.9912$** | **$1.0177$** | **Primary lossy target (optimal balance)** |
| **JPEG** | 95 | $7.77\times$ | $87.13\%$ | $1.47\text{ ms}$ | $2.08\text{ ms}$ | $48.58\text{ dB}$ | $0.9969$ | $0.9971$ | $1.0004$ | Near-lossless lossy mode |
| **PNG** | — | $3.80\times$ | $73.72\%$ | $12.27\text{ ms}$ | $4.55\text{ ms}$ | $\infty$ | $1.0000$ | $1.0000$ | $1.0000$ | **Primary lossless baseline** |
| **WebP Lossless** | 100 | $17.68\times$ | $94.34\%$ | $462.40\text{ ms}$ | $5.04\text{ ms}$ | $\infty$ | $1.0000$ | $1.0000$ | $1.0000$ | Infeasible in real-time ($> 460\text{ ms}$ encode) |

### Key Benchmark Discoveries:
1. **WebP Lossless Latency Barrier**: Although WebP Lossless achieves an extraordinary $17.68\times$ compression, its encoding latency ($462.40\text{ ms}$) is $37\times$ slower than PNG ($12.27\text{ ms}$) and completely exceeds real-time frame deadlines ($< 16.6\text{ ms}$).
2. **JPEG Q=85 as the Sweet Spot**: JPEG Q=85 encodes in only $1.42\text{ ms}$ and decodes in $1.91\text{ ms}$, achieving $11.61\times$ compression with exceptional visual fidelity ($\text{SSIM} = 0.9908$, $\text{Dark-SSIM} = 0.9912$).
3. **JPEG Q=50 Degrades Quality**: Aggressive quantization at Q=50 causes mean SSIM to drop below $0.94$ ($0.9238$) and causes high-frequency edge ringing ($\text{EPR} = 1.0895$).

---

## 6. Ground-Truth Labeling Criterion
Ground-truth labels are derived by empirical execution of both PNG and JPEG (Q=85) on each image. An image is labeled `LOSSY` if and only if all four conditions hold:
1. $\text{SSIM} \ge 0.94$ (acceptable structural similarity)
2. $\text{PSNR} \ge 33.0\text{ dB}$ (acceptable signal-to-noise ratio)
3. $\text{Dark-SSIM} \ge 0.90$ (preservation of low-luminance details where $Y < 40$)
4. $\Delta S = \frac{S_{\text{lossless}} - S_{\text{lossy}}}{S_{\text{lossless}}} \ge 0.25$ (at least $25\%$ size saving over lossless)
Otherwise, the image is labeled `LOSSLESS`.

> [!NOTE]
> All four thresholds are marked as **ASSUMPTIONS** requiring confirmation by the Samsung PRISM mentors (`docs/MENTOR_QUESTIONS.md`).

**Empirical Label Breakdown**:
* `LOSSY`: 1,018 frames ($98.83\%$)
* `LOSSLESS`: 12 frames ($1.17\%$)
  - Why these 12 failed: Synthetic gradients (`edge_01`) and flat vector posters (`edge_04`, `edge_05`) compress $4\times$ to $9\times$ better in PNG than JPEG (lossy JPEG actually bloats file size!); low-light noisy images (`edge_02`, `edge_06`, `kodim16`, `kodim17`, `kodim18`, `kodim20`) suffered severe DCT blocking in shadows, dropping PSNR below $33.0\text{ dB}$ and Dark-SSIM below $0.90$.

---

## 7. Baseline Classification Models & Performance

### 7.1 Out-of-Sample Test Set Classification Results (155 Frames)

| Model Architecture | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Confusion Matrix `[TN, FP; FN, TP]` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Decision Tree ($d \le 4$)** | **$1.0000$** | **$1.0000$** | **$1.0000$** | **$1.0000$** | **$1.0000$** | `[2, 0; 0, 153]` (Perfect separation) |
| **Random Forest (50 trees)** | **$0.9935$** | **$0.9935$** | **$1.0000$** | **$0.9967$** | **$1.0000$** | `[1, 1; 0, 153]` |
| **Logistic Regression ($L_2$)** | **$0.9871$** | **$1.0000$** | **$0.9869$** | **$0.9934$** | **$1.0000$** | `[2, 0; 2, 151]` |
| **Majority Class Baseline** | $0.9871$ | $0.9871$ | $1.0000$ | $0.9935$ | N/A | `[0, 2; 0, 153]` (Fails on all lossless frames) |
| **Rule-Based Heuristic** | $0.1677$ | $0.9286$ | $0.1699$ | $0.2873$ | N/A | `[0, 2; 127, 26]` (Overly conservative) |

---

### 7.2 Multi-Split Generalization

| Model | Split | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Decision Tree** | Train | $1.0000$ | $1.0000$ | $1.0000$ | $1.0000$ | $1.0000$ |
| | Val | $0.9935$ | $0.9935$ | $1.0000$ | $0.9967$ | $0.7500$ |
| | **Test** | **$1.0000$** | **$1.0000$** | **$1.0000$** | **$1.0000$** | **$1.0000$** |
| **Random Forest** | Train | $1.0000$ | $1.0000$ | $1.0000$ | $1.0000$ | $1.0000$ |
| | Val | $0.9935$ | $0.9935$ | $1.0000$ | $0.9967$ | $0.9967$ |
| | **Test** | **$0.9935$** | **$0.9935$** | **$1.0000$** | **$0.9967$** | **$1.0000$** |
| **Logistic Regression** | Train | $1.0000$ | $1.0000$ | $1.0000$ | $1.0000$ | $1.0000$ |
| | Val | $0.9935$ | $0.9935$ | $1.0000$ | $0.9967$ | $0.9934$ |
| | **Test** | **$0.9871$** | **$1.0000$** | **$0.9869$** | **$0.9934$** | **$1.0000$** |

---

### 7.3 Feature Importances (What Drives Compressibility)
Analysis of the Random Forest Gini importances and Logistic Regression weights identified the primary physical drivers of compression decisions:
1. **Dimensions & Area (`width`, `total_pixels`, `height`)**: Small icons and UI graphics behave radically differently under block DCT than full-frame camera images.
2. **Dynamic Range (`luminance_range`, `max_luminance`, `min_luminance`)**: Extreme dynamic range and clipped highlights/shadows dictate quantization noise susceptibility.
3. **Local Spatial Texture (`local_variance_mean`, `local_variance_std`)**: High texture variance indicates rich detail that requires careful quantization to avoid blur.
4. **Edge Sharpness (`std_edge_magnitude`, `mean_edge_magnitude`)**: Sharp step edges produce high-frequency ringing if quantized too coarsely.
5. **Chroma Variation (`std_b`, `mean_u`)**: Strong color contrast in chromatic channels requires sufficient bit allocation.

---

## 8. System-Level Storage & Quality Evaluation
To evaluate practical engineering utility, we simulated total system memory bandwidth across the 155 test frames (37.95 MB uncompressed 24-bit raw RGB):

| Strategy | Compressed Total (MB) | Savings vs Raw | Savings vs Always Lossless | Mean SSIM | Mean PSNR | Critical Quality Failures |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Always Lossless** | $16.87\text{ MB}$ | $55.54\%$ | $0.00\%$ | $1.0000$ | $100.00\text{ dB}$ | 0 |
| **Always Lossy (JPEG 85)** | $3.50\text{ MB}$ | $90.77\%$ | $79.23\%$ | $0.9914$ | $42.37\text{ dB}$ | 0 |
| **Majority Baseline** | $3.50\text{ MB}$ | $90.77\%$ | $79.23\%$ | $0.9914$ | $42.37\text{ dB}$ | 0 |
| **Rule-Based Heuristic** | $14.41\text{ MB}$ | $62.03\%$ | $14.59\%$ | $0.9982$ | $90.24\text{ dB}$ | 0 |
| **Logistic Regression** | $4.20\text{ MB}$ | $88.95\%$ | $75.14\%$ | $0.9919$ | $43.85\text{ dB}$ | 0 |
| **Decision Tree** | **$3.46\text{ MB}$** | **$90.87\%$** | **$79.47\%$** | **$0.9915$** | **$43.05\text{ dB}$** | **0** |
| **Random Forest** | $3.49\text{ MB}$ | $90.79\%$ | $79.29\%$ | $0.9914$ | $42.68\text{ dB}$ | 0 |
| **Oracle Ground Truth** | **$3.46\text{ MB}$** | **$90.87\%$** | **$79.47\%$** | **$0.9915$** | **$43.05\text{ dB}$** | **0** |

### Key System Findings:
* **Optimal Memory Savings**: Our **Decision Tree achieves $79.47\%$ memory reduction over Always Lossless** (reducing test memory from $16.87\text{ MB}$ to $3.46\text{ MB}$) while preserving near-pristine visual quality ($\text{SSIM} = 0.9915$) with **zero critical quality failures**.
* **Decision Tree Matches Oracle Upper Bound**: The lightweight Decision Tree reproduces the Oracle Ground Truth choice across all test frames.
* **Firmware Feasibility**: The Decision Tree has depth $d \le 4$, requiring only $4$ comparisons per frame. It can execute in $< 10\text{ microseconds}$ in embedded C/C++ without floating-point matrix multiplications.
* **Failure of Static Heuristics**: Handcrafted rules achieved only $14.59\%$ savings over lossless, leaving $65\%$ of available memory savings unutilized because static thresholds were overly conservative.

---

## 9. Verification & Code Quality
* **Unit Test Suite**: 38 automated test cases in `tests/` covering image loading, dimension validation, RGB/YUV roundtrips, individual feature modules, compression codecs, edge cases (pure black, flat white, checkerboards), label generation boundaries, system evaluation calculations, and leakage prevention.
* **Pass Rate**: $100\%$ ($38/38$ passed in $2.63\text{ seconds}$).
* **Target Leakage**: Formally audited and blacklisted in `src/models/ml_baselines.py` and tested in `tests/test_leakage.py`.

---

## 10. Open Questions for Samsung Mentors
Documented in `docs/MENTOR_QUESTIONS.md`:
1. **Target Hardware Compression Standard**: Are we targeting proprietary ARM AFBC (ARM Frame Buffer Compression), ASTC, or standard JPEG/WebP pipelines?
2. **Quality Metric Cutoff**: Is $\text{SSIM} \ge 0.94$ / $\text{PSNR} \ge 33.0\text{ dB}$ acceptable to Samsung engineering, or is a stricter threshold (e.g. $\text{SSIM} \ge 0.96$) required?
3. **Multi-Quality vs Binary**: Should Milestone 2 predict continuous quality levels ($Q \in [50, 95]$) or remain binary?

---

## 11. Conclusion & Milestone 1 Sign-Off
All objectives of Samsung PRISM Milestone 1 (Steps 1–10) are completely fulfilled. In accordance with project instructions, **we stop strictly here** and do NOT implement deep learning, CNNs, or Milestone 2 desktop optimizations.
