# Project Assumptions and Engineering Decisions

## Samsung PRISM Project — Worklet ID: 26VI11
**Adaptive Compression: Intelligent Frame Compression for Memory Optimization**  
**Department:** CSED  

---

## 1. Structured Assumption Log

### ASSUMPTION 1: Color Space Standard
- **ASSUMPTION:** ITU-R BT.601 is used as the default color space transformation matrix from sRGB to YUV (YCbCr).
- **WHY:** ITU-R BT.601 is the standard color representation utilized by classic image/video codecs including standard JPEG (JFIF), MPEG-2, and standard-definition video buffering.
- **CURRENT CHOICE:** Formula: $Y = 0.299R + 0.587G + 0.114B$, $U = -0.168736R - 0.331264G + 0.5B + 128$, $V = 0.5R - 0.418688G - 0.081312B + 128$.
- **RISK:** Modern high-definition displays (HDTV/UHD) often employ ITU-R BT.709 or BT.2020 matrices with different luma weighting ($0.2126R + 0.7152G + 0.0722B$).
- **FUTURE VALIDATION:** Benchmark feature sensitivity between BT.601 and BT.709 representations on wide-gamut display frames in later milestones.

---

### ASSUMPTION 2: Dark and Bright Pixel Cutoff Thresholds
- **ASSUMPTION:** Dark pixels are defined as $Y < 40.0$ (~15.7% intensity) and bright pixels as $Y > 215.0$ (~84.3% intensity) on an 8-bit scale $[0, 255]$.
- **WHY:** Shadow regions with $Y < 40$ are where sensor shot/thermal noise is most prominent and where human vision perceives quantization contouring (banding) most acutely due to Weber's contrast law. Highlight regions with $Y > 215$ correspond to near-saturation where clipping and high-contrast Gibbs ringing occur.
- **CURRENT CHOICE:** Fixed constants $40.0$ and $215.0$.
- **RISK:** Thresholds may not adapt optimally to HDR (10-bit/12-bit) content or high dynamic range displays.
- **FUTURE VALIDATION:** Perform ablation analysis during model training to test if adaptive percentiles (e.g. bottom 10% vs top 10%) yield higher classification utility than fixed intensity cutoffs.

---

### ASSUMPTION 3: Local Block Variance Partitioning (8x8 Grid)
- **ASSUMPTION:** Spatial local variance is computed across non-overlapping $8 \times 8$ pixel patches.
- **WHY:** The $8 \times 8$ partition matches the canonical discrete cosine transform (DCT) block size in JPEG and baseline MPEG compression.
- **CURRENT CHOICE:** Non-overlapping $8 \times 8$ blocks with boundary reflection padding.
- **RISK:** Modern codecs (HEIF, AVIF, WebP, VVC) utilize variable transform blocks ranging from $4 \times 4$ up to $64 \times 64$.
- **FUTURE VALIDATION:** Evaluate multi-scale local variance ($4 \times 4$, $8 \times 8$, $16 \times 16$) if future models target multi-resolution block codecs.

---

### ASSUMPTION 4: Noise Estimator as Empirical Proxy
- **ASSUMPTION:** The Immerkaer (1996) fast pseudo-Laplacian filter is employed as a noise proxy rather than ground-truth noise.
- **WHY:** Uncompressed single frames arrive without clean reference ground truth. The Immerkaer mask provides an $O(N)$ spatial convolution estimate of high-frequency disturbance.
- **CURRENT CHOICE:** 3x3 pseudo-Laplacian convolution on luminance channel.
- **RISK:** Extremely dense, high-frequency regular textures (e.g., fine fabric, wire mesh, halftone patterns) produce high filter responses that simulate noise.
- **FUTURE VALIDATION:** Compare Immerkaer proxy against wavelet-based median absolute deviation (MAD) estimators and patch-based PCA noise estimators.

---

### ASSUMPTION 5: Non-Destructive Preprocessing & Resolution Preservation
- **ASSUMPTION:** Images are not downsampled to small uniform dimensions (e.g. 64x64 or 128x128).
- **WHY:** Downsampling acts as a low-pass spatial filter that irreversibly destroys high-frequency textures, edge sharpness, and sensor noise patterns—the exact characteristics that determine whether lossy compression produces objectionable artifacts.
- **CURRENT CHOICE:** Original native resolutions (~300x200 to 768x512) are preserved verbatim.
- **RISK:** Variable resolutions result in variable feature extraction runtimes per frame.
- **FUTURE VALIDATION:** Measure feature extraction latency vs resolution trade-offs if strict real-time deadlines ($< 2\text{ ms}$) are imposed on hardware targets.

---

### ASSUMPTION 6: Handling of Grayscale and Alpha Channels
- **ASSUMPTION:** Grayscale images are converted to 3-channel RGB with identical planes ($R=G=B$) and tagged with an `is_grayscale=True` flag. Alpha channels are composited over a neutral 50% gray background ($RGB = 128, 128, 128$).
- **WHY:** The downstream feature extractor and eventual ML models expect uniform 3-channel input arrays. Neutral gray compositing prevents edge-contrast artifacts that occur when compositing over pure black or white.
- **CURRENT CHOICE:** Automatic standardization in `clean_and_validate_dataset()`.
- **RISK:** Compositing modifies edge contrast around transparent boundaries.
- **FUTURE VALIDATION:** For UI graphics with alpha transparency, evaluate whether alpha should be encoded as a 4th channel in a dedicated RGBA compression path.

---

### ASSUMPTION 7: Separation of Feature Extraction from Classification (Zero Target Leakage)
- **ASSUMPTION:** No lossy or lossless compression experiments are run, and no `LOSSY` / `LOSSLESS` ground-truth labels are created at this stage.
- **WHY:** Ground truth must be established empirically by measuring compression ratio and objective quality (PSNR/SSIM) trade-offs across multiple codecs. Labeling images prior to empirical testing violates scientific methodology and introduces target leakage.
- **CURRENT CHOICE:** Stop strictly after Step 6 (dataset, preprocessing, RGB/YUV, features, CSV, validation, tests, and documentation).
- **RISK:** None. Preserves absolute scientific and methodological purity.
- **FUTURE VALIDATION:** Next milestone will execute empirical compression benchmarks (JPEG, WebP, PNG, QOI) to compute rate-distortion trade-offs and assign objective labels.
