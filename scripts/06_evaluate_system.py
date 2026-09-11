import os
import sys
import yaml
import json
import argparse
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.evaluation.system_evaluator import evaluate_system_impact
from src.utils.visualizer import plot_storage_quality_tradeoff
from src.utils.logger import setup_logger

logger = setup_logger("06_evaluate_system")

def main(config_path: str = "configs/config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    metadata_dir = config["paths"]["metadata_dir"]
    results_dir = config["paths"]["results_dir"]
    figures_dir = config["paths"]["figures_dir"]
    
    labels_df = pd.read_csv(os.path.join(metadata_dir, "labels.csv"))
    test_df = labels_df[labels_df["split"] == "test"].reset_index(drop=True)
    
    preds_path = os.path.join(results_dir, "baseline", "test_predictions.json")
    with open(preds_path, "r") as f:
        test_preds = json.load(f)
        
    # Add Oracle Ground Truth strategy
    test_preds["oracle_ground_truth"] = test_df["is_lossy_binary"].values.tolist()
    
    label_cfg = config["labeling"]
    sys_eval = evaluate_system_impact(
        test_metadata=test_df,
        predictions={k: np.array(v) for k, v in test_preds.items()},
        ssim_threshold=label_cfg["ssim_threshold"],
        psnr_threshold=label_cfg["psnr_threshold"],
        dark_ssim_threshold=label_cfg["dark_ssim_threshold"]
    )
    
    out_json = os.path.join(results_dir, "system_evaluation.json")
    with open(out_json, "w") as f:
        json.dump(sys_eval, f, indent=2)
        
    logger.info("=== SYSTEM-LEVEL STORAGE & QUALITY EVALUATION ===")
    for strat, data in sys_eval["strategies"].items():
        logger.info(
            f"Strategy: {strat:<22} | "
            f"Size: {data['total_mb']:.2f}MB | "
            f"Saved vs Lossless: {data['saving_vs_lossless_pct']:>5.1f}% | "
            f"Mean SSIM: {data['mean_ssim']:.4f} | "
            f"Failures: {data['critical_failures']}"
        )
        
    plot_storage_quality_tradeoff(sys_eval, os.path.join(figures_dir, "storage_quality_tradeoff.png"))
    logger.info(f"System evaluation report saved to {out_json}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()
    main(args.config)
