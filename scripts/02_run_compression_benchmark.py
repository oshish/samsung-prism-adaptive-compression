import os
import sys
import yaml
import argparse
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.preprocessing.image_loader import load_image
from src.compression.benchmark import run_codec_suite
from src.evaluation.metrics import evaluate_quality
from src.evaluation.artifact_analyzer import calculate_dark_metrics, detect_banding_score, calculate_edge_preservation
from src.utils.logger import setup_logger

logger = setup_logger("02_compression_benchmark")

def _benchmark_single_image(args):
    img_id, path, split, lossless_codecs, lossy_codecs, lossy_qualities = args
    img = load_image(path)
    
    bench_results = run_codec_suite(
        img,
        lossless_codecs=lossless_codecs,
        lossy_codecs=lossy_codecs,
        lossy_qualities=lossy_qualities
    )
    
    records = []
    for res in bench_results:
        q_metrics = evaluate_quality(img, res.decompressed_img)
        dark_metrics = calculate_dark_metrics(img, res.decompressed_img)
        banding = detect_banding_score(res.decompressed_img)
        edge_pres = calculate_edge_preservation(img, res.decompressed_img)
        
        records.append({
            "image_id": img_id,
            "split": split,
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
            "banding_score": banding,
            "edge_preservation": edge_pres
        })
    return records

def main(config_path: str = "configs/config.yaml", max_workers: int = 8):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    metadata_dir = config["paths"]["metadata_dir"]
    results_dir = config["paths"]["results_dir"]
    comp_results_dir = os.path.join(results_dir, "compression")
    os.makedirs(comp_results_dir, exist_ok=True)
    
    splits_path = os.path.join(metadata_dir, "splits.csv")
    splits_df = pd.read_csv(splits_path)
    
    comp_cfg = config["compression"]
    lossless_codecs = comp_cfg["lossless_codecs"]
    lossy_codecs = comp_cfg["lossy_codecs"]
    lossy_qualities = comp_cfg["lossy_quality_levels"]
    
    logger.info(f"Running rate-distortion compression benchmark across {len(splits_df)} images...")
    logger.info(f"Lossless codecs: {lossless_codecs} | Lossy codecs: {lossy_codecs} (Q={lossy_qualities})")
    
    tasks = [
        (row["image_id"], row["file_path"], row["split"], lossless_codecs, lossy_codecs, lossy_qualities)
        for _, row in splits_df.iterrows()
    ]
    
    all_records = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for result in tqdm(executor.map(_benchmark_single_image, tasks), total=len(tasks), desc="Benchmarking Codecs"):
            all_records.extend(result)
            
    df = pd.DataFrame(all_records)
    out_csv = os.path.join(metadata_dir, "compression_experiments.csv")
    results_csv = os.path.join(comp_results_dir, "compression_results.csv")
    df.to_csv(out_csv, index=False)
    df.to_csv(results_csv, index=False)
    
    logger.info(f"Compression benchmark completed. Recorded {len(df)} trials across {len(splits_df)} images.")
    logger.info(f"Saved to {out_csv} and {results_csv}")
    
    # Log summary statistics per codec
    summary = df.groupby(["codec", "quality"], dropna=False).agg({
        "compression_ratio": "mean",
        "encode_time_ms": "mean",
        "decode_time_ms": "mean",
        "psnr": "mean",
        "ssim": "mean",
        "dark_ssim": "mean",
        "edge_preservation": "mean"
    }).reset_index()
    logger.info("Summary Rate-Distortion & Latency Benchmarks:\n" + summary.to_string(index=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    main(args.config, max_workers=args.workers)
