import os
import sys
import yaml
import argparse

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.dataset.dataset_builder import prepare_benchmark_dataset, create_datasplits
from src.utils.logger import setup_logger

logger = setup_logger("01_prepare_dataset")

def main(config_path: str = "configs/config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    raw_dir = config["paths"]["raw_dir"]
    metadata_dir = config["paths"]["metadata_dir"]
    ds_cfg = config["dataset"]
    
    logger.info(f"Phase 1: Preparing benchmark dataset in '{raw_dir}'...")
    image_paths = prepare_benchmark_dataset(raw_dir)
    logger.info(f"Prepared {len(image_paths)} total benchmark frames (Kodak + Edge-Case Suite).")
    
    logger.info(f"Generating deterministic train/val/test splits (Seed: {ds_cfg['random_seed']})...")
    splits_df = create_datasplits(
        image_paths=image_paths,
        metadata_dir=metadata_dir,
        train_ratio=ds_cfg["train_ratio"],
        val_ratio=ds_cfg["val_ratio"],
        test_ratio=ds_cfg["test_ratio"],
        random_seed=ds_cfg["random_seed"]
    )
    
    counts = splits_df["split"].value_counts().to_dict()
    logger.info(f"Splits successfully generated: {counts}")
    logger.info(f"Saved manifest to {os.path.join(metadata_dir, 'splits.csv')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config.yaml", help="Path to config file")
    args = parser.parse_args()
    main(args.config)
