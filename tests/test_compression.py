import pytest
import numpy as np

from src.compression.codecs import compress_image, decompress_image
from src.compression.benchmark import benchmark_compression

def test_lossless_png_reconstruction():
    img = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
    png_bytes = compress_image(img, codec="png")
    assert len(png_bytes) > 0
    
    recon = decompress_image(png_bytes)
    assert np.array_equal(img, recon) # Exact bit-for-bit reconstruction

def test_lossless_webp_reconstruction():
    img = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
    webp_bytes = compress_image(img, codec="webp_lossless")
    assert len(webp_bytes) > 0
    
    recon = decompress_image(webp_bytes)
    assert np.array_equal(img, recon)

def test_lossy_jpeg_size_reduction():
    # Natural-like gradient
    H, W = 128, 128
    grad = np.linspace(0, 255, W, dtype=np.uint8)
    img = np.tile(grad, (H, 1, 3)).reshape(H, W, 3)
    
    bench_lossless = benchmark_compression(img, codec="png")
    bench_lossy = benchmark_compression(img, codec="jpeg", quality=75)
    
    assert bench_lossy.compressed_bytes < bench_lossless.raw_bytes
    assert bench_lossy.compression_ratio > 1.0
    assert bench_lossy.decompressed_img.shape == (H, W, 3)
