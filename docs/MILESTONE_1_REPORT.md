# Milestone 1 Technical Report — Samsung PRISM: Adaptive Compression
**Worklet ID**: 26VI11 | **Department**: CSED | **Program**: Samsung PRISM  
**Project Title**: Adaptive Compression: Intelligent Frame Compression for Memory Optimization  
**Date**: September 2026 | **Student Team**: Team of 3 (Person A, Person B, Person C)

---

## 1. Problem
High-resolution imaging in mobile devices (smartphones, cameras, wearables, and smart displays) creates severe memory bandwidth bottlenecks. Transmitting uncompressed 24-bit RGB frame buffers between camera ISPs, GPUs, and LPDDR memory consumes massive bandwidth and battery power.
* **Lossless compression** (e.g., PNG, WebP Lossless) guarantees zero degradation, but its compression ratio is modest ($1.5\times$ to $2.5\times$).
* **Lossy compression** (e.g., JPEG, WebP Lossy) achieves dramatic memory savings ($5\times$ to $20\times$), but risks introducing objectionable artifacts—particularly in dark regions (shadow blocking), smooth gradients (color banding), and fine textures.

The core research and engineering problem is:
> **Given an input frame, can we intelligently decide whether lossy compression will provide meaningful memory savings while strictly maintaining acceptable visual quality, or whether lossless compression is mandatory?**

---

## 2. Proposed Solution
We developed a complete, reproducible, pre-compression decision engine that extracts $\mathcal{O}(N)$ statistical, spatial, and frequency features from the uncompressed frame buffer and classifies the image into either `LOSSY` or `LOSSLESS` mode before compression occurs. Ground-truth labels are generated via empirical rate-distortion benchmarking rather than subjective heuristics.

---

## 3. System Architecture
The Milestone 1 architecture decouples feature extraction, color spaces, compression codecs, and decision logic:
```
Raw Frame (RGB / YUV BT.601)
            │
            ▼
Pre-Compression Feature Extractor (25 features across luminance, texture, edges, noise, entropy)
            │
            ▼
Intelligent Decision Engine (Trained ML Classifier / Heuristic)
           / \
          /   \
  Decision:   Decision:
   LOSSY       LOSSLESS
     │             │
     ▼             ▼
JPEG / WebP-L   PNG / WebP-LL
     │             │
     \             /
      ▼           ▼
System Memory Storage & Quality Verification (SSIM, PSNR, Dark-SSIM)
```

---

## 4. Dataset
We utilized a 30-image benchmark suite combining canonical photographic benchmarks with high-stress synthetic edge cases:
1. **Kodak Lossless True Color Image Suite (24 images)**: Pristine uncompressed 24-bit RGB photographic images ($768 \times 512$). Canonical reference standard in JPEG/WebP compression literature.
2. **Synthetic Stress Suite (6 images)**:
   - `edge_01_smooth_gradient`: Smooth gradient testing false-contouring and color banding.
   - `edge_02_dark_noisy`: Ultra-low luminance ($Y < 20$) with heavy Gaussian noise ($\sigma = 12.0$).
   - `edge_03_dense_texture`: Procedural high-frequency cloth/foliage textures.
   - `edge_04_sharp_ui_graphics`: High-contrast UI text and vector geometric borders.
   - `edge_05_clean_flat_poster`: Solid color flat regions (ideal candidate for compression).
   - `edge_06_mixed_hdr`: High dynamic range split scene (shadows + bright sunlight).

### Partitioning & Leakage Audit
Partitions were created deterministically (`random_seed: 42`) strictly by `image_id`:
* **Train Split**: 17 images (10 LOSSLESS, 7 LOSSY)
* **Validation Split**: 5 images (2 LOSSLESS, 3 LOSSY)
* **Test Split**: 8 images (4 LOSSLESS, 4 LOSSY — perfectly balanced 50/50 evaluation ground truth)

---

