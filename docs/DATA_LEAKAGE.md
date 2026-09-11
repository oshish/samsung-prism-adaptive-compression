# Data Leakage Prevention Guide

## Samsung PRISM Project — Worklet ID: 26VI11
**Adaptive Compression: Intelligent Frame Compression for Memory Optimization**  
**Department:** CSED  

---

## 1. Principle of Pre-Compression Feature Purity

The overarching objective of this project is to develop an intelligent decision system that evaluates an incoming raw/uncompressed image frame and determines whether to route it to **LOSSY** or **LOSSLESS** compression before compression occurs.

Consequently, any machine learning classifier or heuristic developed in later milestones must operate **strictly on information available prior to compression**.

> [!CAUTION]
> **Definition of Target / Data Leakage in Compression Decision Systems:**  
> Data leakage occurs whenever features extracted from the post-compression state (e.g., compressed byte count, compression runtime, reconstructed quality metrics, or empirical ground-truth labels) are included in the feature dataset or training representation. Doing so produces deceptively high model accuracy during training while rendering the model completely non-functional in real-time frame buffering systems.

---

## 2. Permitted vs. Strictly Prohibited Information

| Category | Status | Specific Metrics / Features | Scientific Rationale |
| :--- | :---: | :--- | :--- |
| **Basic Structure** | **ALLOWED** | `width`, `height`, `aspect_ratio`, `total_pixels` | Inherent frame dimensions known upon buffer allocation. |
| **Luminance & Contrast** | **ALLOWED** | `mean_luminance`, `std_luminance`, `min_luminance`, `max_luminance`, `median_luminance`, `dark_pixel_ratio`, `bright_pixel_ratio`, `luminance_range`, `rms_contrast`, `michelson_contrast` | Computed directly from original pixel values in $O(N)$ time. |
| **Histogram & Information** | **ALLOWED** | `p10_luminance`, `p90_luminance`, `iqr_luminance`, `shannon_entropy` | Measures distribution peakiness and theoretical memoryless source entropy before encoding. |
| **Spatial Details & Edges** | **ALLOWED** | `sobel_edge_density`, `mean_edge_magnitude`, `std_edge_magnitude`, `laplacian_variance` | First- and second-order spatial derivatives of uncompressed pixels. |
| **Texture & Local Variation**| **ALLOWED** | `local_variance_mean`, `local_variance_std`, `glcm_contrast`, `glcm_homogeneity` | 8x8 block-level variance and spatial co-occurrence in uncompressed domain. |
| **Noise Proxies** | **ALLOWED** | `noise_estimate` (Immerkaer filter), `dark_chroma_variance` | Fast spatial filtering proxy estimates of high-frequency disturbances. |
| **Color Spaces** | **ALLOWED** | `mean_r`, `mean_g`, `mean_b`, `std_r`, `std_g`, `std_b`, `mean_u`, `mean_v`, `std_u`, `std_v`, `colorfulness` | Color moments and chroma distribution in original sRGB/YUV planes. |
| **Target Decision Labels** | **STRICTLY PROHIBITED** | `label`, `decision`, `is_lossless`, `compression_target` | Ground truth belongs exclusively to later evaluation milestones after empirical codec experimentation. |
| **Compression Performance** | **STRICTLY PROHIBITED** | `compressed_size_bytes`, `compression_ratio`, `space_saving`, `bits_per_pixel (bpp)`, `encoding_time_ms` | Cannot be measured until codecs have already executed. |
| **Distortion / Quality Metrics**| **STRICTLY PROHIBITED** | `PSNR`, `SSIM`, `MS-SSIM`, `LPIPS`, `VMAF`, `delta_E` | Requires the decompressed reconstructed image; unavailable at decision time. |

---

## 3. Why Target Leakage Catastrophically Breaks the Engineering Goal

In an embedded camera or frame-buffer pipeline (e.g. Samsung mobile ISP or display processor):
1. An uncompressed frame arrives in memory.
2. The system has a strict budget (e.g., $< 5\text{ ms}$) to extract features and classify the frame.
3. If the decision requires running JPEG or PNG to observe the resulting file size or PSNR, the entire latency and energy purpose of adaptive compression is defeated: the system would have to perform both compressions simply to decide which one to use!
4. Therefore, our automated test suite includes a strict **Leakage Blacklist Audit** (`tests/test_leakage.py`) that scans the master feature CSV and extractor return schemas, failing immediately if any prohibited keyword appears.

---

## 4. Leakage Blacklist Keywords Monitored by CI/Tests

```python
LEAKAGE_BLACKLIST = [
    "label",
    "lossy",
    "lossless",
    "psnr",
    "ssim",
    "lpips",
    "vmaf",
    "ratio",
    "bpp",
    "compressed_size",
    "compressed_bytes",
    "saving",
    "delta_e",
    "codec_time"
]
```
The master feature CSV generated in Step 6 (`data/metadata/image_features.csv`) is verified 100% clean of all blacklist terms.

