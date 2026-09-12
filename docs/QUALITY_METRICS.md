# Quality & Artifact Evaluation Metrics Specification
**Project**: Samsung PRISM — Adaptive Compression: Intelligent Frame Compression for Memory Optimization  
**Worklet ID**: 26VI11 | **Department**: CSED | **Milestone**: 1 (Steps 8 & 9)

---

## 1. Overview & Evaluation Philosophy
Evaluating visual quality in mobile display and camera frame buffer compression requires balancing two competing objectives:
1. **Mathematical Reconstruction Accuracy**: Global pixel-level fidelity ($L_2$ error norm).
2. **Perceptual Degradation & Artifact Resistance**: Preservation of structural geometry, edge sharpness, low-luminance details (shadows), and smooth continuous gradients.

In this project, we implement and benchmark five quantitative quality metrics:
* **PSNR (Peak Signal-to-Noise Ratio)**: Global logarithmic signal-to-noise ratio in decibels (dB).
* **SSIM (Structural Similarity Index)**: 3-channel perceptual structural fidelity measuring luminance, contrast, and structural correlation.
* **Localized Dark-SSIM ($Y < 40$)**: Localized structural similarity restricted to dark shadow regions to catch severe DCT blocking and false contouring.
* **Banding Risk Score**: Gradient plateau detector measuring false contouring and quantization steps across smooth gradients.
* **Edge Preservation Ratio**: Gradient energy retention measuring edge blurring ($< 1.0$) vs high-frequency ringing ($> 1.0$).
* **LPIPS Feasibility Analysis**: Evaluation of deep feature perceptual distance for real-time mobile frame buffer pipelines.

---

## 2. Mathematical Formulations

### 2.1 Peak Signal-to-Noise Ratio (PSNR)
Given an original frame $I_{\text{orig}}$ and reconstructed frame $I_{\text{comp}}$ of size $H \times W \times C$:
$$\text{MSE} = \frac{1}{H \cdot W \cdot C} \sum_{y=1}^{H} \sum_{x=1}^{W} \sum_{c=1}^{C} \left( I_{\text{orig}}(x, y, c) - I_{\text{comp}}(x, y, c) \right)^2$$

$$\text{PSNR} = 10 \cdot \log_{10}\left( \frac{\text{MAX}_I^2}{\text{MSE}} \right) = 20 \cdot \log_{10}\left( \frac{255.0}{\sqrt{\text{MSE}}} \right)$$

* For identical images ($\text{MSE} = 0$), $\text{PSNR} \to \infty$ (handled as $100.0\text{ dB}$ in numeric reporting).
* **Threshold Benchmark**: $\text{PSNR} \ge 33.0\text{ dB}$ indicates acceptable mobile display fidelity without overt compression distortion.

---

### 2.2 Structural Similarity Index (SSIM)
SSIM compares local patterns of pixel intensities normalized for luminance and contrast:
$$\text{SSIM}(x, y) = \frac{(2\mu_x\mu_y + C_1)(2\sigma_{xy} + C_2)}{(\mu_x^2 + \mu_y^2 + C_1)(\sigma_x^2 + \sigma_y^2 + C_2)}$$

* $\mu_x, \mu_y$: Local sample means using an $11 \times 11$ Gaussian weighting window ($\sigma = 1.5$).
* $\sigma_x^2, \sigma_y^2$: Local sample variances.
* $\sigma_{xy}$: Local covariance between original and compressed patches.
* $C_1 = (K_1 L)^2, C_2 = (K_2 L)^2$ with $K_1 = 0.01, K_2 = 0.03, L = 255$.
* Range: $[-1.0, 1.0]$, where $1.0$ is identical structural fidelity.
* **Threshold Benchmark**: $\text{SSIM} \ge 0.94$.

---

