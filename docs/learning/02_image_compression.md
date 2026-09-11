# Learning Module 02: Principles of Image Compression (Lossy vs Lossless)

## 1. What We Built
In `src/compression/codecs.py` and `src/compression/benchmark.py`, we implemented a standardized compression abstraction supporting:
* **Lossless Codecs**: PNG (spatial predictive filtering + DEFLATE) and WebP Lossless (VP8L entropy coding).
* **Lossy Codecs**: JPEG (DCT + quantization + Huffman) and WebP Lossy (intra-frame VP8 prediction + DCT-like transform) across quality levels (50, 75, 85, 95).

## 2. Core Concepts
* **Raw Uncompressed Frame Size**:
  $$S_{\text{raw}} = \text{Height} \times \text{Width} \times \text{Channels} \quad (\text{bytes})$$
  For a $768 \times 512$ RGB image, $S_{\text{raw}} = 1,179,648\text{ bytes } (\approx 1.18\text{ MB})$.
* **Compression Ratio (CR)**:
  $$\text{CR} = \frac{S_{\text{raw}}}{S_{\text{compressed}}}$$
  $\text{CR} = 10.0$ indicates that the compressed frame occupies $10\%$ of raw memory.
* **Storage Reduction Ratio ($R$)**:
  $$R = \frac{S_{\text{lossless}} - S_{\text{lossy}}}{S_{\text{lossless}}} = 1 - \frac{S_{\text{lossy}}}{S_{\text{lossless}}}$$
  Measures the marginal memory savings achieved by choosing lossy over lossless.

## 3. Lossless Compression Mechanics
Lossless codecs exploit *spatial redundancy* and *statistical redundancy* without discarding any information:
1. **Prediction**: Predicts current pixel value from neighboring left, top, and top-left pixels.
2. **Residual Encoding**: Computes difference: $r(x, y) = I(x, y) - \hat{I}(x, y)$. Residuals are sharply clustered near zero.
3. **Entropy Coding**: Employs Huffman or Arithmetic coding to assign short bitstrings to frequent residuals.
* **Limitation**: If an image contains sensor noise or high entropy, residuals are broad and unpredictable, dropping CR towards $1.0\times$.

## 4. Lossy Compression Mechanics
Lossy codecs exploit *psychovisual redundancy* (imperfections in the human visual system):
1. **Color Transform**: RGB $\to$ YCbCr with chroma subsampling (4:2:0).
2. **Frequency Transform**: 2D Discrete Cosine Transform (DCT) transforms spatial $8 \times 8$ blocks into frequency domain coefficients.
3. **Quantization**: High-frequency coefficients are divided by large quantization step sizes and rounded to integers:
   $$F_Q(u, v) = \text{round}\left(\frac{F(u, v)}{Q(u, v)}\right)$$
   This step discards imperceptible high frequencies and creates long runs of zeros.
4. **Entropy Coding**: Run-length encoding + Huffman coding.

## 5. Relevant Code
* [`src/compression/codecs.py`](file:///Users/oshishmadhan/.gemini/antigravity/scratch/adaptive-compression/src/compression/codecs.py): `compress_image()`, `decompress_image()`.
* [`src/compression/benchmark.py`](file:///Users/oshishmadhan/.gemini/antigravity/scratch/adaptive-compression/src/compression/benchmark.py): `benchmark_compression()`, `run_codec_suite()`.

## 6. PRISM / Technical Interview Questions
1. *Q: What causes blocking artifacts in JPEG compression?*  
   **A**: Independent quantization of separate $8 \times 8$ DCT blocks. At block boundaries, coarse quantization creates discontinuous jump steps between adjacent pixel blocks.
2. *Q: Why does high ISO sensor noise destroy lossless compression efficiency?*  
   **A**: Sensor noise is stochastic (uncorrelated). Lossless predictors cannot anticipate random noise, resulting in flat, high-entropy residual distributions that cannot be compressed.
