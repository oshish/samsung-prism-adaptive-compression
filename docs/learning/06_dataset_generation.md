# Learning Module 06: Dataset Acquisition, Stress Suite & Leakage-Safe Splitting

## 1. What We Built
In `src/dataset/dataset_builder.py`, we created a benchmark preparation engine combining:
* **The Canonical Kodak Dataset**: 24 pristine, uncompressed true-color images ($768 \times 512$). Kodak is universally recognized in literature (JPEG, WebP, BPG, AVIF) as the gold standard for image compression evaluation.
* **Synthetic / Controlled Stress Suite**: 6 targeted test frames designed specifically for mobile memory failure modes:
  1. `edge_01_smooth_gradient`: Banding / false-contouring test.
  2. `edge_02_dark_noisy`: Low-light frame ($Y < 20$) with heavy Gaussian noise ($\sigma = 12$).
  3. `edge_03_dense_texture`: Procedural high-frequency cloth/foliage texture.
  4. `edge_04_sharp_ui_graphics`: High-contrast UI text, rectangles, and fine line graphics.
  5. `edge_05_clean_flat_poster`: Solid color blocks (ideal candidate for lossy compression).
  6. `edge_06_mixed_hdr`: High dynamic range split frame (shadows + bright sunlight).

## 2. Leakage-Safe Partitioning
* Partitioning is strictly deterministic (Seed 42).
* Partitioning occurs by `image_id` (60% Train, 20% Val, 20% Test).
* No derived crops or compressed variants of a training image ever appear in the validation or test splits.

## 3. PRISM / Technical Interview Questions
1. *Q: Why did we supplement Kodak with synthetic stress frames?*  
   **A**: Standard photographic benchmarks rarely include extreme edge cases such as purely synthetic UI screenshots, pure linear gradients, or severe sensor noise. Incorporating controlled edge cases ensures the compression decision engine is stress-tested against worst-case memory failures.
2. *Q: How do we prevent data leakage across splits?*  
   **A**: All splitting is performed on the parent image manifest prior to any feature extraction or compression experiments. Downstream processes reference only the manifest split column.
