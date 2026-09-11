import os
import sys
import yaml
import json
import argparse
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.ml_baselines import train_baseline_models
from src.models.model_evaluator import evaluate_classifier
from src.utils.visualizer import plot_confusion_matrices, plot_feature_importances
from src.utils.logger import setup_logger

logger = setup_logger("05_train_baselines")

# Strict blacklist to guarantee ZERO data leakage into model inputs
TARGET_BLACKLIST = {
    "image_id", "split", "file_path", "label", "is_lossy_binary",
    "lossless_codec", "lossless_bytes", "lossless_cr",
    "lossy_codec", "lossy_quality", "lossy_bytes", "lossy_cr",
    "size_saving_ratio", "psnr", "ssim", "dark_ssim", "banding_score",
    "quality_passed", "saving_passed", "dark_passed", "raw_bytes"
}

def main(config_path: str = "configs/config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    metadata_dir = config["paths"]["metadata_dir"]
    results_dir = config["paths"]["results_dir"]
    figures_dir = config["paths"]["figures_dir"]
    os.makedirs(os.path.join(results_dir, "baseline"), exist_ok=True)
    
    feats_df = pd.read_csv(os.path.join(metadata_dir, "features.csv"))
    labels_df = pd.read_csv(os.path.join(metadata_dir, "labels.csv"))
    
    merged = pd.merge(feats_df, labels_df[["image_id", "label", "is_lossy_binary"]], on="image_id")
    
    # Audit for target leakage: select only pre-compression feature columns
    feature_cols = [c for c in feats_df.columns if c not in TARGET_BLACKLIST]
    logger.info(f"Target Leakage Audit: Identified {len(feature_cols)} clean pre-compression features.")
    logger.info(f"Feature Columns: {feature_cols}")
    
    # Partition by split
    train_mask = merged["split"] == "train"
    val_mask = merged["split"] == "val"
    test_mask = merged["split"] == "test"
    
    X_train = merged.loc[train_mask, feature_cols]
    y_train = merged.loc[train_mask, "is_lossy_binary"].values
    
    X_val = merged.loc[val_mask, feature_cols]
    y_val = merged.loc[val_mask, "is_lossy_binary"].values
    
    X_test = merged.loc[test_mask, feature_cols]
    y_test = merged.loc[test_mask, "is_lossy_binary"].values
    
    logger.info(f"Split sizes: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")
    
    # Train baselines
    models = train_baseline_models(X_train, y_train, random_state=config["models"]["random_seed"])
    
    eval_results = {}
    test_predictions = {}
    confusion_matrices = {}
    
    for name, model in models.items():
        # Evaluate on Val
        val_pred = model.predict(X_val)
        val_eval = evaluate_classifier(y_val, val_pred)
        
        # Evaluate on Test
        test_pred = model.predict(X_test)
        test_predictions[name] = test_pred.tolist()
        test_prob = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None
        test_eval = evaluate_classifier(y_test, test_pred, test_prob)
        
        eval_results[name] = {
            "val": val_eval,
            "test": test_eval
        }
        confusion_matrices[name] = test_eval["confusion_matrix"]
        
        logger.info(f"[{name.upper()}] Test Acc: {test_eval['accuracy']:.3f} | F1: {test_eval['f1_score']:.3f} | Prec: {test_eval['precision']:.3f} | Rec: {test_eval['recall']:.3f}")

    # Save metrics JSON
    metrics_path = os.path.join(results_dir, "baseline", "model_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(eval_results, f, indent=2)
        
    # Save predictions JSON for system evaluation
    preds_path = os.path.join(results_dir, "baseline", "test_predictions.json")
    with open(preds_path, "w") as f:
        json.dump(test_predictions, f, indent=2)
        
    # Visualizations
    plot_confusion_matrices(confusion_matrices, os.path.join(figures_dir, "confusion_matrices.png"))
    
    if "random_forest" in models:
        rf_importances = models["random_forest"].get_feature_importances()
        plot_feature_importances(rf_importances, os.path.join(figures_dir, "feature_importances.png"))
        
    logger.info(f"Baseline training & evaluation completed. Results saved to {metrics_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()
    main(args.config)