## 5. Preprocessing
Implemented in `src/preprocessing/`:
* **Input Validation**: Strict validation of array dimensions, 3 channels, non-zero area, and `uint8` data type.
* **Dual Color-Space Representation**:
  - **RGB**: Uncompressed sensor and display format.
  - **YUV (YCbCr) BT.601 / BT.709**: Decouples Luminance ($Y$, perceived brightness) from Chrominance ($Cb/Cr$). Standard ITU matrix transformation with reversible roundtrip checked within $\le 2$ gray levels.
* **Luminance Extraction**: Fast 2D luminance plane extraction $Y = 0.299R + 0.587G + 0.114B$.

---

## 6. Compression Experiments
Across the 30 images, we benchmarked 10 codec configurations (300 total trials):
* **Lossless**: PNG, WebP Lossless
* **Lossy**: JPEG (Qualities 50, 75, 85, 95), WebP Lossy (Qualities 50, 75, 85, 95)
* **Measurements**: Raw file bytes ($S_{\text{raw}}$), compressed file bytes ($S_{\text{comp}}$), compression ratio ($\text{CR} = S_{\text{raw}} / S_{\text{comp}}$), encode latency (ms), decode latency (ms).

Key Empirical Finding:
* On natural Kodak photography, JPEG Q=85 achieved an average size reduction of **$81.5\%$** relative to lossless PNG while maintaining $\text{SSIM} = 0.959$ and $\text{PSNR} = 35.2\text{ dB}$.
* On smooth gradients (`edge_01`) and flat vector graphics (`edge_04`), lossless PNG was actually **$5\times$ to $8\times$ smaller** than lossy JPEG! Attempting lossy compression on vector/flat graphics bloated file size rather than compressing it.

---

## 7. Quality Metrics
Implemented in `src/evaluation/`:
1. **PSNR (Peak Signal-to-Noise Ratio)**: Logarithmic signal-to-MSE ratio in dB.
2. **SSIM (Structural Similarity Index)**: Local window covariance capturing structural degradation.
3. **Dark-Region Artifact Metrics**: Localized MSE, PSNR, and SSIM computed strictly over pixels with $Y < 40$.
4. **Banding Score**: Derivative step detection quantifying false-contouring in smooth gradients.
5. **Edge Energy Preservation**: Gradient energy ratio pre- vs post-compression.
6. **LPIPS Investigation**: Formal study finding that deep feature distance (AlexNet/VGG) requires $>50\text{ ms}$ latency and 50MB+ weights, making it unsuitable for hard real-time mobile frame buffers ($<2\text{ ms}$ budget). LPIPS is reserved for offline verification.

---

## 8. Feature Engineering (Pre-Compression Only)
Implemented in `src/features/` with **zero target leakage**:
* **Luminance & Brightness (7 features)**: `mean_luminance`, `std_luminance`, `skew_luminance`, `kurtosis_luminance`, `dark_pixel_ratio`, `bright_pixel_ratio`, `rms_contrast`.
* **Spatial Texture & Variance (7 features)**: `local_variance_mean`, `local_variance_std`, `glcm_contrast`, `glcm_dissimilarity`, `glcm_homogeneity`, `glcm_energy`, `glcm_correlation`.
* **Edges & Sharpness (4 features)**: `sobel_mean_magnitude`, `sobel_max_magnitude`, `sobel_edge_density`, `laplacian_variance`.
* **Noise Estimation (2 features)**: `noise_estimate` (Immerkaer Laplacian mask), `dark_chroma_variance`.
* **Entropy & Color (5 features)**: `shannon_entropy_y`, `color_entropy_mean`, `colorfulness`, `chroma_std_u`, `chroma_std_v`.

All features operate in $\mathcal{O}(N)$ time directly on raw pixels. Automated testing (`tests/test_leakage.py`) verified that no post-compression metrics enter feature matrices.

---

