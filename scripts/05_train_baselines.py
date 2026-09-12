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
    
    labels_df = pd.read_csv(os.path.join(metadata_dir, "labels.csv"))
    feats_path = os.path.join(metadata_dir, "image_features.csv")
    if not os.path.exists(feats_path):
        feats_path = os.path.join(metadata_dir, "features.csv")
    feats_df = pd.read_csv(feats_path)
    
    # Left merge on labels_df preserves deterministic splits order
    merged = pd.merge(labels_df[["image_id", "split", "label", "is_lossy_binary"]], feats_df, on="image_id")
    
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
    test_image_ids = merged.loc[test_mask, "image_id"].tolist()
    
    logger.info(f"Split sizes: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")
    
    # Train baselines
    models = train_baseline_models(X_train, y_train, random_state=config["models"]["random_seed"])
    
    eval_results = {}
    test_predictions = {}
    confusion_matrices = {}
    
    logger.info(f"{'Model':<22} | {'Split':<6} | {'Accuracy':<8} | {'Precision':<9} | {'Recall':<8} | {'F1-Score':<8} | {'ROC-AUC':<8}")
    logger.info("-" * 80)
    
    for name, model in models.items():
        # Evaluate on Train
        train_pred = model.predict(X_train)
        train_prob = model.predict_proba(X_train) if hasattr(model, "predict_proba") else None
        train_eval = evaluate_classifier(y_train, train_pred, train_prob)
        
        # Evaluate on Val
        val_pred = model.predict(X_val)
        val_prob = model.predict_proba(X_val) if hasattr(model, "predict_proba") else None
        val_eval = evaluate_classifier(y_val, val_pred, val_prob)
        
        # Evaluate on Test
        test_pred = model.predict(X_test)
        test_predictions[name] = test_pred.tolist()
        test_prob = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None
        test_eval = evaluate_classifier(y_test, test_pred, test_prob)
        
        eval_results[name] = {
            "train": train_eval,
            "val": val_eval,
            "test": test_eval
        }
        confusion_matrices[name] = test_eval["confusion_matrix"]
        
        t_auc_str = f"{train_eval['roc_auc']:.3f}" if train_eval['roc_auc'] is not None else "N/A"
        v_auc_str = f"{val_eval['roc_auc']:.3f}" if val_eval['roc_auc'] is not None else "N/A"
        te_auc_str = f"{test_eval['roc_auc']:.3f}" if test_eval['roc_auc'] is not None else "N/A"
        
        logger.info(f"{name:<22} | {'Train':<6} | {train_eval['accuracy']:<8.3f} | {train_eval['precision']:<9.3f} | {train_eval['recall']:<8.3f} | {train_eval['f1_score']:<8.3f} | {t_auc_str:<8}")
        logger.info(f"{'':<22} | {'Val':<6} | {val_eval['accuracy']:<8.3f} | {val_eval['precision']:<9.3f} | {val_eval['recall']:<8.3f} | {val_eval['f1_score']:<8.3f} | {v_auc_str:<8}")
        logger.info(f"{'':<22} | {'Test':<6} | {test_eval['accuracy']:<8.3f} | {test_eval['precision']:<9.3f} | {test_eval['recall']:<8.3f} | {test_eval['f1_score']:<8.3f} | {te_auc_str:<8}")
        logger.info("-" * 80)

    # Save metrics JSON
    metrics_path = os.path.join(results_dir, "baseline", "model_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(eval_results, f, indent=2)
        
    # Save predictions JSON for system evaluation
    preds_path = os.path.join(results_dir, "baseline", "test_predictions.json")
    preds_payload = {
        "test_image_ids": test_image_ids,
        "predictions": test_predictions
    }
    with open(preds_path, "w") as f:
        json.dump(preds_payload, f, indent=2)
        
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
