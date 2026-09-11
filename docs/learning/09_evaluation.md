# Learning Module 09: System-Level Objective Evaluation

## 1. What We Built
In `src/evaluation/system_evaluator.py`, we designed the evaluation that addresses the true engineering objective of Samsung PRISM:
> "If our classifier chooses the compression strategy, what happens to actual file size and image quality?"

## 2. Comparative Strategies
We benchmark 6 competing strategies on the held-out test split:
1. **Always Lossless**: Upper bound on quality ($\text{SSIM} = 1.0$, $\text{PSNR} = \infty$), lower bound on memory savings.
2. **Always Lossy**: Upper bound on memory savings, worst-case risk of quality violations.
3. **Rule-Based Heuristic**: Handcrafted engineering rules.
4. **Logistic Regression Classifier**: Linear statistical boundary.
5. **Random Forest Classifier**: Non-linear ensemble model.
6. **Oracle Ground Truth**: Theoretical upper bound (perfect foresight).

## 3. Evaluated System Metrics
For each strategy across the test split, the evaluator measures:
* **Total Storage Footprint (MB)** across test frames.
* **Storage Savings vs Raw Uncompressed Frame Buffer (%)**.
* **Storage Savings vs Always Lossless (%)**.
* **Mean SSIM & Mean PSNR** across the test set.
* **Critical Quality Violations**: Number and percentage of frames where the model chose `LOSSY` but the resulting compressed frame violated acceptable quality constraints.

## 4. PRISM / Technical Interview Questions
1. *Q: What does the Pareto frontier tell us in adaptive compression?*  
   **A**: It visualizes the optimal trade-off curve between memory savings and visual fidelity. A superior model pushes the frontier towards high savings without sacrificing SSIM.
