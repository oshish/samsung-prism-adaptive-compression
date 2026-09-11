# Learning Module 08: Baseline Machine Learning Classifiers

## 1. What We Built
In `src/models/`, we implemented 5 baseline strategies:
1. **Majority Class Baseline**: Predicts the dominant class in the training split. Sets the performance floor.
2. **Rule-Based Baseline**: Human domain heuristic testing the hypothesis:
   "If mean luminance is adequate ($\ge 65$), dark ratio is small ($\le 0.35$), noise is low ($\le 12$), and high-frequency texture is moderate ($\le 800$), choose `LOSSY`; else `LOSSLESS`."
3. **Logistic Regression**: Linear decision boundary with standard scaling and balanced class weighting.
4. **Decision Tree Classifier**: Interpretable orthogonal decision boundaries (max depth = 4).
5. **Random Forest Classifier**: Ensemble of 50 decorrelated decision trees with feature importance extraction.

## 2. Model Evaluation Metrics
* **Accuracy**: $\frac{TP + TN}{TP + TN + FP + FN}$ (monitors overall classification correctness).
* **Precision**: $\frac{TP}{TP + FP}$ (crucial: predicts LOSSY when it is truly safe for LOSSY; minimizes quality violations).
* **Recall**: $\frac{TP}{TP + FN}$ (maximizes opportunistic memory savings by identifying compressible frames).
* **F1-Score**: Harmonic mean of Precision and Recall.
* **Confusion Matrix**: Visualizes False Positives (catastrophic quality errors) vs False Negatives (missed storage savings).

## 3. PRISM / Technical Interview Questions
1. *Q: Why start with simple baselines rather than a Deep Convolutional Neural Network (CNN)?*  
   **A**: Occam's Razor and engineering rigor. Simple models provide fast inference ($< 1\text{ ms}$ on CPU), complete interpretability, zero overfitting risk on small benchmark sets, and establish a firm benchmark against which complex deep learning models in Milestone 2 must be justified.
2. *Q: In our problem, is a False Positive or a False Negative worse?*  
   **A**: A **False Positive** is far worse. A False Positive occurs when the model predicts `LOSSY` for an image that requires `LOSSLESS`, resulting in visible artifacts or banding. A False Negative merely misses a storage optimization opportunity while preserving perfect lossless fidelity.
