# Learning Module 01: Project Overview & System Architecture

## 1. What We Built
We designed and implemented Milestone 1 of the **Samsung PRISM Adaptive Compression** system. The core architecture evaluates incoming uncompressed image frames and intelligently classifies them into the optimal compression domain:
$$\text{LOSSY} \quad \text{vs} \quad \text{LOSSLESS}$$

## 2. Why We Built It
Modern mobile platforms, smartphone camera ISPs, and display controllers transfer gigabytes of image data across high-speed bus interfaces (e.g., MIPI CSI, LPDDR memory buses). Transmitting raw uncompressed 24-bit RGB frames generates massive memory bandwidth bottlenecks and battery drain.
* Lossless compression guarantees zero fidelity loss but provides limited compression ratios ($1.5\times$ to $2.5\times$).
* Lossy compression drastically reduces bandwidth ($5\times$ to $15\times$), but risks noticeable visual degradation—especially in low-light dark regions, smooth color gradients, and high-frequency textures.
* Our system learns to predict whether a frame can tolerate lossy compression *before* compression takes place.

## 3. How It Works
1. **Raw Frame Ingestion**: The system ingests an RGB or YUV frame buffer.
2. **Pre-Compression Feature Extraction**: Fast, $\mathcal{O}(N)$ statistical, spatial, and frequency features are computed directly on the uncompressed pixels.
3. **Intelligent Decision Engine**: A machine learning classifier evaluates the feature vector and outputs a compression decision.
4. **Targeted Codec Execution**: The frame is dispatched to the chosen codec (Lossless or Lossy).
5. **Memory & Quality Verification**: Memory consumption and visual quality are monitored against acceptable constraints.

## 4. Relevant Code Files
* [`configs/config.yaml`](file:///Users/oshishmadhan/.gemini/antigravity/scratch/adaptive-compression/configs/config.yaml): Central parameters for codecs, quality constraints, and feature thresholds.
* [`src/dataset/dataset_builder.py`](file:///Users/oshishmadhan/.gemini/antigravity/scratch/adaptive-compression/src/dataset/dataset_builder.py): Dataset acquisition and leakage-proof split generator.
* [`src/dataset/labeler.py`](file:///Users/oshishmadhan/.gemini/antigravity/scratch/adaptive-compression/src/dataset/labeler.py): Empirical ground-truth labeling engine.
* [`scripts/run_pipeline.py`](file:///Users/oshishmadhan/.gemini/antigravity/scratch/adaptive-compression/scripts/run_pipeline.py): End-to-end automated pipeline executor.

## 5. Design Decisions & Alternatives
* **Decision**: Adopt an empirical labeling protocol rather than hardcoded heuristics (e.g. bright $\to$ lossy).
  * *Alternative*: Heuristic rules. *Why rejected*: Fails to capture complex interaction between noise, texture, and DCT quantization.
* **Decision**: Binary decision for Milestone 1.
  * *Alternative*: Continuous quality factor regression. *Why rejected*: Matches Samsung PRISM Milestone 1 specification.

## 6. Common Bugs & Pitfalls
* **Target Leakage**: Accidentally passing post-compression file size or PSNR/SSIM to the classifier. If the classifier knows the compressed size, it achieves 100% fake accuracy.
* **Overfitting on Small Benchmarks**: Training deep neural networks on small benchmark sets without proper regularization.

## 7. PRISM / Technical Interview Questions
1. *Q: Why is classification accuracy an incomplete metric for adaptive compression?*  
   **A**: A model could achieve 90% accuracy by always predicting Lossy, but if the 10% misclassified frames suffer catastrophic banding or black-level blocking, the mobile user experience is ruined. We must evaluate net storage savings against critical quality violations.
2. *Q: How does this pipeline fit into a mobile camera ISP architecture?*  
   **A**: It acts as a frame-buffer dispatch gatekeeper between the sensor ISP pipeline and the LPDDR system memory.
