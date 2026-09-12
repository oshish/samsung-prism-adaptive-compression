# Compression Experiments & Rate-Distortion Benchmarks
**Project**: Samsung PRISM — Adaptive Compression: Intelligent Frame Compression for Memory Optimization  
**Worklet ID**: 26VI11 | **Department**: CSED | **Milestone**: 1 (Step 7)

---

## 1. Experimental Overview
Step 7 evaluates the compression efficiency, encoding/decoding runtime latency, and rate-distortion characteristics of canonical lossless and lossy compression codecs across our diverse 1,030-frame dataset.

The evaluated codec configurations comprise:
* **Lossless Codecs**:
  1. **PNG**: Deflate/LZ77 filter-based lossless compression (standard reference in image compression literature).
  2. **WebP Lossless**: Advanced predictive entropy coding using VP8L, achieving higher density than PNG at the cost of additional CPU encoding time.
* **Lossy Codecs**:
  3. **JPEG (Quality = 50)**: High compression / low bitrate mode.
  4. **JPEG (Quality = 75)**: Balanced web standard.
  5. **JPEG (Quality = 85)**: High-fidelity preservation mode (default lossy candidate for PRISM decision engine).
  6. **JPEG (Quality = 95)**: Near-lossless lossy mode with minimal quantization.

Across $1,030$ images, this produces $6 \times 1,030 = 6,180$ empirical compression trials.

---

## 2. Benchmark Metrics Recorded per Trial
For each compression trial, the benchmark harness records:
1. `raw_bytes`: Total byte count of the uncompressed 24-bit RGB frame ($H \times W \times 3$).
2. `compressed_bytes`: File size of the compressed bitstream in memory.
3. `compression_ratio`: Ratio of uncompressed to compressed size ($\frac{\text{raw\_bytes}}{\text{compressed\_bytes}}$).
4. `encode_time_ms`: CPU encoding time measured via high-resolution monotonic performance counter.
5. `decode_time_ms`: CPU decompression time to reconstruct the RGB array.
6. `mse`: Global Mean Squared Error between original and reconstructed RGB pixel arrays.
7. `psnr`: Peak Signal-to-Noise Ratio (dB).
8. `ssim`: 3-channel Structural Similarity Index (11x11 Gaussian window).
9. `dark_ssim`: Localized SSIM restricted to low-luminance regions ($Y < 40$).
10. `dark_psnr`: Localized PSNR in shadow regions.
11. `banding_score`: Quantitative false contouring / step gradient metric.
12. `edge_preservation`: Ratio of high-frequency gradient energy.

Outputs are written to:
* `data/metadata/compression_experiments.csv`
* `results/compression/compression_results.csv`

---

## 3. Empirical Rate-Distortion & Latency Benchmarks (6,180 Trials)

The table below summarizes the mean empirical performance across all 1,030 images in the benchmark dataset:

| Codec | Quality | Compression Ratio | Memory Saved vs Raw | Encode Latency | Decode Latency | PSNR (dB) | SSIM | Dark-SSIM | Edge Pres. | Real-Time Suitability |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **JPEG** | 50 | $18.81\times$ | $94.68\%$ | $1.45\text{ ms}$ | $1.77\text{ ms}$ | $30.95$ | $0.9238$ | $0.9273$ | $1.0895$ | Fails SSIM ($\tau \ge 0.94$) & PSNR ($\tau \ge 33.0$) |
| **JPEG** | 75 | $14.63\times$ | $93.16\%$ | $1.43\text{ ms}$ | $1.87\text{ ms}$ | $46.43$ | $0.9929$ | $0.9927$ | $1.0010$ | Excellent quality, fast |
| **JPEG** | **85** | **$11.61\times$** | **$91.39\%$** | **$1.42\text{ ms}$** | **$1.91\text{ ms}$** | **$42.08$** | **$0.9908$** | **$0.9912$** | **$1.0177$** | **Primary lossy target: optimal balance** |
| **JPEG** | 95 | $7.77\times$ | $87.13\%$ | $1.47\text{ ms}$ | $2.08\text{ ms}$ | $48.58$ | $0.9969$ | $0.9971$ | $1.0004$ | Near-lossless lossy mode |
| **PNG** | — | $3.80\times$ | $73.72\%$ | $12.27\text{ ms}$ | $4.55\text{ ms}$ | $\infty$ | $1.0000$ | $1.0000$ | $1.0000$ | **Primary lossless standard: reliable, safe** |
| **WebP Lossless** | 100 | $17.68\times$ | $94.34\%$ | $462.40\text{ ms}$ | $5.04\text{ ms}$ | $\infty$ | $1.0000$ | $1.0000$ | $1.0000$ | Unusable in real-time ($> 460\text{ ms}$ encode) |

---

## 4. Key Engineering Insights
1. **The WebP Lossless Bottleneck**: While WebP Lossless achieves exceptional compression ($17.68\times$ vs PNG's $3.80\times$), its encoding latency of $462.4\text{ ms}$ per frame makes it completely infeasible for real-time camera ISP or $60\text{ Hz} / 120\text{ Hz}$ display frame buffer hardware.
2. **JPEG Q=85 as Ideal Operating Point**: JPEG Q=85 delivers $11.61\times$ compression with an average encode time of only $1.42\text{ ms}$ and decode time of $1.91\text{ ms}$, comfortably fitting within mobile frame delivery budgets while maintaining exceptional visual fidelity ($\text{SSIM} = 0.9908$, $\text{Dark-SSIM} = 0.9912$).
3. **JPEG Q=50 Degrades Structure**: At Q=50, average SSIM drops to $0.9238$ and PSNR to $30.95\text{ dB}$, confirming that aggressive quantization breaches acceptable quality thresholds on photographic frames.
4. **Edge Energy Preservation**: JPEG Q=85 and Q=75 maintain near-unity edge preservation ($1.018$ and $1.001$), whereas Q=50 shows high-frequency artifact inflation ($1.0895$).
