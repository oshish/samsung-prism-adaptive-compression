# Dataset Documentation: Benchmark Frame Collection

## Samsung PRISM Project — Worklet ID: 26VI11
**Adaptive Compression: Intelligent Frame Compression for Memory Optimization**  
**Department:** CSED  

---

## 1. Dataset Selection Rationale & Sources

To benchmark pre-compression feature extraction and subsequent adaptive compression decision systems, the dataset must exhibit genuine, unconstrained variation across visual and statistical dimensions relevant to compression (spatial frequency, edge density, dynamic range, texture, noise, and color saturation).

Rather than collecting unverified web images or creating an artificial binary split (e.g. 500 bright / 500 dark), we combine three complementary, established sources:

### Primary Source: Caltech-101 (Stratified Subsample)
- **Source:** California Institute of Technology (Fei-Fei et al., 2004). Canonical computer vision benchmark hosted on high-speed AWS S3 mirror (`https://s3.amazonaws.com/fast-ai-imageclas/caltech_101.tgz`).
- **Archive Size:** 131 MB total (9,145 images across 101 semantic categories + 1 diverse background category).
- **Sampling Strategy:** Stratified selection of 10 images per category across 101 categories ($\sim 1,010$ images).
- **Why Chosen:** Broad category coverage spanning natural objects, animals, vehicles, indoor tools, architectural scenes, vegetation, and diverse backgrounds. Provides realistic natural variations in lighting, contrast, textures, and edges.

### Secondary Source: Kodak Lossless True Color Image Suite
- **Source:** Canonical 24-image Kodak PhotoCD benchmark (`http://r0k.us/graphics/kodak/`).
- **Characteristics:** Uncompressed 24-bit RGB photographic scenes ($768 \times 512$ or $512 \times 768$).
- **Why Chosen:** Universally recognized standard in image compression research (used in JPEG, JPEG 2000, WebP, and learned neural compression benchmarks). Free from previous compression artifacts.

### Tertiary Source: Synthetic Compression Stress-Test Suite
- **Source:** Programmatically generated deterministic edge cases ($768 \times 512$).
- **Cases:**
  1. `stress_01_smooth_gradient`: Banding / contouring stress-test (challenging for lossy DCT; compact in lossless).
  2. `stress_02_dark_noisy`: Low-light frame ($Y < 40$) with additive Gaussian noise (sensor noise stress-test).
  3. `stress_03_dense_texture`: High-frequency sinusoids (challenging detail preservation).
  4. `stress_04_sharp_ui_graphics`: High-contrast vector text and lines (Gibbs ringing stress-test).
  5. `stress_05_clean_flat_poster`: Large uniform color blocks (ideal candidate for lossy/run-length).
  6. `stress_06_mixed_hdr`: Split dark shadow / bright highlight regions (extreme contrast stress-test).

---

## 2. Dataset Diversity Profile

The dataset spans all critical dimensions that impact image compressibility:
- **Brightness Spectrum:** Deep underexposure / shadows ($Y < 40$), balanced mid-tones, and bright near-saturation highlights ($Y > 215$).
- **Contrast:** Low-contrast hazy/foggy scenes to high dynamic range scenes with sharp tonal transitions.
- **Texture Density:** Smooth gradients and clean flat posters up to high-frequency textures (foliage, animal fur, woven cloth).
- **Edge Characteristics:** Soft natural transitions, organic curved boundaries, and razor-sharp geometric UI edges.
- **Noise Conditions:** Pristine lossless scans, real photographic sensor grain, and high-noise shadow environments.
- **Chromaticity:** Monochrome/low-saturation frames (where YUV chrominance $U/V$ is near-flat) to vibrant colorful objects with wide chromatic variance.

---

## 3. Automated Cleaning Pipeline

Raw files undergo a multi-stage automated validation process implemented in `src/data/cleaner.py`:
1. **File Integrity Verification:** Full bitstream decode check using Pillow `Image.open().load()`. Corrupted or truncated files are rejected with error logging.
2. **Exact Duplicate Elimination:** Cryptographic SHA-256 hash computed on file bytes. Identical files are logged and skipped.
3. **Perceptual Duplicate Elimination:** 64-bit difference hash (dHash) computed across adjacent horizontal gradients on downscaled luminance. Exact visual matches are eliminated.
4. **Dimension Anomaly Rejection:** Files with dimensions $< 32\text{ px}$ or aspect ratios $> 10:1$ are flagged and skipped.
5. **Color Channel Standardization:**
   - Grayscale images (1-channel `L` mode or identical $R=G=B$ planes) are standardized to 3-channel RGB arrays for uniform tensor handling, and tagged with `is_grayscale=True` in the metadata.
   - Alpha channels (`RGBA`) are composited over neutral 50% gray ($RGB = 128, 128, 128$) to eliminate 4-channel incompatibilities while avoiding contrast distortion.

All cleaning operations are recorded in `data/metadata/cleaning_log.csv`.

---

## 4. Preprocessing Principles (Non-Destructive)

- **Preservation of Raw Data:** `data/raw/` is treated as strictly read-only and preserved verbatim. Cleaned images are staged into `data/processed/`.
- **No Downsampling:** Images are **not** downsampled to low resolutions (e.g. 64x64). Compression characteristics are intimately tied to spatial frequency; downsampling acts as a destructive low-pass filter that eliminates fine edge ringing and high-frequency textures.
- **Native Resolutions:** Images retain their native dimensions ($\sim 300 \times 200$ to $768 \times 512$), perfectly reflecting typical embedded frame-buffer tiles.

---

## 5. Known Limitations

1. **Resolution Heterogeneity:** Because Caltech-101 and Kodak frames vary in native aspect ratio and dimensions, feature extraction times vary proportionally with total pixel count ($W \times H$).
2. **Natural vs Synthetic Ratio:** Approximately 97% of images are real-world photographs, with 6 targeted synthetic frames specifically testing codec failure modes.

---

## 6. Full Reproducibility Guide

Any researcher or student can reconstruct the entire dataset from scratch using the provided scripts:

```bash
# Step 1: Download & stage raw images (~1,040 images)
python scripts/download_dataset.py

# Steps 2 & 3: Clean, deduplicate, standardize, and output to data/processed/
python scripts/prepare_dataset.py

# Steps 4 & 5: Extract 32 pre-compression features to master CSV
python scripts/extract_features.py

# Step 6: Validate quality, generate statistics, and plot distributions
python scripts/validate_dataset.py
```

