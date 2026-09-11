import os
import sys
import yaml
import argparse
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.dataset.labeler import build_labeled_dataset
from src.utils.visualizer import plot_class_distribution, plot_feature_distributions
from src.utils.logger import setup_logger

logger = setup_logger("04_generate_labels")

def main(config_path: str = "configs/config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    metadata_dir = config["paths"]["metadata_dir"]
    figures_dir = config["paths"]["figures_dir"]
    splits_path = os.path.join(metadata_dir, "splits.csv")
    splits_df = pd.read_csv(splits_path)
    
    logger.info("Generating ground-truth labels based on configurable decision criterion...")
    labels_df = build_labeled_dataset(splits_df, config=config)
    
    out_csv = os.path.join(metadata_dir, "labels.csv")
    labels_df.to_csv(out_csv, index=False)
    
    dist = labels_df["label"].value_counts().to_dict()
    logger.info(f"Class Distribution: {dist}")
    logger.info(f"Labels saved to {out_csv}")
    
    # Plot distributions
    plot_class_distribution(labels_df, os.path.join(figures_dir, "class_distribution.png"))
    
    feats_csv = os.path.join(metadata_dir, "features.csv")
    if os.path.exists(feats_csv):
        feats_df = pd.read_csv(feats_csv)
        plot_feature_distributions(feats_df, labels_df, os.path.join(figures_dir, "feature_distributions.png"))
        logger.info(f"Saved visualization figures to {figures_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()
    main(args.config)
