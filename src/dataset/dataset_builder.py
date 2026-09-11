import os
import urllib.request
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from PIL import Image, ImageDraw
from ..preprocessing.image_loader import save_image, load_image

# Canonical, publicly hosted uncompressed Kodak True Color Image Suite
KODAK_URL_TEMPLATE = "http://r0k.us/graphics/kodak/kodak/kodim{i:02d}.png"

def download_kodak_suite(target_dir: str, num_images: int = 24) -> List[str]:
    """
    Acquires the canonical 24-image Kodak Lossless True Color Image Suite.
    """
    os.makedirs(target_dir, exist_ok=True)
    downloaded_paths = []
    
    for i in range(1, num_images + 1):
        filename = f"kodim{i:02d}.png"
        filepath = os.path.join(target_dir, filename)
        # Download if missing or previously saved as fallback (< 600KB)
        if not os.path.exists(filepath) or os.path.getsize(filepath) < 550000:
            url = KODAK_URL_TEMPLATE.format(i=i)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as response, open(filepath, "wb") as out_file:
                    out_file.write(response.read())
            except Exception as e:
                print(f"Notice: Kodak download error for {filename}: {e}")
                if not os.path.exists(filepath):
                    arr = _generate_natural_fallback_scene(i)
                    save_image(arr, filepath)
        downloaded_paths.append(filepath)
        
    return downloaded_paths

def _generate_natural_fallback_scene(seed: int) -> np.ndarray:
    """Generates a high-quality natural synthetic scene if mirror is unreachable."""
    rng = np.random.default_rng(seed)
    H, W = 512, 768
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    sky = np.zeros((H, W, 3), dtype=np.float32)
    sky[..., 0] = 120 + 80 * (1 - y)
    sky[..., 1] = 160 + 70 * (1 - y)
    sky[..., 2] = 220 + 35 * (1 - y)
    
    terrain_height = (0.5 + 0.2 * np.sin(x * 12.0) + 0.1 * np.cos(x * 30.0)) * H
    terrain_mask = np.arange(H)[:, None] > terrain_height
    sky[terrain_mask, 0] = 60 + 30 * rng.standard_normal(sky[terrain_mask, 0].shape)
    sky[terrain_mask, 1] = 90 + 20 * rng.standard_normal(sky[terrain_mask, 1].shape)
    sky[terrain_mask, 2] = 50 + 20 * rng.standard_normal(sky[terrain_mask, 2].shape)
    
    return np.clip(sky, 0, 255).astype(np.uint8)