### 2.3 Localized Dark-SSIM (Shadow Artifact Protection)
Human vision exhibits non-linear sensitivity (Weber-Fechner Law / Stevens' Power Law). In dark shadows ($Y < 40$), standard 8-bit JPEG DCT quantization discards high-order AC coefficients, producing severe block boundaries and contour steps that are glaringly noticeable when viewing on OLED screens.

**Definition**:
1. Compute BT.601 luminance: $Y = 0.299 R + 0.587 G + 0.114 B$.
2. Form shadow mask: $M_{\text{dark}}(x, y) = \mathbb{I}(Y(x, y) < 40.0)$.
3. Compute full SSIM pixel map $\text{SSIM}_{\text{map}}(x, y)$.
4. Extract localized score:
$$\text{Dark-SSIM} = \frac{1}{|M_{\text{dark}}|} \sum_{(x,y) \in M_{\text{dark}}} \text{SSIM}_{\text{map}}(x, y)$$

* If $|M_{\text{dark}}| < 50$ pixels, the frame has negligible shadow regions, returning $\text{Dark-SSIM} = 1.0$ (no shadow risk).
* **Threshold Benchmark**: $\text{Dark-SSIM} \ge 0.90$.

---

### 2.4 Banding Risk Score (False-Contouring Detector)
Under heavy quantization, smooth continuous gradients (sky, vignettes, solid backgrounds) degenerate into stepped staircase plateaus:
1. Compute horizontal and vertical Sobel gradients: $G_x = \text{Sobel}_x(Y), G_y = \text{Sobel}_y(Y), G = \sqrt{G_x^2 + G_y^2}$.
2. Identify smooth regions: $M_{\text{smooth}} = \mathbb{I}(G < 15.0)$.
3. Count flat quantized steps within smooth areas:
$$\text{Banding Score} = \frac{\sum_{(x,y) \in M_{\text{smooth}}} \mathbb{I}(G(x, y) < 0.5)}{|M_{\text{smooth}}|}$$
* Range: $[0.0, 1.0]$. A score $> 0.25$ indicates severe false contouring risk.

---

### 2.5 Edge Preservation Ratio
Quantifies high-frequency energy retention across edges:
$$\text{EPR} = \frac{\sum_{x,y} \|\nabla I_{\text{comp}}(x, y)\|}{\sum_{x,y} \|\nabla I_{\text{orig}}(x, y)\|}$$
* $\text{EPR} \approx 1.0$: Ideal edge fidelity.
* $\text{EPR} < 0.90$: Noticeable blurring / softening of sharp text or textures.
* $\text{EPR} > 1.10$: Unwanted high-frequency noise or ringing artifacts.

---

## 3. LPIPS Feasibility Analysis for Mobile Frame Buffer Pipelines

| Evaluation Dimension | Traditional Fast Metrics (PSNR / SSIM / Dark-SSIM) | Learned Perceptual Metric (LPIPS) |
| :--- | :--- | :--- |
| **Computational Complexity** | $\mathcal{O}(N)$ integer / float arithmetic | Deep CNN forward pass (AlexNet / VGG backbone) |
| **Model Size / Weights** | 0 MB (pure mathematical operations) | 50 MB – 100 MB weights file |
| **Dependencies** | NumPy, SciPy, Pillow | PyTorch, TorchVision, CUDA / Metal / NPU runtime |
| **Latency per 1080p Frame** | $\approx 1.2\text{ ms}$ (CPU multi-core) | $\approx 45\text{ ms} - 120\text{ ms}$ (Mobile GPU/NPU) |
| **Real-Time Buffer Budget** | Fits within $\le 2\text{ ms}$ frame deadline | Exceeds real-time mobile display refresh budget by $20\times-60\times$ |
| **Suitability** | **Primary metric for real-time pre-compression decision engine** | **Strictly offline evaluation and rate-distortion benchmarking in Milestone 2** |

### Conclusion & Recommendation
For Milestone 1, **PSNR, SSIM, and Dark-SSIM** are the authoritative evaluation metrics for ground-truth labeling and runtime system trade-off. LPIPS is reserved for offline validation studies.