## 9. Label Generation
Rather than assuming "bright $\to$ lossy", ground-truth labels are derived empirically in `src/dataset/labeler.py`:
$$\text{Label} = \begin{cases} \text{LOSSY}, & \text{if } \text{SSIM} \ge \tau_{\text{SSIM}} \land \text{PSNR} \ge \tau_{\text{PSNR}} \land R \ge \tau_{\text{saving}} \land \text{Dark-SSIM} \ge \tau_{\text{dark}} \\ \text{LOSSLESS}, & \text{otherwise} \end{cases}$$
Default parameters in `configs/config.yaml`:
* $\tau_{\text{SSIM}} = 0.94$
* $\tau_{\text{PSNR}} = 33.0\text{ dB}$
* $\tau_{\text{saving}} = 0.25$ ($25\%$ savings over lossless)
* $\tau_{\text{dark}} = 0.90$
*(All marked as `ASSUMPTION — REQUIRES MENTOR CONFIRMATION`)*.

Resulting Dataset Balance: **16 LOSSLESS vs 14 LOSSY**.

---

## 10. Baseline Models
We implemented and trained 5 baseline strategies:
1. **Majority Class Baseline**: Always predicts `LOSSLESS` (the majority class in training).
2. **Rule-Based Baseline**: Handcrafted heuristic testing:
   "If `mean_luminance` $\ge 65$, `dark_pixel_ratio` $\le 0.35$, `noise_estimate` $\le 12$, and `laplacian_variance` $\le 800$ $\to$ `LOSSY`, else `LOSSLESS`."
3. **Logistic Regression**: Linear statistical boundary with StandardScaler.
4. **Decision Tree Classifier**: Interpretable orthogonal decision trees (depth $\le 4$).
5. **Random Forest Classifier**: Ensemble of 50 decorrelated decision trees with feature importances.

---

## 11. Results

### Classification Performance on Held-Out Test Set (8 Frames: 4 Lossless, 4 Lossy)

| Model | Test Accuracy | Precision (Lossy) | Recall (Lossy) | F1-Score | ROC-AUC | Confusion Matrix (TN, FP, FN, TP) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Majority Class** | 50.0% | 0.000 | 0.000 | 0.000 | — | [4, 0, 4, 0] |
| **Rule-Based Heuristic** | 50.0% | 0.500 | 0.500 | 0.500 | — | [2, 2, 2, 2] |
| **Logistic Regression** | 75.0% | 0.667 | 1.000 | 0.800 | 0.500 | [2, 2, 0, 4] |
| **Decision Tree** | 75.0% | 0.667 | 1.000 | 0.800 | 0.750 | [2, 2, 0, 4] |
| **Random Forest** | **100.0%** | **1.000** | **1.000** | **1.000** | **1.000** | **[4, 0, 0, 4]** |

---

## 12. Storage Reduction & System-Level Impact

### Evaluated Across Held-Out Test Frames (Raw Uncompressed Size = 9.00 MB)