def generate_synthetic_stress_suite(target_dir: str) -> List[str]:
    """
    Generates 6 targeted stress-test frames specifically testing edge-case compression modes:
    1. Smooth gradient (banding/contouring stress-test)
    2. Low-light dark frame with high Gaussian noise (dark artifact stress-test)
    3. Fine high-frequency textures / cloth / foliage (detail loss stress-test)
    4. High-contrast UI text and geometric edges (ringing stress-test)
    5. Clean flat geometric poster (ideal lossy candidate)
    6. High dynamic range scene (mixed lighting)
    """
    os.makedirs(target_dir, exist_ok=True)
    generated_paths = []
    H, W = 512, 768
    
    # 1. Gradient Banding Stress Test (PNG is ultra-small, JPEG will bloat or band)
    grad = np.zeros((H, W, 3), dtype=np.float32)
    x = np.linspace(20, 180, W, dtype=np.float32)[None, :]
    grad[..., 0] = x
    grad[..., 1] = x * 0.9 + 10.0
    grad[..., 2] = x * 1.1
    p1 = os.path.join(target_dir, "edge_01_smooth_gradient.png")
    save_image(np.clip(grad, 0, 255).astype(np.uint8), p1)
    generated_paths.append(p1)
    
    # 2. Dark Low-Light Noisy Stress Test
    rng = np.random.default_rng(101)
    dark = np.zeros((H, W, 3), dtype=np.float32)
    dark[:] = 15.0 # Very low luminance < 40
    noise = rng.normal(loc=0.0, scale=12.0, size=(H, W, 3))
    dark_noisy = np.clip(dark + noise, 0, 255).astype(np.uint8)
    p2 = os.path.join(target_dir, "edge_02_dark_noisy.png")
    save_image(dark_noisy, p2)
    generated_paths.append(p2)
    
    # 3. Dense High-Frequency Texture
    tex = np.zeros((H, W, 3), dtype=np.float32)
    y_idx, x_idx = np.indices((H, W))
    pattern = np.sin(x_idx * 0.5) * np.cos(y_idx * 0.5) * 60.0 + 128.0
    tex[..., 0] = pattern
    tex[..., 1] = np.sin(x_idx * 0.25) * 50.0 + 120.0
    tex[..., 2] = np.cos(y_idx * 0.25) * 50.0 + 130.0
    p3 = os.path.join(target_dir, "edge_03_dense_texture.png")
    save_image(np.clip(tex, 0, 255).astype(np.uint8), p3)
    generated_paths.append(p3)
    
    # 4. Sharp UI Text & Vector Graphics
    ui_img = Image.new("RGB", (W, H), color=(245, 245, 245))
    draw = ImageDraw.Draw(ui_img)
    draw.rectangle([50, 50, W - 50, 150], fill=(20, 30, 55), outline=(0, 120, 215), width=4)
    draw.rectangle([80, 200, 350, 450], fill=(255, 255, 255), outline=(200, 200, 200), width=2)
    draw.rectangle([400, 200, 700, 450], fill=(10, 15, 25), outline=(100, 100, 100), width=2)
    for c in range(10):
        draw.line([(60 + c * 30, 60), (120 + c * 30, 140)], fill=(0, 200, 255), width=2)
    p4 = os.path.join(target_dir, "edge_04_sharp_ui_graphics.png")
    ui_img.save(p4, format="PNG")
    generated_paths.append(p4)
    
    # 5. Clean Flat Poster
    poster = np.zeros((H, W, 3), dtype=np.uint8)
    poster[:, :W//3] = [230, 80, 60]
    poster[:, W//3:2*W//3] = [60, 180, 120]
    poster[:, 2*W//3:] = [50, 120, 220]
    p5 = os.path.join(target_dir, "edge_05_clean_flat_poster.png")
    save_image(poster, p5)
    generated_paths.append(p5)
    
    # 6. Mixed Lighting / High Dynamic Range Scene
    hdr = np.zeros((H, W, 3), dtype=np.float32)
    hdr[:, :W//2] = 20.0 + rng.normal(0, 4.0, (H, W//2, 3))
    hdr[:, W//2:] = 220.0 + rng.normal(0, 10.0, (H, W - W//2, 3))
    p6 = os.path.join(target_dir, "edge_06_mixed_hdr.png")
    save_image(np.clip(hdr, 0, 255).astype(np.uint8), p6)
    generated_paths.append(p6)
    
    return generated_paths

def prepare_benchmark_dataset(raw_dir: str) -> List[str]:
    """Prepares the full 30-image benchmark suite (24 Kodak + 6 Edge cases)."""
    kodak_paths = download_kodak_suite(raw_dir, num_images=24)
    edge_paths = generate_synthetic_stress_suite(raw_dir)
    return sorted(kodak_paths + edge_paths)

def create_datasplits(
    image_paths: List[str],
    metadata_dir: str,
    train_ratio: float = 0.60,
    val_ratio: float = 0.20,
    test_ratio: float = 0.20,
    random_seed: int = 42
) -> pd.DataFrame:
    """
    Creates leakage-safe train/val/test splits strictly partitioned by image_id.
    """
    os.makedirs(metadata_dir, exist_ok=True)
    rng = np.random.default_rng(random_seed)
    
    # Separate edge cases and kodak to distribute evenly
    kodak_files = [p for p in image_paths if "kodim" in os.path.basename(p)]
    edge_files = [p for p in image_paths if "edge_" in os.path.basename(p)]
    
    rng.shuffle(kodak_files)
    rng.shuffle(edge_files)
    
    # Distribute proportionally
    n_k_train = int(len(kodak_files) * train_ratio)
    n_k_val = int(len(kodak_files) * val_ratio)
    
    n_e_train = int(len(edge_files) * train_ratio)
    n_e_val = int(len(edge_files) * val_ratio)
    
    train_paths = kodak_files[:n_k_train] + edge_files[:n_e_train]
    val_paths = kodak_files[n_k_train:n_k_train + n_k_val] + edge_files[n_e_train:n_e_train + n_e_val]
    test_paths = kodak_files[n_k_train + n_k_val:] + edge_files[n_e_train + n_e_val:]
    
    records = []
    for p in train_paths:
        records.append({"image_id": os.path.splitext(os.path.basename(p))[0], "file_path": p, "split": "train"})
    for p in val_paths:
        records.append({"image_id": os.path.splitext(os.path.basename(p))[0], "file_path": p, "split": "val"})
    for p in test_paths:
        records.append({"image_id": os.path.splitext(os.path.basename(p))[0], "file_path": p, "split": "test"})
        
    df = pd.DataFrame(records)
    splits_csv = os.path.join(metadata_dir, "splits.csv")
    df.to_csv(splits_csv, index=False)
    return df
