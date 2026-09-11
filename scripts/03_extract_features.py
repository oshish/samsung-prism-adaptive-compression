import os
import sys
import yaml
import argparse
import pandas as pd
from tqdm import tqdm

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.preprocessing.image_loader import load_image
from src.features.extractor import extract_features
from src.utils.logger import setup_logger

logger = setup_logger("03_extract_features")

def main(config_path: str = "configs/config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    metadata_dir = config["paths"]["metadata_dir"]
    splits_path = os.path.join(metadata_dir, "splits.csv")
    splits_df = pd.read_csv(splits_path)
    
    logger.info(f"Extracting pre-compression image features for {len(splits_df)} frames...")
    
    records = []
    for _, row in tqdm(splits_df.iterrows(), total=len(splits_df), desc="Extracting Features"):
        img_id = row["image_id"]
        path = row["file_path"]
        img = load_image(path)
        
        feats = extract_features(img, config=config.get("features", {}))
        record = {
            "image_id": img_id,
            "split": row["split"],
            **feats
        }
        records.append(record)
        
    df = pd.DataFrame(records)
    out_csv = os.path.join(metadata_dir, "features.csv")
    df.to_csv(out_csv, index=False)
    logger.info(f"Feature extraction completed. {len(df.columns) - 2} features saved to {out_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()
    main(args.config)
