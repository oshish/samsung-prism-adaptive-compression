# Learning Module 07: Empirical Ground-Truth Label Generation

## 1. What We Built
In `src/dataset/labeler.py`, we implemented the empirical ground-truth label generation engine. Rather than relying on ungrounded heuristics (such as bright $\to$ lossy), our engine measures actual compression performance on each frame:
1. Compresses losslessly (PNG) $\to$ $S_{\text{lossless}}$.
2. Compresses lossy (JPEG, Q=75) $\to$ $S_{\text{lossy}}$, $\text{PSNR}$, $\text{SSIM}$, $\text{Dark-SSIM}$, and $\text{Banding Score}$.
3. Evaluates Marginal Storage Savings:
   $$R = \frac{S_{\text{lossless}} - S_{\text{lossy}}}{S_{\text{lossless}}}$$
4. Decides Ground Truth:
   $$\text{Label} = \begin{cases} \text{LOSSY}, & \text{if } \text{SSIM} \ge \tau_{\text{SSIM}} \land \text{PSNR} \ge \tau_{\text{PSNR}} \land R \ge \tau_{\text{saving}} \land \text{Dark-SSIM} \ge \tau_{\text{dark}} \\ \text{LOSSLESS}, & \text{otherwise} \end{cases}$$

## 2. Why Configurable Parameters?
All thresholds are marked:
`ASSUMPTION — REQUIRES MENTOR CONFIRMATION`
* In `configs/config.yaml`:
  * `ssim_threshold`: $0.95$
  * `psnr_threshold`: $34.0\text{ dB}$
  * `min_size_saving`: $0.25$ ($25\%$ savings over lossless)
  * `dark_ssim_threshold`: $0.92$
  * `dark_pixel_cutoff`: $40$

If the Samsung mentor requests higher fidelity (e.g. $\text{SSIM} \ge 0.98$) or allows lower saving cutoffs, the pipeline updates labels with a single configuration parameter and regenerates labels in seconds.

## 3. PRISM / Technical Interview Questions
1. *Q: Why do we require both SSIM and a minimum size saving ratio?*  
   **A**: If lossy compression achieves high visual quality ($\text{SSIM} = 0.99$) but only saves $2\%$ of memory compared to lossless compression, taking the risk of lossy compression is completely unjustified. The storage savings must be worth the risk of irreversible quantization.
2. *Q: How does the dark SSIM constraint protect image quality?*  
   **A**: In images with dark backgrounds, global SSIM can remain above $0.96$ even if the shadows exhibit severe blockiness. The localized $\text{Dark-SSIM}$ check forces such frames into `LOSSLESS` mode.
