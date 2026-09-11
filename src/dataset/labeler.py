import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from ..preprocessing.image_loader import load_image, validate_image
from ..compression.codecs import compress_image, decompress_image
from ..evaluation.metrics import evaluate_quality
from ..evaluation.artifact_analyzer import calculate_dark_metrics, detect_banding_score

def generate_ground_truth_label(
    rgb_img: np.ndarray,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Derives the empirical ground-truth label (LOSSY vs LOSSLESS) for a single image.
    
    EVALUATION CRITERIA:
    1. Lossless compression (PNG) establishes baseline size S_lossless.
    2. Lossy compression (JPEG, Q=75) yields S_lossy, PSNR, SSIM, and Dark-SSIM.
    3. Size savings ratio: R = (S_lossless - S_lossy) / S_lossless.
    4. An image is labeled LOSSY if and only if:
       - SSIM >= ssim_threshold (default 0.95)
       - PSNR >= psnr_threshold (default 34.0 dB)
       - R >= min_size_saving (default 0.25)
       - Dark-SSIM >= dark_ssim_threshold (default 0.92)
       Otherwise: LOSSLESS.
       
    ALL THRESHOLDS ARE MARKED: ASSUMPTION — REQUIRES MENTOR CONFIRMATION
    """
    validate_image(rgb_img)
    cfg = config or {}
    label_cfg = cfg.get("labeling", {})
    comp_cfg = cfg.get("compression", {})
    
    ssim_thresh = label_cfg.get("ssim_threshold", 0.95)
    psnr_thresh = label_cfg.get("psnr_threshold", 34.0)
    min_saving = label_cfg.get("min_size_saving", 0.25)
    dark_ssim_thresh = label_cfg.get("dark_ssim_threshold", 0.92)
    dark_cutoff = label_cfg.get("dark_pixel_cutoff", 40.0)
    
    lossless_codec = comp_cfg.get("default_lossless_codec", "png")
    lossy_codec = comp_cfg.get("default_lossy_codec", "jpeg")
    lossy_q = comp_cfg.get("default_lossy_quality", 75)
    
    raw_bytes = int(rgb_img.nbytes)
    
    # 1. Lossless compression
    lossless_bytes = compress_image(rgb_img, codec=lossless_codec)
    s_lossless = len(lossless_bytes)
    cr_lossless = float(raw_bytes / max(1, s_lossless))
    
    # 2. Lossy compression
    lossy_bytes = compress_image(rgb_img, codec=lossy_codec, quality=lossy_q)
    s_lossy = len(lossy_bytes)
    cr_lossy = float(raw_bytes / max(1, s_lossy))
    lossy_decomp = decompress_image(lossy_bytes)
    
    # 3. Quality evaluation
    q_metrics = evaluate_quality(rgb_img, lossy_decomp)
    psnr = q_metrics["psnr"]
    ssim = q_metrics["ssim"]
    
    # 4. Artifact evaluation
    dark_metrics = calculate_dark_metrics(rgb_img, lossy_decomp, dark_cutoff=dark_cutoff)
    dark_ssim = dark_metrics["dark_ssim"]
    banding_score = detect_banding_score(lossy_decomp)
    
    # 5. Storage savings ratio
    size_saving_ratio = float((s_lossless - s_lossy) / max(1, s_lossless))
    
    # 6. Ground-Truth Decision
    quality_passed = (ssim >= ssim_thresh) and (psnr >= psnr_thresh)
    saving_passed = size_saving_ratio >= min_saving
    dark_passed = dark_ssim >= dark_ssim_thresh
    
    is_lossy = quality_passed and saving_passed and dark_passed
    label = "LOSSY" if is_lossy else "LOSSLESS"
    
    return {
        "raw_bytes": raw_bytes,
        "lossless_codec": lossless_codec,
        "lossless_bytes": s_lossless,
        "lossless_cr": cr_lossless,
        "lossy_codec": lossy_codec,
        "lossy_quality": lossy_q,
        "lossy_bytes": s_lossy,
        "lossy_cr": cr_lossy,
        "size_saving_ratio": size_saving_ratio,
        "psnr": psnr,
        "ssim": ssim,
        "dark_ssim": dark_ssim,
        "banding_score": banding_score,
        "quality_passed": bool(quality_passed),
        "saving_passed": bool(saving_passed),
        "dark_passed": bool(dark_passed),
        "label": label,
        "is_lossy_binary": int(is_lossy)
    }

def build_labeled_dataset(
    splits_df: pd.DataFrame,
    config: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Iterates through dataset splits, generates ground-truth labels and metadata.
    """
    records = []
    for _, row in splits_df.iterrows():
        img_id = row["image_id"]
        path = row["file_path"]
        split = row["split"]
        
        img = load_image(path)
        label_info = generate_ground_truth_label(img, config=config)
        
        record = {
            "image_id": img_id,
            "file_path": path,
            "split": split,
            **label_info
        }
        records.append(record)
        
    return pd.DataFrame(records)
