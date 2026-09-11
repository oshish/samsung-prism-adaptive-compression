import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier

class MLModelWrapper:
    """
    Unified wrapper for scikit-learn classifiers with feature scaling,
    feature importance extraction, and single-class safety fallbacks.
    """
    def __init__(self, model_type: str, random_state: int = 42):
        self.model_type = model_type
        self.random_state = random_state
        self.feature_names: list = []
        self.model = None
        
    def _create_model(self, num_classes: int):
        if num_classes < 2:
            return DummyClassifier(strategy="most_frequent")
        if self.model_type == "logistic_regression":
            return Pipeline([
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(random_state=self.random_state, max_iter=1000, class_weight="balanced"))
            ])
        elif self.model_type == "decision_tree":
            return DecisionTreeClassifier(max_depth=4, random_state=self.random_state, class_weight="balanced")
        elif self.model_type == "random_forest":
            return RandomForestClassifier(n_estimators=50, max_depth=5, random_state=self.random_state, class_weight="balanced")
        else:
            raise ValueError(f"Unknown model_type: {self.model_type}")
            
    def fit(self, X: pd.DataFrame, y: np.ndarray) -> "MLModelWrapper":
        self.feature_names = list(X.columns)
        num_classes = len(np.unique(y))
        self.model = self._create_model(num_classes)
        self.model.fit(X, y)
        return self
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict(X)
        
    def predict_proba(self, X: pd.DataFrame) -> Optional[np.ndarray]:
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(X)
            if probs.shape[1] == 2:
                return probs[:, 1]
            elif probs.shape[1] == 1:
                return probs[:, 0]
        return None
        
    def get_feature_importances(self) -> Dict[str, float]:
        if isinstance(self.model, DummyClassifier):
            return {f: 0.0 for f in self.feature_names}
        if self.model_type == "logistic_regression" and hasattr(self.model, "named_steps"):
            clf = self.model.named_steps["clf"]
            if hasattr(clf, "coef_"):
                coefs = np.abs(clf.coef_[0])
                return {f: float(c) for f, c in zip(self.feature_names, coefs)}
        elif self.model_type in ("decision_tree", "random_forest"):
            if hasattr(self.model, "feature_importances_"):
                importances = self.model.feature_importances_
                return {f: float(imp) for f, imp in zip(self.feature_names, importances)}
        return {}

def train_baseline_models(
    X_train: pd.DataFrame,
    y_train: np.ndarray,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Trains all candidate baseline models:
    1. Majority Class
    2. Rule-Based Heuristic
    3. Logistic Regression
    4. Decision Tree
    5. Random Forest
    """
    from .baseline_heuristics import MajorityClassBaseline, RuleBasedBaseline
    
    models = {}
    
    # 1. Majority
    maj = MajorityClassBaseline()
    y_series = pd.Series(["LOSSY" if v == 1 else "LOSSLESS" for v in y_train])
    maj.fit(X_train, y_series)
    models["majority"] = maj
    
    # 2. Rule-Based
    rb = RuleBasedBaseline()
    rb.fit(X_train, y_series)
    models["rule_based"] = rb
    
    # 3. Logistic Regression
    lr = MLModelWrapper("logistic_regression", random_state=random_state)
    lr.fit(X_train, y_train)
    models["logistic_regression"] = lr
    
    # 4. Decision Tree
    dt = MLModelWrapper("decision_tree", random_state=random_state)
    dt.fit(X_train, y_train)
    models["decision_tree"] = dt
    
    # 5. Random Forest
    rf = MLModelWrapper("random_forest", random_state=random_state)
    rf.fit(X_train, y_train)
    models["random_forest"] = rf
    
    return models
