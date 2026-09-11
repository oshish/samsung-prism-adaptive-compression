# Adaptive Frame Compression: Intelligent Frame Compression for Memory Optimization

**Samsung PRISM Student Project**  
**Worklet ID:** 26VI11  
**Department:** Computer Science & Engineering (CSED)  
**Team:** 3 Student Researchers  

---

> [!IMPORTANT]
> **Milestone Status — Steps 1–6 Complete:**  
> **This repository currently implements the dataset and feature extraction stage (Steps 1–6). Compression classification and machine learning models are not yet implemented.**  
> The current deliverable is a verified, diverse ~1,000-image dataset, standardized RGB/YUV representations, modular pre-compression feature extraction, master CSV, comprehensive validation reports, and tests.

---

## 1. Project Overview

Modern mobile display and camera pipelines process high-resolution frames under strict memory bandwidth, thermal, and battery constraints. The overarching objective of this Samsung PRISM project is to build an intelligent, low-latency framework that evaluates incoming raw uncompressed frames and determines the optimal compression strategy:
- **LOSSY Compression:** High size reduction with acceptable perceptual quality (e.g. for high-noise or natural texture scenes).
- **LOSSLESS Compression:** Perfect pixel reconstruction (e.g. for synthetic UI graphics, text, or high-contrast edge regions vulnerable to ringing/banding artifacts).

This milestone establishes the scientific foundation:
$$\text{Raw Image} \longrightarrow \text{Clean Dataset} \longrightarrow \text{RGB / YUV} \longrightarrow \text{Feature Extraction} \longrightarrow \text{Master CSV}$$

---

## 2. Repository Structure

```
adaptive-compression/
├── README.md                           # Project documentation and reproduction guide
├── requirements.txt                    # Project dependencies
├── .gitignore                          # Git ignore configuration
│
├── data/
│   ├── raw/                            # Preserved raw images (~1,040 images)
│   ├── processed/                      # Cleaned, standardized 3-channel RGB PNG frames
│   └── metadata/
│       ├── dataset_raw_manifest.csv    # Manifest of acquired raw images
│       ├── cleaning_log.csv            # Audit trail of all cleaning/deduplication actions
│       └── image_features.csv          # MASTER CSV: 32 pre-compression features per frame
│
├── src/
│   ├── data/
│   │   ├── downloader.py               # Reproducible multi-source dataset acquisition
│   │   └── cleaner.py                  # Integrity, duplicate detection (SHA-256/dHash), standardization
│   ├── preprocessing/
│   │   ├── image_loader.py             # Safe image loading and shape validation
│   │   └── color_space.py              # Compatibility re-export
│   ├── color/
│   │   └── color_space.py              # ITU-R BT.601 RGB <-> YUV color conversion
│   ├── features/
│   │   ├── brightness.py               # Luminance mean/std, dark/bright ratios
│   │   ├── contrast.py                 # Dynamic range, RMS contrast, Michelson contrast
│   │   ├── histogram.py                # Percentiles (p10, p90, IQR) & Shannon entropy
│   │   ├── edges.py                    # Sobel gradient, edge density, Laplacian variance
│   │   ├── texture.py                  # 8x8 block local variance & GLCM Haralick features
│   │   ├── noise.py                    # Immerkaer Laplacian noise proxy & dark chroma noise
│   │   ├── color.py                    # RGB/YUV channel moments & Hasler-Süsstrunk colorfulness
│   │   └── extractor.py                # Unified modular extract_features() interface
│   └── utils/
│       └── logger.py                   # Structured console/file logging
│
├── scripts/
│   ├── download_dataset.py             # Step 1: Download & stage raw images
│   ├── prepare_dataset.py              # Steps 2 & 3: Clean, deduplicate, and standardize images
│   ├── extract_features.py             # Steps 4 & 5: Run modular feature extraction to master CSV
│   └── validate_dataset.py             # Step 6: Automated sanity analysis, report & figures
│
├── results/
│   ├── dataset/
│   │   ├── dataset_validation_report.txt # Full cleaning and dataset integrity report
│   │   └── dataset_summary.json        # Machine-readable summary statistics
│   └── features/
│       ├── feature_summary_stats.csv   # Mean, std, median, skew, kurtosis per feature
│       ├── feature_distributions.png   # Multi-panel histogram distributions
│       └── correlation_matrix.png      # Feature correlation heatmap
│
├── tests/
│   ├── test_pipeline_steps.py          # Unit & edge case tests for Steps 1–6
│   ├── test_features.py                # Feature extraction unit tests
│   ├── test_preprocessing.py           # Image loading and color space tests
│   └── test_leakage.py                 # Strict target leakage blacklist audit
│
└── docs/
    ├── DATASET.md                      # Dataset sources, diversity, cleaning & reproducibility
    ├── FEATURE_DEFINITIONS.md          # Comprehensive feature dictionary & formulae
    ├── DATA_LEAKAGE.md                 # Pre-compression purity & target leakage prevention
    └── ASSUMPTIONS.md                  # Structured log of non-obvious engineering assumptions
```