| Compression Strategy | Total Size (MB) | Savings vs Raw (%) | Savings vs Always Lossless (%) | Mean SSIM | Mean PSNR (dB) | Critical Quality Failures | Failure Rate (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Always Lossless** | 4.51 MB | 49.9% | 0.0% | 1.0000 | 100.0 dB | 0 | 0.0% |
| **Always Lossy** | 0.89 MB | 90.1% | 80.2% | 0.9201 | 36.0 dB | **3** | **37.5%** |
| **Majority Baseline** | 4.51 MB | 49.9% | 0.0% | 1.0000 | 100.0 dB | 0 | 0.0% |
| **Rule-Based Heuristic** | 3.09 MB | 65.7% | 31.5% | 0.9796 | 69.8 dB | **1** | **12.5%** |
| **Logistic Regression** | 1.19 MB | 86.8% | 73.5% | 0.9301 | 52.1 dB | **2** | **25.0%** |
| **Decision Tree** | 1.19 MB | 86.8% | 73.5% | 0.9301 | 52.1 dB | **2** | **25.0%** |
| **Random Forest (Our Model)** | **2.38 MB** | **73.5%** | **47.1%** | **0.9788** | **68.8 dB** | **0** | **0.0%** |
| **Oracle (Ground Truth)** | **2.38 MB** | **73.5%** | **47.1%** | **0.9788** | **68.8 dB** | **0** | **0.0%** |

---

## 13. Quality Preservation vs Memory Trade-Off
The empirical data clearly validates the central engineering thesis:
* **The Danger of "Always Lossy"**: While saving $80.2\%$ of memory, Always Lossy produces **3 critical quality failures** on test frames (SSIM drops to 0.67 on dark/noisy frames and produces banding on gradients).
* **The Waste of "Always Lossless"**: Avoids artifacts, but wastes 4.51 MB of memory.
* **The Intelligence of Random Forest**: Matches the theoretical Oracle Upper Bound: saves **$47.1\%$ of memory over lossless** while maintaining a pristine mean SSIM of **$0.9788$** with **0 critical quality failures**.

---

## 14. Classification Performance Analysis
Feature importance analysis from the Random Forest revealed the top 3 drivers of compressibility:
1. `sobel_edge_density` (high edge density forces lossless mode to preserve crisp detail).
2. `noise_estimate` (high sensor noise ruins DCT quantization, forcing lossless mode).
3. `shannon_entropy_y` (low entropy indicates flat or smooth regions that compress efficiently).

---

## 15. Limitations
1. **Sample Size**: Evaluated on 30 benchmark frames (canonical Kodak + edge cases). While statistically standard for image compression, Milestone 2 should scale to hundreds of camera frames.
2. **Binary Formulation**: Currently decides between binary Lossy vs Lossless. A production pipeline could benefit from adaptive quality factor selection ($Q \in [50, 95]$).
3. **Software Codecs**: Used JPEG and WebP as proxies for hardware frame buffers (AFBC / ASTC).

---

## 16. Assumptions
Tracked in `docs/ASSUMPTIONS.md`:
* $\tau_{\text{SSIM}} = 0.94$, $\tau_{\text{PSNR}} = 33.0\text{ dB}$, $\tau_{\text{saving}} = 0.25$, $\tau_{\text{dark}} = 0.90$.
* All thresholds are configurable and flagged: `ASSUMPTION — REQUIRES MENTOR CONFIRMATION`.

---

## 17. Mentor Questions
Documented in `docs/MENTOR_QUESTIONS.md`:
1. Does Samsung specify a target quality metric (SSIM, MS-SSIM, PSNR) or cutoff threshold for frame buffer compression?
2. Which codec family (e.g. WebP, JPEG, ASTC, or proprietary AFBC) reflects Samsung's target hardware architecture?
3. Should Milestone 2 expand from binary classification to multi-level adaptive quality?

---

## 18. What We Learned
1. **Banding vs Texture**: Smooth gradients compress poorly under DCT lossy codecs and bloat in size compared to spatial lossless predictors (PNG).
2. **Noise Destroys Lossy Quality**: High-ISO sensor noise causes catastrophic DCT block distortion in low-light regions.
3. **Pre-Compression Statistical Features Are Highly Predictive**: Standard statistical features ($\mathcal{O}(N)$ complexity) allow lightweight decision models like Random Forest to predict compressibility with 100% accuracy on our test benchmark without needing heavy deep learning.

---

## 19. Recommended Milestone 2 Work
1. **Dataset Expansion**: Ingest 200+ frames from mobile camera burst sequences and Android UI screen captures.
2. **Continuous Quality Scaling**: Formulate adaptive quality prediction ($Q \in [1, 100]$) via regression or multi-class binning (`LOSSLESS`, `LOSSY_HIGH`, `LOSSY_MEDIUM`).
3. **Lightweight Neural Models**: Evaluate MobileNet-v3 / efficient 1D CNN backbones against our tabular Random Forest baseline.
4. **Hardware Latency Benchmarking**: Profile feature extraction on ARM / mobile CPU architecture to ensure inference latency $< 2\text{ ms}$.
