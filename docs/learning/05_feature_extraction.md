# Learning Module 05: Pre-Compression Feature Extraction (Zero-Leakage Engineering)

## 1. What We Built
In `src/features/`, we built an extensive suite of pre-compression image feature extractors:
* `brightness_features.py`: Mean, standard deviation, skewness, kurtosis, dark/bright ratios, RMS contrast.
* `texture_features.py`: Local $8 \times 8$ patch variance mean and variance; GLCM Haralick contrast, dissimilarity, homogeneity, energy, and correlation.
* `edge_features.py`: Sobel mean/max magnitude, edge density ($> 30.0$), Laplacian focus variance.
* `noise_features.py`: Immerkaer fast Laplacian Gaussian noise estimator; dark-region chroma variance.
* `entropy_features.py`: Shannon entropy of luminance (bits/pixel); per-channel color entropy; Hasler & Süsstrunk colorfulness metric.
* `extractor.py`: Unified, failure-safe wrapper returning a flattened feature dictionary.

## 2. Why Pre-Compression Features Only?
To make a real-time compression decision, the system cannot compress the image first to check if it compresses well. The features must be extracted **strictly before compression** using only the input frame buffer.
* **Zero Target Leakage**: If any post-compression metric (e.g. compressed file size, PSNR, SSIM) is used as an input feature, the model cheats. We enforced an automated blacklist in `tests/test_leakage.py` to mathematically guarantee zero leakage.

## 3. Mathematical Noise Estimation (Immerkaer Filter)
Instead of fitting slow wavelet transforms, we use Immerkaer's discrete $3 \times 3$ Laplacian mask $N$:
$$N = \begin{bmatrix} 1 & -2 & 1 \\ -2 & 4 & -2 \\ 1 & -2 & 1 \end{bmatrix}$$
$$\hat{\sigma}_n = \sqrt{\frac{\pi}{2}} \frac{1}{6(W-2)(H-2)} \sum_{x,y} |(I * N)(x, y)|$$
This operator cancels polynomial gradients (smooth surfaces and linear ramps) and isolates zero-mean additive Gaussian noise in a single 2D convolution pass.

## 4. PRISM / Technical Interview Questions
1. *Q: Why is Shannon entropy of the luminance histogram predictive of compression?*  
   **A**: Shannon entropy $H = -\sum p_i \log_2 p_i$ defines the theoretical lower bound on bits required to represent each pixel without loss. Images with high entropy contain diverse, unpredictable intensities that resist both spatial prediction and lossless entropy coding.
2. *Q: What is the computational complexity of our feature extraction?*  
   **A**: All features (Sobel, Immerkaer mask, local variance, histogram) operate in $\mathcal{O}(N)$ time where $N = W \times H$. No iterative optimization or deep backpropagation is required.
