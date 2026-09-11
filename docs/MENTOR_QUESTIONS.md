# Mentor Questions — Samsung PRISM: Adaptive Compression
**Worklet ID**: 26VI11 | **Department**: CSED | **Milestone**: 1 Review Preparation

The following prioritized questions have been prepared by our student team (Person A, Person B, Person C) to discuss with our Samsung PRISM mentor during our Milestone 1 review.

---

### Priority 1: Ground-Truth Labeling & Quality Criteria (CRITICAL)
> **Question 1.1**: For generating our ground-truth compression labels, should we define the optimal strategy using a fixed perceptual-quality threshold (e.g. SSIM $\ge 0.95$ / PSNR $\ge 34.0\text{ dB}$), or does Samsung have a specific proprietary or task-dependent criterion for "acceptable visual quality"?
* **Context**: Our Milestone 1 empirical pipeline derives labels by measuring the actual rate-distortion outcome: if lossy compression yields $\text{SSIM} \ge \tau_{\text{SSIM}}$ while saving $\ge 25\%$ storage, the frame is labeled `LOSSY`; otherwise `LOSSLESS`. We need to align our threshold with Samsung's target use case.

> **Question 1.2**: Is dark-region artifact degradation (such as blocking or false contouring in low-light scenes) a primary failure mode that Samsung specifically monitors? Does Samsung prefer a localized metric (e.g. Dark-SSIM on $Y < 40$) or visual artifact flagging?

---

### Priority 2: Target Codecs & Hardware Environment
> **Question 2.1**: Which compression codecs most closely match Samsung's intended target memory subsystem?
* **Context**: In Milestone 1, we implemented standard modular software codecs: Lossless (PNG, WebP Lossless) and Lossy (JPEG, WebP Lossy at varying quality levels). Is Samsung targeting a software image buffer pipeline (e.g., WebP / JPEG / AVIF) or hardware frame buffer compression (such as AFBC, ASTC, or proprietary display driver compression)?

> **Question 2.2**: What is the target execution budget for the decision engine?
* **Context**: Should feature extraction and inference execute within a hard real-time budget (e.g., $< 2\text{ ms}$ per frame in C/C++/NPU) or is it an asynchronous background memory optimization?

---

### Priority 3: Color Space & Sensor Pipeline Expectations
> **Question 3.1**: What input representation will the system receive in deployment?
* **Context**: Does the incoming frame arrive as raw RGB888, packed RGBA, or planar YUV420 / YUV422 directly from the camera ISP or GPU frame buffer?
* **Context**: In Milestone 1, we built full support for both RGB and ITU-R BT.601 YCbCr, extracting features across luminance ($Y$) and chrominance ($Cb/Cr$).

---

### Priority 4: Formulation Scope & Future Milestones
> **Question 4.1**: In Milestone 2 and beyond, should we retain a strictly binary decision (`LOSSY` vs `LOSSLESS`), or is Samsung interested in multi-level adaptive compression (e.g., `LOSSLESS`, `LOSSY_HIGH_QUALITY`, `LOSSY_BALANCED`, `LOSSY_AGGRESSIVE`) or continuous quality parameter prediction ($Q \in [1, 100]$)?

> **Question 4.2**: Does Samsung have a preferred evaluation dataset (e.g. mobile camera sensor captures, burst frames, UI screenshots) that we should incorporate into Milestone 2, alongside the standard Kodak and stress-test benchmark datasets used in Milestone 1?
