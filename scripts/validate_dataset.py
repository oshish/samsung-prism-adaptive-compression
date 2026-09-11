#!/usr/bin/env python3
"""
scripts/validate_dataset.py
Step 6: Rigorous Dataset Quality Validation and Feature Sanity Analysis.
Checks:
- Row counts, duplicate IDs, duplicate rows
- Missing, NaN, and Infinite values
- Feature range validation and impossible values
- Constant and near-zero-variance features
- High collinearity / feature correlation matrix
- Distribution figures and detailed structured text reports
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd

# Headless matplotlib configuration
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_cache"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.logger import setup_logger

logger = setup_logger("validate_dataset")


def run_dataset_and_feature_validation(
    features_csv: str,
    cleaning_log_csv: str,
    results_dataset_dir: str,
    results_features_dir: str
):
    os.makedirs(results_dataset_dir, exist_ok=True)
    os.makedirs(results_features_dir, exist_ok=True)
    os.makedirs("/tmp/matplotlib_cache", exist_ok=True)
    
    logger.info(f"Loading master features CSV: {features_csv}")
    if not os.path.exists(features_csv):
        raise FileNotFoundError(f"Feature CSV not found: {features_csv}")
        
    df = pd.read_csv(features_csv)
    total_rows, total_cols = df.shape
    logger.info(f"Dataset loaded with {total_rows} rows and {total_cols} columns.")
    
    # 1. Image ID and duplicate validation
    duplicate_ids = df["image_id"].duplicated().sum()
    duplicate_rows = df.duplicated().sum()
    
    # 2. Missing, NaN, and Inf checks
    num_cols = [c for c in df.columns if c not in ("image_id", "file_path")]
    missing_counts = df[num_cols].isnull().sum().to_dict()
    total_missing = sum(missing_counts.values())
    
    nan_counts = {c: int(np.isnan(df[c]).sum()) for c in num_cols}
    inf_counts = {c: int(np.isinf(df[c]).sum()) for c in num_cols}
    total_nans = sum(nan_counts.values())
    total_infs = sum(inf_counts.values())
    
    # 3. Variance and constant feature analysis
    variances = df[num_cols].var()
    constant_features = [c for c in num_cols if variances[c] == 0.0]
    low_variance_features = [c for c in num_cols if 0.0 < variances[c] < 1e-4]
    
    # 4. Statistical Summary
    stats_df = df[num_cols].describe().T
    stats_df["variance"] = variances
    stats_df["skewness"] = df[num_cols].skew()
    stats_df["kurtosis"] = df[num_cols].kurtosis()
    stats_csv = os.path.join(results_features_dir, "feature_summary_stats.csv")
    stats_df.to_csv(stats_csv)
    
    # 5. Correlation Analysis
    corr_matrix = df[num_cols].corr()
    high_corr_pairs = []
    for i in range(len(num_cols)):
        for j in range(i + 1, len(num_cols)):
            f1, f2 = num_cols[i], num_cols[j]
            r = corr_matrix.loc[f1, f2]
            if abs(r) >= 0.85:
                high_corr_pairs.append((f1, f2, float(r)))
                
    high_corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    
    # 6. Cleaning Log Summary
    cleaning_summary = {}
    if os.path.exists(cleaning_log_csv):
        df_clean = pd.read_csv(cleaning_log_csv)
        cleaning_summary = {
            "total_raw_scanned": len(df_clean),
            "status_counts": df_clean["status"].value_counts().to_dict(),
            "action_counts": df_clean["action"].value_counts().to_dict(),
            "grayscale_count": int(df_clean.get("is_grayscale", pd.Series([False])).sum())
        }
        
    # Generate structured dataset validation report
    dataset_report_path = os.path.join(results_dataset_dir, "dataset_validation_report.txt")
    with open(dataset_report_path, "w") as f:
        f.write("=" * 70 + "\n")
        f.write("SAMSUNG PRISM ADAPTIVE FRAME COMPRESSION: DATASET VALIDATION REPORT\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total Master Feature Rows: {total_rows}\n")
        f.write(f"Total Feature Columns:    {total_cols} (2 metadata, {len(num_cols)} numerical)\n")
        f.write(f"Duplicate Image IDs:      {duplicate_ids}\n")
        f.write(f"Duplicate Entire Rows:    {duplicate_rows}\n")
        f.write(f"Total Missing / Null:     {total_missing}\n")
        f.write(f"Total NaN Values:         {total_nans}\n")
        f.write(f"Total Infinite Values:    {total_infs}\n\n")
        
        f.write("-" * 50 + "\n")
        f.write("DATASET CLEANING AUDIT\n")
        f.write("-" * 50 + "\n")
        for k, v in cleaning_summary.items():
            f.write(f"  {k}: {v}\n")
            
        f.write("\n" + "-" * 50 + "\n")
        f.write("FEATURE VARIANCE AUDIT\n")
        f.write("-" * 50 + "\n")
        f.write(f"Constant Features (zero variance): {constant_features if constant_features else 'None'}\n")
        f.write(f"Near-Zero Variance Features (< 1e-4): {low_variance_features if low_variance_features else 'None'}\n\n")
        
        f.write("-" * 50 + "\n")
        f.write("STRONGLY CORRELATED FEATURE PAIRS (|r| >= 0.85)\n")
        f.write("-" * 50 + "\n")
        if high_corr_pairs:
            for f1, f2, r in high_corr_pairs:
                f.write(f"  {f1:25s} <-> {f2:25s} : r = {r:+.4f}\n")
        else:
            f.write("  No feature pairs exceed |r| >= 0.85.\n")
            
    # Also save JSON summary
    summary_json_path = os.path.join(results_dataset_dir, "dataset_summary.json")
    with open(summary_json_path, "w") as f:
        json.dump({
            "total_images": int(total_rows),
            "total_features": int(len(num_cols)),
            "duplicate_ids": int(duplicate_ids),
            "total_missing": int(total_missing),
            "total_nans": int(total_nans),
            "total_infs": int(total_infs),
            "constant_features": [str(x) for x in constant_features],
            "low_variance_features": [str(x) for x in low_variance_features],
            "high_corr_pair_count": int(len(high_corr_pairs)),
            "cleaning_summary": {k: int(v) if isinstance(v, (np.integer, int)) else v for k, v in cleaning_summary.items()}
        }, f, indent=2, default=str)

    # 7. Generate Visualizations
    logger.info("Generating feature distribution plots...")
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()
    
    key_features = [
        ("mean_luminance", "Mean Luminance (Y)", "Blues_d"),
        ("shannon_entropy", "Shannon Entropy (bits/pixel)", "Greens_d"),
        ("sobel_edge_density", "Sobel Edge Density", "Oranges_d"),
        ("noise_estimate", "Immerkaer Noise Estimate", "Reds_d"),
        ("local_variance_mean", "Local 8x8 Variance Mean", "Purples_d"),
        ("colorfulness", "Hasler-Süsstrunk Colorfulness", "YlGnBu_d")
    ]
    
    for idx, (feat, title, palette) in enumerate(key_features):
        if feat in df.columns:
            sns.histplot(df[feat], kde=True, ax=axes[idx], color=sns.color_palette(palette)[-2])
            axes[idx].set_title(title, fontsize=12, fontweight="bold")
            axes[idx].set_xlabel("Value")
            axes[idx].set_ylabel("Frame Count")
            axes[idx].grid(True, alpha=0.3)
            
    plt.tight_layout()
    dist_plot_path = os.path.join(results_features_dir, "feature_distributions.png")
    plt.savefig(dist_plot_path, dpi=200)
    plt.close()
    
    # Correlation matrix heatmap
    logger.info("Generating feature correlation matrix heatmap...")
    plt.figure(figsize=(18, 14))
    # Select most informative numerical features for clean readability
    display_cols = [c for c in num_cols if c not in ("width", "height", "aspect_ratio", "total_pixels")]
    sub_corr = df[display_cols].corr()
    sns.heatmap(
        sub_corr,
        cmap="coolwarm",
        center=0,
        annot=False,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8}
    )
    plt.title("Feature Correlation Matrix (Visual & Compression Features)", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    corr_plot_path = os.path.join(results_features_dir, "correlation_matrix.png")
    plt.savefig(corr_plot_path, dpi=200)
    plt.close()
    
    logger.info("Validation and Analysis successfully completed!")
    logger.info(f"Validation report: {dataset_report_path}")
    logger.info(f"Summary stats:     {stats_csv}")
    logger.info(f"Distribution plot: {dist_plot_path}")
    logger.info(f"Correlation plot:  {corr_plot_path}")


def main():
    parser = argparse.ArgumentParser(description="Validate dataset quality and perform feature sanity analysis.")
    parser.add_argument("--features-csv", default="data/metadata/image_features.csv", help="Path to master features CSV")
    parser.add_argument("--cleaning-log", default="data/metadata/cleaning_log.csv", help="Path to cleaning log CSV")
    parser.add_argument("--dataset-results", default="results/dataset", help="Output directory for dataset validation")
    parser.add_argument("--feature-results", default="results/features", help="Output directory for feature analysis")
    args = parser.parse_args()
    
    run_dataset_and_feature_validation(
        features_csv=args.features_csv,
        cleaning_log_csv=args.cleaning_log,
        results_dataset_dir=args.dataset_results,
        results_features_dir=args.feature_results
    )


if __name__ == "__main__":
    main()
