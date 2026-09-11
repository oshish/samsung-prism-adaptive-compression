#!/usr/bin/env python3
"""
scripts/prepare_dataset.py
Steps 2 & 3: Clean, organize, and preprocess the dataset.
Detects corruptions, duplicates (SHA-256 and dHash), channel inconsistencies,
and saves verified, non-destructively preprocessed images into data/processed/.
"""

import os
import sys
import argparse

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.cleaner import clean_and_validate_dataset
from src.utils.logger import setup_logger

logger = setup_logger("prepare_dataset")


def main():
    parser = argparse.ArgumentParser(description="Clean, deduplicate, and organize benchmark dataset.")
    parser.add_argument("--raw-dir", default="data/raw", help="Path to raw data directory")
    parser.add_argument("--processed-dir", default="data/processed", help="Path to processed data directory")
    parser.add_argument("--metadata-dir", default="data/metadata", help="Path to metadata directory")
    args = parser.parse_args()
    
    logger.info("Starting Steps 2 & 3: Dataset Cleaning and Preprocessing...")
    df_clean, summary = clean_and_validate_dataset(
        raw_dir=args.raw_dir,
        processed_dir=args.processed_dir,
        metadata_dir=args.metadata_dir
    )
    
    logger.info(f"Cleaning complete. Valid usable images: {summary['valid_images']}")
    logger.info(f"Cleaning log saved to {os.path.join(args.metadata_dir, 'cleaning_log.csv')}")


if __name__ == "__main__":
    main()

