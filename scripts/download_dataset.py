#!/usr/bin/env python3
"""
scripts/download_dataset.py
Step 1: Download and acquire approximately 1,000 diverse benchmark images.
"""

import os
import sys
import argparse

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.downloader import download_all_datasets
from src.utils.logger import setup_logger

logger = setup_logger("download_dataset")


def main():
    parser = argparse.ArgumentParser(description="Download and stage raw benchmark datasets (~1,000 images).")
    parser.add_argument("--raw-dir", default="data/raw", help="Path to raw data directory")
    parser.add_argument("--metadata-dir", default="data/metadata", help="Path to metadata directory")
    args = parser.parse_args()
    
    logger.info("Starting Step 1: Dataset Acquisition...")
    df_manifest = download_all_datasets(raw_dir=args.raw_dir, metadata_dir=args.metadata_dir)
    logger.info(f"Step 1 Complete. Staged {len(df_manifest)} raw images.")
    logger.info(f"Manifest written to: {os.path.join(args.metadata_dir, 'dataset_raw_manifest.csv')}")


if __name__ == "__main__":
    main()

