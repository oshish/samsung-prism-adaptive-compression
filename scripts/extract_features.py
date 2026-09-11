#!/usr/bin/env python3
"""
scripts/extract_features.py
Steps 4 & 5: Feature Extraction from RGB and YUV representations.
Generates master feature dataset: data/metadata/image_features.csv.
Guarantees zero target leakage (no compression results, no labels).
"""

import os
import sys
import argparse
import pandas as pd
from tqdm import tqdm

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.preprocessing.image_loader import load_image
from src.features.extractor import extract_features
from src.utils.logger import setup_logger

logger = setup_logger("extract_features")


def main():
    parser = argparse.ArgumentParser(description="Extract pre-compression features across all processed images.")
    parser.add_argument("--processed-dir", default="data/processed", help="Path to processed image directory")
    parser.add_argument("--metadata-dir", default="data/metadata", help="Path to metadata directory")
    parser.add_argument("--output-csv", default="data/metadata/image_features.csv", help="Path for output master CSV")
    args = parser.parse_args()
    
    logger.info("Starting Steps 4 & 5: RGB/YUV Feature Extraction...")
    
    if not os.path.exists(args.processed_dir):
        logger.error(f"Processed directory '{args.processed_dir}' does not exist. Run scripts/prepare_dataset.py first.")
        sys.exit(1)
        
    image_files = [
        os.path.join(args.processed_dir, f)
        for f in sorted(os.listdir(args.processed_dir))
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]
    
    if not image_files:
        logger.error(f"No valid images found in '{args.processed_dir}'.")
        sys.exit(1)
        
    logger.info(f"Found {len(image_files)} processed images. Extracting features...")
    
    records = []
    for img_path in tqdm(image_files, desc="Extracting Features"):
        filename = os.path.basename(img_path)
        image_id = os.path.splitext(filename)[0]
        
        try:
            rgb_arr = load_image(img_path)
            feats = extract_features(rgb_arr)
            
            # Row schema: image_id, path, followed by extracted features
            row = {
                "image_id": image_id,
                "file_path": img_path,
                **feats
            }
            records.append(row)
        except Exception as e:
            logger.warning(f"Feature extraction failed for {filename}: {e}")
            
    df_features = pd.DataFrame(records)
    
    # Save master CSV
    os.makedirs(os.path.dirname(os.path.abspath(args.output_csv)), exist_ok=True)
    df_features.to_csv(args.output_csv, index=False)
    
    # Also save copy to data/metadata/features.csv for compatibility
    compat_csv = os.path.join(args.metadata_dir, "features.csv")
    df_features.to_csv(compat_csv, index=False)
    
    logger.info(f"Feature extraction successfully completed!")
    logger.info(f"Total images processed: {len(df_features)}")
    logger.info(f"Feature count (including metadata): {len(df_features.columns)}")
    logger.info(f"Master feature CSV saved to: {args.output_csv}")


if __name__ == "__main__":
    main()

