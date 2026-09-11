# Learning Module 04: Image Quality Metrics & Artifact Analysis

## 1. What We Built
In `src/evaluation/metrics.py` and `src/evaluation/artifact_analyzer.py`, we implemented:
* **PSNR (Peak Signal-to-Noise Ratio)** in dB.
* **SSIM (Structural Similarity Index)** with multichannel support.
* **Dark-Region Quality Metrics** (localized PSNR and SSIM on $Y < 40$).
* **False-Contouring / Banding Detection** in smooth gradient regions.
* **Edge Energy Preservation** via Sobel gradient ratios.
* **LPIPS Feasibility Study** evaluating deep perceptual metrics vs runtime constraints.

## 2. Mathematical Foundations

### Mean Squared Error (MSE) & PSNR
$$\text{MSE} = \frac{1}{3 \cdot H \cdot W} \sum_{c=1}^3 \sum_{x=1}^W \sum_{y=1}^H (I(x, y, c) - \hat{I}(x, y, c))^2$$
$$\text{PSNR} = 10 \cdot \log_{10}\left(\frac{255^2}{\text{MSE}}\right) \quad (\text{dB})$$
* **Interpretation**: High PSNR ($> 35\text{ dB}$) indicates minimal numerical deviation. For identical images ($\text{MSE} = 0$), $\text{PSNR} = \infty$.
* **Limitation**: PSNR weights all pixel errors identically. A high-frequency textured error is imperceptible to humans, whereas a smooth gradient error of the same magnitude produces glaring visual banding.

### Structural Similarity Index (SSIM)
Measures structural degradation across luminance, contrast, and structural comparison:
$$\text{SSIM}(x, y) = \frac{(2\mu_x\mu_y + c_1)(2\sigma_{xy} + c_2)}{(\mu_x^2 + \mu_y^2 + c_1)(\sigma_x^2 + \sigma_y^2 + c_2)}$$
where $\mu$ is local mean, $\sigma$ is local standard deviation, $\sigma_{xy}$ is cross-covariance, $c_1 = (0.01 \cdot 255)^2$, and $c_2 = (0.03 \cdot 255)^2$.

### Dark-Region Artifact Metrics
Under low-light conditions, human contrast sensitivity follows the Weber-Fechner Law ($\Delta I / I = \text{constant}$). When $I$ is small (dark background), tiny intensity deviations $\Delta I$ are disproportionately visible.
* We compute localized $\text{SSIM}_{\text{dark}}$ strictly where $Y < 40$.

### Banding / False-Contouring Detection
Smooth continuous gradients exhibit non-zero, continuous gradient vectors. Aggressive lossy quantization collapses smooth ramps into stepped plateaus:
$$\text{Banding Score} = \frac{\text{Count}(\|\nabla I\| < 0.5 \text{ in smooth regions})}{\text{Total Smooth Pixels}}$$

## 3. LPIPS Feasibility Analysis
* **Why not real-time LPIPS?** LPIPS passes $256 \times 256$ patches through a deep neural network (e.g. AlexNet or VGG-16). This incurs $> 50\text{ ms}$ latency per frame and requires 50MB+ weights. In Milestone 1, SSIM and PSNR provide mathematically sound, microsecond-speed metrics. LPIPS is reserved for offline benchmark validation.

## 4. PRISM / Technical Interview Questions
1. *Q: Why can an image have high PSNR (e.g. 38 dB) but still look unacceptable to a human viewer?*  
   **A**: If the 38 dB error is concentrated along a single smooth sky gradient, it creates stark color banding steps that humans instantly spot. PSNR averages error across all pixels and masks localized perceptual artifacts.
2. *Q: How does SSIM differ from MSE?*  
   **A**: MSE measures absolute Euclidean distance between pixel intensities. SSIM normalizes for local luminance and contrast, isolating structural distortion (correlations in spatial patterns).
