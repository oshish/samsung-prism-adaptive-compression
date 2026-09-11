# Feature Definitions and Engineering Rationale

## Samsung PRISM Project — Worklet ID: 26VI11
**Adaptive Compression: Intelligent Frame Compression for Memory Optimization**  
**Department:** CSED  

---

## 1. Feature Architecture Overview

The pre-compression feature extraction pipeline produces **32 columns** per image (4 structural metadata attributes + 28 numerical visual characteristics). All features are extracted strictly from the uncompressed image in **sRGB** and **ITU-R BT.601 YUV (YCbCr)** color spaces before any compression decision or codec execution.

---

## 2. Comprehensive Feature Definition Table

| Feature Name | Category | Channel | Mathematical Definition / Algorithm | Why It Matters for Compression Decision | Known Limitations / Edge Cases |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **`width`** | Structural | Metadata | Image width in pixels ($W$) | Determines spatial resolution; affects codec block partitioning and memory footprint. | Non-square aspect ratios may require padding in block transforms. |
| **`height`** | Structural | Metadata | Image height in pixels ($H$) | Frame vertical extent; combined with width gives total uncompressed buffer size. | Interlacing or padding considerations in video/frame codecs. |
| **`aspect_ratio`** | Structural | Metadata | $\frac{W}{H}$ | Identifies non-standard wide/tall aspect ratios. | Can become extreme on panoramic crops. |
| **`total_pixels`** | Structural | Metadata | $W \times H$ | Total uncompressed pixel count ($N$); governs uncompressed raw byte footprint ($3N$). | Does not capture spatial frequency content. |
| **`mean_luminance`** | Luminance | Y | $\mu_Y = \frac{1}{N} \sum_{i} Y_i$ | Human eye sensitivity is highest in mid-tones; governs perceptual distortion visibility. | Fails to distinguish a flat gray frame from a mixed black-and-white frame. |
| **`std_luminance`** | Luminance | Y | $\sigma_Y = \sqrt{\frac{1}{N} \sum_i (Y_i - \mu_Y)^2}$ | Global contrast spread; high $\sigma_Y$ indicates wide dynamic range across the scene. | Sensitive to global illumination outliers. |
| **`min_luminance`** | Luminance | Y | $\min_i (Y_i)$ | Identifies presence of pure black pixels ($0$) or shadow floor. | Sensitive to single defective/black pixels. |
| **`max_luminance`** | Luminance | Y | $\max_i (Y_i)$ | Identifies presence of saturated highlight pixels ($255$). | Sensitive to specular highlights/hot pixels. |
| **`median_luminance`** | Luminance | Y | $\text{Median}(Y)$ | Robust central tendency, invariant to extreme shadow/highlight outliers. | Computational sort required ($O(N \log N)$). |
| **`dark_pixel_ratio`** | Luminance | Y | $\frac{1}{N} \sum_i \mathbb{I}(Y_i < 40.0)$ | Low-light regions where lossy quantizers produce visible blocking and chroma noise blotches. | Cutoff threshold ($40.0$) is conventional/experimental. |
| **`bright_pixel_ratio`** | Luminance | Y | $\frac{1}{N} \sum_i \mathbb{I}(Y_i > 215.0)$ | Highlights prone to clipping and ringing around saturated edges. | Cutoff threshold ($215.0$) is conventional/experimental. |
| **`luminance_range`** | Contrast | Y | $\max(Y) - \min(Y)$ | Full dynamic range span of the luminance channel. | Can be dominated by two isolated extreme pixels. |
| **`rms_contrast`** | Contrast | Y | $\frac{\sigma_Y}{\mu_Y + \epsilon}$ | Root-Mean-Square contrast; standard psychophysical contrast metric normalized by mean brightness. | Unstable when mean luminance approaches zero (stabilized via $\epsilon = 10^{-6}$). |
| **`michelson_contrast`** | Contrast | Y | $\frac{Y_{\max} - Y_{\min}}{Y_{\max} + Y_{\min} + \epsilon}$ | Standard contrast metric for periodic patterns and gratings. | Bound to $[0, 1]$; can saturate on high-dynamic scenes. |
| **`p10_luminance`** | Histogram | Y | 10th percentile of $Y$ | Shadow boundary marker; more robust than minimum. | Discrete percentile estimate. |
| **`p90_luminance`** | Histogram | Y | 90th percentile of $Y$ | Highlight boundary marker; more robust than maximum. | Discrete percentile estimate. |
| **`iqr_luminance`** | Histogram | Y | $p_{75} - p_{25}$ | Interquartile range; robust measure of statistical dispersion. | Ignores extreme tail behavior. |
| **`shannon_entropy`** | Histogram / Info | Y | $-\sum_{k=0}^{255} p(k) \log_2 p(k)$ | Information entropy of luminance histogram in bits/pixel. Sets the theoretical limit for 1st-order lossless entropy coding. | Assumes memoryless source (ignores 2D spatial pixel correlations). |
| **`sobel_edge_density`**| Edges | Y | $\frac{1}{N} \sum_i \mathbb{I}(\|\nabla Y\|_i > 30.0)$ | Proportion of pixels containing sharp spatial gradients. High edge density triggers ringing under lossy DCT. | Fixed threshold ($30.0$) may overcount high-frequency noise. |
| **`mean_edge_magnitude`**| Edges | Y | $\frac{1}{N} \sum_i \|\nabla Y\|_i$ | Average gradient strength across entire frame. Distinguishes soft gradients from hard boundaries. | Sensitive to overall image contrast. |
| **`std_edge_magnitude`** | Edges | Y | $\text{std}(\|\nabla Y\|)$ | Dispersion of edge strengths across image. | Correlated with overall dynamic range. |
| **`laplacian_variance`** | Sharpness | Y | $\text{Var}(\nabla^2 Y)$ | Focus/sharpness metric. High values indicate crisp textures and high-frequency content. | Highly sensitive to sensor noise and salt-and-pepper artifacts. |
| **`local_variance_mean`**| Texture | Y | $\frac{1}{B} \sum_{b=1}^B \text{Var}(Y_{\text{block } b})$ | Mean 8x8 block variance. Directly models DCT block energy in JPEG/AVC encoding. | Block alignment is fixed to non-overlapping 8x8 grid. |
| **`local_variance_std`** | Texture | Y | $\text{std}_b(\text{Var}(Y_{\text{block } b}))$ | Heterogeneity of texture across the image (e.g., smooth sky vs textured terrain). | High computational variance on mixed scenes. |
| **`glcm_contrast`** | Texture | Y | $\sum_{i,j} \|i - j\|^2 P(i,j)$ | Haralick GLCM contrast on 16-level quantized luminance. Captures local spatial transitions. | Quantization to 16 gray levels reduces precision for speed. |
| **`glcm_homogeneity`** | Texture | Y | $\sum_{i,j} \frac{P(i,j)}{1 + \|i - j\|}$ | Haralick GLCM homogeneity. High values indicate smooth, uniform transitions (favors lossy). | Inversely related to GLCM contrast. |
| **`noise_estimate`** | Noise Proxy | Y | $\frac{\sqrt{\pi/2}}{6(W-2)(H-2)} \sum \|Y * M_{\text{Laplace}}\|$ | Immerkaer (1996) fast pseudo-Laplacian noise proxy. Estimates additive Gaussian noise standard deviation. | High-frequency regular textures can trigger the filter; it is an empirical noise proxy, not ground truth. |
| **`dark_chroma_variance`**| Noise Proxy | U, V | $\frac{1}{2}(\text{Var}(U_{\text{dark}}) + \text{Var}(V_{\text{dark}}))$ for $Y < 40$ | Sensor thermal noise in shadow regions manifests as chromatic blotching. Highly vulnerable to 4:2:0 subsampling. | Defaults to $0.0$ if fewer than 100 dark pixels are present. |
| **`mean_r`, `mean_g`, `mean_b`** | Color Moments | R, G, B | $\frac{1}{N} \sum_i C_i$ | Primary channel color balances. Guides color quantization tables. | Strongly correlated with luminance mean. |
| **`std_r`, `std_g`, `std_b`** | Color Moments | R, G, B | $\text{std}_i(C_i)$ | Energy distribution across individual RGB color planes. | Inter-channel correlations are high in natural images. |
| **`mean_u`, `mean_v`** | Chrominance | U, V | $\frac{1}{N} \sum_i U_i, \frac{1}{N} \sum_i V_i$ | Average color difference (centered at 128 for neutral gray). | Chrominance is shifted by $+128$ offset in BT.601 representation. |
| **`std_u`, `std_v`** | Chrominance | U, V | $\text{std}_i(U_i), \text{std}_i(V_i)$ | Spread of color information. Low chroma std allows near-zero bit allocation to Cb/Cr. | Does not indicate spatial frequency of color changes. |
| **`colorfulness`** | Color Vibrancy | R, G, B | $\sigma_{rgyb} + 0.3 \mu_{rgyb}$ | Hasler & Süsstrunk (2003) metric. Measures perceived colorfulness / chromatic saturation. | Empirical psychophysical metric derived from human observer ratings. |

