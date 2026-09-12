import numpy as np
import pandas as pd
from typing import Dict, Any, List

def evaluate_system_impact(
    test_metadata: pd.DataFrame,
    predictions: Dict[str, np.ndarray],
    ssim_threshold: float = 0.94,
    psnr_threshold: float = 33.0,
    dark_ssim_threshold: float = 0.90
) -> Dict[str, Any]:
    """
    Evaluates the real-world engineering objective:
    How does each strategy (Always Lossless, Always Lossy, Heuristic, ML, Oracle)
    perform in terms of:
    - Total Storage (MB)
    - Memory Saving % over raw uncompressed frame buffer
    - Memory Saving % over Always Lossless
    - Mean Quality (SSIM and PSNR)
    - Critical Artifact / Quality Failure Rate
    """
    total_raw_bytes = float(test_metadata["raw_bytes"].sum())
    total_lossless_bytes = float(test_metadata["lossless_bytes"].sum())
    total_lossy_bytes = float(test_metadata["lossy_bytes"].sum())
    num_samples = len(test_metadata)
    
    strategies: Dict[str, Any] = {}
    
    # 1. Always Lossless
    strategies["always_lossless"] = {
        "total_mb": total_lossless_bytes / (1024 * 1024),
        "saving_vs_raw_pct": 100.0 * (1.0 - total_lossless_bytes / total_raw_bytes),
        "saving_vs_lossless_pct": 0.0,
        "mean_ssim": 1.0,
        "mean_psnr": 100.0,
        "critical_failures": 0,
        "critical_failure_rate": 0.0
    }
    
    # 2. Always Lossy
    lossy_failures = 0
    lossy_ssims = []
    lossy_psnrs = []
    for _, row in test_metadata.iterrows():
        is_bad = (row["ssim"] < ssim_threshold) or (row["psnr"] < psnr_threshold) or (row["dark_ssim"] < dark_ssim_threshold)
        if is_bad:
            lossy_failures += 1
        lossy_ssims.append(row["ssim"])
        lossy_psnrs.append(row["psnr"])
        
    strategies["always_lossy"] = {
        "total_mb": total_lossy_bytes / (1024 * 1024),
        "saving_vs_raw_pct": 100.0 * (1.0 - total_lossy_bytes / total_raw_bytes),
        "saving_vs_lossless_pct": 100.0 * (1.0 - total_lossy_bytes / total_lossless_bytes),
        "mean_ssim": float(np.mean(lossy_ssims)),
        "mean_psnr": float(np.mean(lossy_psnrs)),
        "critical_failures": lossy_failures,
        "critical_failure_rate": float(lossy_failures / max(1, num_samples))
    }
    
    # 3. Model Strategies
    for model_name, preds in predictions.items():
        chosen_bytes = 0.0
        chosen_ssims = []
        chosen_psnrs = []
        critical_fails = 0
        
        for idx, (_, row) in enumerate(test_metadata.iterrows()):
            chose_lossy = (preds[idx] == 1)
            if chose_lossy:
                chosen_bytes += row["lossy_bytes"]
                chosen_ssims.append(row["ssim"])
                chosen_psnrs.append(row["psnr"])
                is_bad = (row["ssim"] < ssim_threshold) or (row["psnr"] < psnr_threshold) or (row["dark_ssim"] < dark_ssim_threshold)
                if is_bad:
                    critical_fails += 1
            else:
                chosen_bytes += row["lossless_bytes"]
                chosen_ssims.append(1.0)
                chosen_psnrs.append(100.0) # pristine reconstruction
                
        strategies[model_name] = {
            "total_mb": chosen_bytes / (1024 * 1024),
            "saving_vs_raw_pct": 100.0 * (1.0 - chosen_bytes / total_raw_bytes),
            "saving_vs_lossless_pct": 100.0 * (1.0 - chosen_bytes / total_lossless_bytes),
            "mean_ssim": float(np.mean(chosen_ssims)),
            "mean_psnr": float(np.mean(chosen_psnrs)),
            "critical_failures": critical_fails,
            "critical_failure_rate": float(critical_fails / max(1, num_samples))
        }
        
    return {
        "num_test_frames": num_samples,
        "total_raw_mb": total_raw_bytes / (1024 * 1024),
        "strategies": strategies
    }
