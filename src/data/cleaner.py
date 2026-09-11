"""
src/data/cleaner.py
Automated cleaning and organization pipeline for raw benchmark images.
Validates file integrity, detects duplicates (SHA-256 and dHash),
handles color channels (converts grayscale/alpha to standardized RGB),
and preserves raw images while staging verified frames in data/processed/.
"""

import os
import hashlib
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image
from tqdm import tqdm


def compute_sha256(filepath: str) -> str:
    """Computes SHA-256 cryptographic hash of file contents."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_dhash(image: Image.Image, hash_size: int = 8) -> str:
    """
    Computes difference hash (dHash) to detect exact visual duplicates.
    """
    # Resize to (hash_size + 1, hash_size) grayscale
    resized = image.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = np.array(resized, dtype=np.float32)
    # Compare adjacent horizontal pixels
    diff = pixels[:, 1:] > pixels[:, :-1]
    # Convert bool array to hex string
    decimal_val = 0
    hex_str = []
    for index, val in enumerate(diff.flatten()):
        if val:
            decimal_val += 2 ** (index % 4)
        if (index % 4) == 3:
            hex_str.append(f"{decimal_val:x}")
            decimal_val = 0
    return "".join(hex_str)


def clean_and_validate_dataset(
    raw_dir: str,
    processed_dir: str,
    metadata_dir: str,
    min_dimension: int = 32,
    max_aspect_ratio: float = 10.0
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Processes all raw images, applies integrity validation, removes duplicates,
    standardizes color channels to 3-channel RGB uint8, and outputs to processed_dir.
    
    Returns:
        (cleaning_log_df, summary_stats_dict)
    """
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(metadata_dir, exist_ok=True)
    
    raw_files = []
    for root, _, files in os.walk(raw_dir):
        for f in files:
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp")):
                raw_files.append(os.path.join(root, f))
                
    raw_files.sort()
    print(f"Discovered {len(raw_files)} candidate raw images for cleaning.")
    
    seen_sha256: Dict[str, str] = {}
    seen_dhash: Dict[str, str] = {}
    cleaning_records: List[Dict[str, Any]] = []
    
    valid_count = 0
    corrupt_count = 0
    exact_duplicate_count = 0
    visual_duplicate_count = 0
    dimension_rejected_count = 0
    grayscale_converted_count = 0
    alpha_stripped_count = 0
    
    for raw_path in tqdm(raw_files, desc="Cleaning & Validating Images"):
        filename = os.path.basename(raw_path)
        image_id = os.path.splitext(filename)[0]
        
        # 1. SHA-256 Exact Duplicate Check
        try:
            sha256 = compute_sha256(raw_path)
        except Exception as e:
            cleaning_records.append({
                "image_id": image_id,
                "raw_path": raw_path,
                "status": "CORRUPT",
                "action": "SKIPPED",
                "reason": f"File read failure: {str(e)}",
                "sha256": "",
                "dhash": "",
                "is_grayscale": False
            })
            corrupt_count += 1
            continue
            
        if sha256 in seen_sha256:
            orig_id = seen_sha256[sha256]
            cleaning_records.append({
                "image_id": image_id,
                "raw_path": raw_path,
                "status": "DUPLICATE",
                "action": "SKIPPED",
                "reason": f"Exact byte-level duplicate of {orig_id}",
                "sha256": sha256,
                "dhash": "",
                "is_grayscale": False
            })
            exact_duplicate_count += 1
            continue
            
        seen_sha256[sha256] = image_id
        
        # 2. Image Load and Decode Integrity Check
        try:
            with Image.open(raw_path) as img:
                img.load()  # Force decode compressed bitstream
                raw_mode = img.mode
                w, h = img.size
                
                # Check for degenerate dimensions
                if w < min_dimension or h < min_dimension:
                    cleaning_records.append({
                        "image_id": image_id,
                        "raw_path": raw_path,
                        "status": "INVALID_DIMENSIONS",
                        "action": "SKIPPED",
                        "reason": f"Image dimension too small: {w}x{h} (min: {min_dimension})",
                        "sha256": sha256,
                        "dhash": "",
                        "is_grayscale": False
                    })
                    dimension_rejected_count += 1
                    continue
                    
                aspect_ratio = max(w / h, h / w)
                if aspect_ratio > max_aspect_ratio:
                    cleaning_records.append({
                        "image_id": image_id,
                        "raw_path": raw_path,
                        "status": "INVALID_DIMENSIONS",
                        "action": "SKIPPED",
                        "reason": f"Extreme aspect ratio: {aspect_ratio:.2f} > {max_aspect_ratio}",
                        "sha256": sha256,
                        "dhash": "",
                        "is_grayscale": False
                    })
                    dimension_rejected_count += 1
                    continue
                    
                # Compute dHash for visual duplicate check
                dhash = compute_dhash(img)
                if dhash in seen_dhash:
                    orig_id = seen_dhash[dhash]
                    cleaning_records.append({
                        "image_id": image_id,
                        "raw_path": raw_path,
                        "status": "VISUAL_DUPLICATE",
                        "action": "SKIPPED",
                        "reason": f"Exact perceptual duplicate (dHash match) of {orig_id}",
                        "sha256": sha256,
                        "dhash": dhash,
                        "is_grayscale": False
                    })
                    visual_duplicate_count += 1
                    continue
                seen_dhash[dhash] = image_id
                
                # 3. Channel Standardization
                is_grayscale = False
                action = "KEPT_UNCHANGED"
                
                if raw_mode in ("L", "1"):
                    is_grayscale = True
                    # Standardize to 3-channel RGB (identical planes)
                    rgb_img = img.convert("RGB")
                    action = "CONVERTED_FROM_GRAYSCALE"
                    grayscale_converted_count += 1
                elif raw_mode in ("RGBA", "LA", "PA"):
                    # Strip or composite alpha over neutral 50% gray background
                    bg = Image.new("RGB", img.size, (128, 128, 128))
                    if raw_mode == "RGBA":
                        bg.paste(img, mask=img.split()[3])
                    else:
                        bg.paste(img.convert("RGB"))
                    rgb_img = bg
                    action = "ALPHA_COMPOSITED"
                    alpha_stripped_count += 1
                elif raw_mode == "RGB":
                    # Check if RGB actually contains identical channels (grayscale saved as RGB)
                    arr = np.array(img, dtype=np.uint8)
                    if np.array_equal(arr[..., 0], arr[..., 1]) and np.array_equal(arr[..., 0], arr[..., 2]):
                        is_grayscale = True
                    rgb_img = img
                else:
                    rgb_img = img.convert("RGB")
                    action = f"CONVERTED_FROM_{raw_mode}"
                    
                # 4. Save to processed directory in lossless PNG format
                out_filename = f"{image_id}.png"
                out_path = os.path.join(processed_dir, out_filename)
                rgb_img.save(out_path, format="PNG")
                
                cleaning_records.append({
                    "image_id": image_id,
                    "raw_path": raw_path,
                    "processed_path": out_path,
                    "status": "VALID",
                    "action": action,
                    "reason": "Passed all integrity and duplicate checks",
                    "sha256": sha256,
                    "dhash": dhash,
                    "width": w,
                    "height": h,
                    "raw_mode": raw_mode,
                    "processed_mode": "RGB",
                    "is_grayscale": is_grayscale,
                    "processed_size_bytes": os.path.getsize(out_path)
                })
                valid_count += 1
                
        except Exception as e:
            cleaning_records.append({
                "image_id": image_id,
                "raw_path": raw_path,
                "status": "CORRUPT",
                "action": "SKIPPED",
                "reason": f"Decode error: {str(e)}",
                "sha256": sha256,
                "dhash": "",
                "is_grayscale": False
            })
            corrupt_count += 1

    df_cleaning = pd.DataFrame(cleaning_records)
    log_path = os.path.join(metadata_dir, "cleaning_log.csv")
    df_cleaning.to_csv(log_path, index=False)
    
    summary = {
        "total_raw_scanned": len(raw_files),
        "valid_images": valid_count,
        "corrupt_images": corrupt_count,
        "exact_duplicates": exact_duplicate_count,
        "visual_duplicates": visual_duplicate_count,
        "dimension_rejected": dimension_rejected_count,
        "grayscale_converted": grayscale_converted_count,
        "alpha_composited": alpha_stripped_count
    }
    
    print("\n--- DATASET CLEANING & VALIDATION SUMMARY ---")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print(f"Detailed cleaning log written to: {log_path}\n")
    
    return df_cleaning, summary

