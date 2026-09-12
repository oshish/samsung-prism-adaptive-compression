# Ground-Truth Label Generation & Dataset Engineering
**Project**: Samsung PRISM — Adaptive Compression: Intelligent Frame Compression for Memory Optimization  
**Worklet ID**: 26VI11 | **Department**: CSED | **Milestone**: 1 (Step 9)

---

## 1. Ground-Truth Formulation

The pre-compression decision system assigns one of two discrete operational modes to each incoming frame buffer:
* **`LOSSY` (Class 1)**: Lossy compression (JPEG, Q=85) achieves sufficient memory savings ($\ge 25\%$) while strictly satisfying visual quality requirements.
* **`LOSSLESS` (Class 0)**: Lossless compression (PNG / WebP Lossless) is required because lossy compression introduces objectionable visual degradation, fails dark shadow preservation, or yields insufficient memory reduction to justify the loss.

---

## 2. Multi-Criterion Decision Rule

An image is assigned the label `LOSSY` if and only if all four conditions are simultaneously satisfied:

$$\text{Label} = \begin{cases} 
\text{LOSSY} & \text{if } (\text{SSIM} \ge \tau_{\text{ssim}}) \land (\text{PSNR} \ge \tau_{\text{psnr}}) \land (\text{Dark-SSIM} \ge \tau_{\text{dark}}) \land (\Delta S \ge \tau_{\text{saving}}) \\ 
\text{LOSSLESS} & \text{otherwise} 
\end{cases}$$

### Experimental Thresholds (ASSUMPTION — Requires Mentor Confirmation)
The specific numerical thresholds configured in `configs/config.yaml` are:
1. **$\tau_{\text{ssim}} = 0.94$**: Structural similarity cutoff for imperceptible structural alteration on mobile screens.
2. **$\tau_{\text{psnr}} = 33.0\text{ dB}$**: High-fidelity signal-to-noise ratio cutoff.
3. **$\tau_{\text{dark}} = 0.90$**: Shadow preservation threshold in regions where luminance $Y < 40$.
4. **$\tau_{\text{saving}} = 0.25$ ($25\%$ size saving over lossless)**:
   $$\Delta S = \frac{S_{\text{lossless}} - S_{\text{lossy}}}{S_{\text{lossless}}}$$
   If lossy compression does not reduce compressed bytes by at least $25\%$ compared to lossless PNG, the quality compromise is unjustified, and the system reverts to `LOSSLESS`.

> [!NOTE]
> All four thresholds are marked as **ASSUMPTIONS** requiring formal review and confirmation by the Samsung PRISM mentors. They are fully parameterized in `configs/config.yaml`.

---

## 3. Decision Evidence Retention (`data/metadata/labels.csv`)
For transparency, explainability, and error analysis, the labeling pipeline outputs `labels.csv` containing complete decision evidence for each of the 1,030 images:

| Column | Type | Description |
| :--- | :--- | :--- |
| `image_id` | string | Unique frame identifier |
| `file_path` | string | Path to preprocessed image |
| `split` | string | Partition (`train`, `val`, `test`) |
| `raw_bytes` | int | Uncompressed 24-bit RGB byte count ($H \times W \times 3$) |
| `lossless_codec` | string | Reference lossless codec (`png`) |
| `lossless_bytes` | int | Compressed size using lossless codec |
| `lossless_cr` | float | Lossless compression ratio |
| `lossy_codec` | string | Evaluated lossy codec (`jpeg`) |
| `lossy_quality` | int | Evaluated lossy quality level (`85`) |
| `lossy_bytes` | int | Compressed size using lossy codec |
| `lossy_cr` | float | Lossy compression ratio |
| `size_saving_ratio` | float | Fractional byte reduction over lossless ($\Delta S$) |
| `psnr` | float | Peak signal-to-noise ratio (dB) |
| `ssim` | float | Structural similarity index |
| `dark_ssim` | float | Localized structural similarity for pixels with $Y < 40$ |
| `banding_score` | float | Quantization step / false contouring risk score |
| `quality_passed` | bool | Boolean flag: $\text{SSIM} \ge 0.94 \land \text{PSNR} \ge 33.0$ |
| `saving_passed` | bool | Boolean flag: $\Delta S \ge 0.25$ |
| `dark_passed` | bool | Boolean flag: $\text{Dark-SSIM} \ge 0.90$ |
| `label` | string | Categorical ground truth: `LOSSY` or `LOSSLESS` |
| `is_lossy_binary` | int | Integer target label: `1` (LOSSY) or `0` (LOSSLESS) |

---

## 4. Zero Target Leakage Enforcement (`data/metadata/ml_dataset.csv`)

A fundamental rule of machine learning in compression systems is **strict decoupling between pre-compression features and post-compression outcomes**:

* **Input Features ($X$)**: Must be computable strictly from the uncompressed frame buffer prior to compression (luminance, contrast, texture variance, edges, entropy, noise estimate).
* **Target Label ($y$)**: Derived empirically from compression experiments.
* **Leakage Blacklist**: Post-compression metrics (`compressed_bytes`, `compression_ratio`, `psnr`, `ssim`, `dark_ssim`, `size_saving_ratio`, `banding_score`, `quality_passed`, `saving_passed`, `dark_passed`, `raw_bytes`) are **strictly prohibited** from entering the feature matrix $X$.

The dataset builder enforces this by passing all feature columns through `TARGET_BLACKLIST` and running continuous verification via `tests/test_leakage.py`.