---

## 3. Step-by-Step Reproduction Guide

### Environment Setup
```bash
# Clone the repository
cd adaptive-compression

# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Execution Pipeline (Steps 1–6)
```bash
# Step 1: Download ~1,000 diverse images from Caltech-101, Kodak, and Stress Suites
python scripts/download_dataset.py

# Steps 2 & 3: Clean, detect duplicates, and standardize to data/processed/
python scripts/prepare_dataset.py

# Steps 4 & 5: Extract 32 pre-compression features into data/metadata/image_features.csv
python scripts/extract_features.py

# Step 6: Validate dataset quality, generate statistics, and plot distributions
python scripts/validate_dataset.py
```

### Run Test Suite
```bash
pytest tests/ -v
```

---

## 4. Feature Summary (32 Attributes)

All features are extracted strictly from the uncompressed image before compression:

1. **Structural Metadata (4):** `width`, `height`, `aspect_ratio`, `total_pixels`
2. **Luminance & Brightness (7):** `mean_luminance`, `std_luminance`, `min_luminance`, `max_luminance`, `median_luminance`, `dark_pixel_ratio` ($Y < 40$), `bright_pixel_ratio` ($Y > 215$)
3. **Contrast & Dynamic Range (3):** `luminance_range`, `rms_contrast`, `michelson_contrast`
4. **Histogram & Information (4):** `p10_luminance`, `p90_luminance`, `iqr_luminance`, `shannon_entropy` ($H(Y)$ in bits/pixel)
5. **Edges & Sharpness (4):** `sobel_edge_density`, `mean_edge_magnitude`, `std_edge_magnitude`, `laplacian_variance`
6. **Texture & Spatial Activity (4):** `local_variance_mean` (8x8 blocks), `local_variance_std`, `glcm_contrast`, `glcm_homogeneity`
7. **Noise Proxies (2):** `noise_estimate` (Immerkaer filter), `dark_chroma_variance` (low-light chroma noise)
8. **Color Moments & Vibrancy (7):** `mean_r`, `mean_g`, `mean_b`, `std_r`, `std_g`, `std_b`, `mean_u`, `mean_v`, `std_u`, `std_v`, `colorfulness` (Hasler-Süsstrunk)

---

## 5. Zero Target Leakage Guarantee

As detailed in [`docs/DATA_LEAKAGE.md`](docs/DATA_LEAKAGE.md), the master feature dataset contains **strictly zero target leakage**:
- No compressed file sizes or compression ratios
- No rate-distortion metrics (PSNR, SSIM, LPIPS)
- No `LOSSY` or `LOSSLESS` ground-truth labels
- No codec execution runtimes

This guarantees that future machine learning models trained on this data will be valid for real-time inference prior to frame compression.
