# Project Assumptions — Samsung PRISM: Adaptive Compression
**Worklet ID**: 26VI11 | **Department**: CSED | **Milestone**: 1

> [!WARNING]
> No assumption in this document is treated as an established fact. Every parameter listed below is an engineering hypothesis designed to make the Milestone 1 pipeline executable, testable, and configurable. All items marked as requiring mentor confirmation will be submitted to the Samsung PRISM mentor during our initial review.

---

### Assumption 1: Acceptable Perceptual Quality Threshold ($\tau_{\text{SSIM}}$ and $\tau_{\text{PSNR}}$)
* **ASSUMPTION**: An image compressed using a lossy codec maintains "acceptable quality" if its Structural Similarity Index satisfies $\text{SSIM} \ge 0.95$ and Peak Signal-to-Noise Ratio satisfies $\text{PSNR} \ge 34.0\text{ dB}$.
* **WHY IT WAS NEEDED**: To formulate ground-truth binary labels ($\text{LOSSY}$ vs $\text{LOSSLESS}$) empirically, the pipeline requires an explicit numerical quality constraint.
* **CURRENT CHOICE**: $\tau_{\text{SSIM}} = 0.95$, $\tau_{\text{PSNR}} = 34.0\text{ dB}$ (configured in `configs/config.yaml`).
* **RISK**: If the actual Samsung deployment requires higher fidelity (e.g., $\text{SSIM} \ge 0.98$ for camera post-processing) or allows lower fidelity (e.g., $\text{SSIM} \ge 0.90$ for low-priority UI buffers), the ground truth labels will shift.
* **HOW TO VERIFY**: Conduct subjective visual inspection across diverse images; perform rate-distortion sweeps across quality levels; verify against mentor feedback.
* **WHETHER MENTOR CONFIRMATION IS REQUIRED**: **YES — CRITICAL**.

---

### Assumption 2: Minimum Storage Saving Threshold ($\tau_{\text{saving}}$)
* **ASSUMPTION**: Lossy compression is only justified if it achieves at least a 25% file-size reduction compared to lossless compression:
  $$\frac{S_{\text{lossless}} - S_{\text{lossy}}}{S_{\text{lossless}}} \ge 0.25$$
* **WHY IT WAS NEEDED**: If a lossy codec achieves high visual quality but only saves 2% or 5% memory relative to lossless, risking irreversible lossy quantization is unjustified in a memory subsystem.
* **CURRENT CHOICE**: $\tau_{\text{saving}} = 0.25$ (25% reduction).
* **RISK**: High-noise or high-entropy images might achieve 10%–20% savings without visible artifacts, which a 25% threshold would force into lossless mode.
* **HOW TO VERIFY**: Measure memory bandwidth savings and total memory consumption across benchmark suites under different saving cutoffs (15%, 25%, 35%).
* **WHETHER MENTOR CONFIRMATION IS REQUIRED**: **YES**.

---

### Assumption 3: Dark-Region Sensitivity & Artifact Protection ($\tau_{\text{dark}}$)
* **ASSUMPTION**: Dark regions ($Y < 40$) suffer disproportionate visual degradation due to human contrast sensitivity (Weber-Fechner effect) and DCT block quantization, requiring a dedicated localized metric $\text{SSIM}_{\text{dark}} \ge 0.92$.
* **WHY IT WAS NEEDED**: An image with a bright center and dark background can achieve an overall global $\text{SSIM} > 0.96$ even when the dark regions exhibit severe blockiness and false contouring.
* **CURRENT CHOICE**: $\text{SSIM}_{\text{dark}} \ge 0.92$ evaluated on pixels with luminance $Y < 40$.
* **RISK**: A strict dark-region threshold may force nocturnal images to always use lossless compression, limiting memory savings.
* **HOW TO VERIFY**: Targeted artifact visual inspection and false-contouring detection on dark test frames.
* **WHETHER MENTOR CONFIRMATION IS REQUIRED**: **YES**.

---

### Assumption 4: Representative Baseline Codecs
* **ASSUMPTION**: Standard modern formats—JPEG (DCT lossy) and WebP (VP8 lossy / VP8L lossless) alongside PNG (DEFLATE lossless)—provide representative proxies for memory subsystem compression behavior.
* **WHY IT WAS NEEDED**: Specialized proprietary hardware codecs (e.g. ARM AFBC, Samsung proprietary frame buffer compression, ASTC) are closed-source or hardware-specific. Standard software codecs allow reproducible, cross-platform algorithmic development.
* **CURRENT CHOICE**: Lossless = PNG, WebP Lossless; Lossy = JPEG, WebP Lossy at quality 75.
* **RISK**: The rate-distortion curves of proprietary hardware codecs may differ from JPEG/WebP.
* **HOW TO VERIFY**: Review Samsung PRISM worklet documentation and request clarification on targeted hardware codecs.
* **WHETHER MENTOR CONFIRMATION IS REQUIRED**: **YES**.

---

### Assumption 5: Dual Color-Space Transformation (RGB vs YUV BT.601)
* **ASSUMPTION**: Raw frame buffers can be analyzed in both RGB (for display/sensor compatibility) and ITU-R BT.601 YCbCr (for luminance/chrominance decoupling).
* **WHY IT WAS NEEDED**: The human eye responds differently to luminance vs chrominance; lossy compression relies heavily on chroma subsampling.
* **CURRENT CHOICE**: Preprocessing supports direct RGB and reversible YCbCr (BT.601) representations.
* **RISK**: Modern camera sensors and displays may use Rec.709 or Rec.2020 matrices.
* **HOW TO VERIFY**: Codebase provides modular matrix conversion so switching to Rec.709 is a one-line configuration toggle.
* **WHETHER MENTOR CONFIRMATION IS REQUIRED**: **NO** (architectural flexibility accommodates any ITU standard).

---

### Assumption 6: Binary Formulation for Milestone 1
* **ASSUMPTION**: The compression decision is strictly binary ($\text{LOSSY}$ vs $\text{LOSSLESS}$) rather than continuous (selecting quality $Q \in [1, 100]$) for Milestone 1.
* **WHY IT WAS NEEDED**: Directly mandated by the Samsung PRISM project specifications for Milestone 1.
* **CURRENT CHOICE**: Binary classification target.
* **RISK**: In production, multi-level adaptive compression (e.g. Lossless, Lossy-95, Lossy-75, Lossy-50) may offer better memory optimization.
* **HOW TO VERIFY**: Discuss multi-level or regression formulation with mentor for Milestone 2.
* **WHETHER MENTOR CONFIRMATION IS REQUIRED**: **CONFIRMED FOR M1** (to be revisited in Milestone 2).