---

## 3. Mathematical Reference Formulae

### 3.1 ITU-R BT.601 Matrix Transformation
$$\begin{bmatrix} Y \\ U \\ V \end{bmatrix} = \begin{bmatrix} 0.299000 & 0.587000 & 0.114000 \\ -0.168736 & -0.331264 & 0.500000 \\ 0.500000 & -0.418688 & -0.081312 \end{bmatrix} \begin{bmatrix} R \\ G \\ B \end{bmatrix} + \begin{bmatrix} 0 \\ 128 \\ 128 \end{bmatrix}$$

### 3.2 Immerkaer Pseudo-Laplacian Noise Mask
$$M = \begin{bmatrix} 1 & -2 & 1 \\ -2 & 4 & -2 \\ 1 & -2 & 1 \end{bmatrix}$$
$$\sigma_n = \frac{\sqrt{\pi/2}}{6(W-2)(H-2)} \sum_{x=1}^{W-2} \sum_{y=1}^{H-2} |(Y * M)(x, y)|$$

### 3.3 Hasler & Süsstrunk Colorfulness
$$rg = R - G, \quad yb = \frac{1}{2}(R + G) - B$$
$$\sigma_{rgyb} = \sqrt{\sigma_{rg}^2 + \sigma_{yb}^2}, \quad \mu_{rgyb} = \sqrt{\mu_{rg}^2 + \mu_{yb}^2}$$
$$\text{Colorfulness} = \sigma_{rgyb} + 0.3 \mu_{rgyb}$$

