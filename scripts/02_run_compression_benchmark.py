import os
import sys
import yaml
import argparse
import pandas as pd
from tqdm import tqdm

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.preprocessing.image_loader import load_image
from src.compression.benchmark import run_codec_suite
from src.evaluation.metrics import evaluate_quality
from src.evaluation.artifact_analyzer import calculate_dark_metrics, detect_banding_score
from src.utils.logger import setup_logger

logger = setup_logger("02_compression_benchmark")

def main(config_path: str = "configs/config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    metadata_dir = config["paths"]["metadata_dir"]
    splits_path = os.path.join(metadata_dir, "splits.csv")
    splits_df = pd.read_csv(splits_path)
    
    comp_cfg = config["compression"]
    lossless_codecs = comp_cfg["lossless_codecs"]
    lossy_codecs = comp_cfg["lossy_codecs"]
    lossy_qualities = comp_cfg["lossy_quality_levels"]
    
    logger.info(f"Running rate-distortion compression benchmark across {len(splits_df)} images...")
    
    records = []
    for _, row in tqdm(splits_df.iterrows(), total=len(splits_df), desc="Benchmarking Codecs"):
        img_id = row["image_id"]
        path = row["file_path"]
        img = load_image(path)
        
        bench_results = run_codec_suite(
            img,
            lossless_codecs=lossless_codecs,
            lossy_codecs=lossy_codecs,
            lossy_qualities=lossy_qualities
        )
        
        for res in bench_results:
            q_metrics = evaluate_quality(img, res.decompressed_img)
            dark_metrics = calculate_dark_metrics(img, res.decompressed_img)
            banding = detect_banding_score(res.decompressed_img)
            
            records.append({
                "image_id": img_id,
                "split": row["split"],
                "codec": res.codec,
                "is_lossy": res.is_lossy,
                "quality": res.quality,
                "raw_bytes": res.raw_bytes,
                "compressed_bytes": res.compressed_bytes,
                "compression_ratio": res.compression_ratio,
                "encode_time_ms": res.encode_time_ms,
                "decode_time_ms": res.decode_time_ms,
                "mse": q_metrics["mse"],
                "psnr": q_metrics["psnr"],
                "ssim": q_metrics["ssim"],
                "dark_ssim": dark_metrics["dark_ssim"],
                "dark_psnr": dark_metrics["dark_psnr"],
                "banding_score": banding
            })
            
    df = pd.DataFrame(records)
    out_csv = os.path.join(metadata_dir, "compression_experiments.csv")
    df.to_csv(out_csv, index=False)
    logger.info(f"Compression benchmark completed. Recorded {len(df)} trials to {out_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()
    main(args.config)
