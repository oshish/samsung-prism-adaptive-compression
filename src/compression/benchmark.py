import time
import numpy as np
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from .codecs import compress_image, decompress_image, SUPPORTED_LOSSLESS, SUPPORTED_LOSSY

@dataclass
class CompressionResult:
    codec: str
    is_lossy: bool
    quality: Optional[int]
    raw_bytes: int
    compressed_bytes: int
    compression_ratio: float  # raw_bytes / compressed_bytes
    encode_time_ms: float
    decode_time_ms: float
    decompressed_img: np.ndarray

def benchmark_compression(
    rgb_img: np.ndarray,
    codec: str,
    quality: Optional[int] = None
) -> CompressionResult:
    """
    Benchmarks compression and decompression runtime and size for a given codec and quality.
    """
    raw_bytes = int(rgb_img.nbytes)
    is_lossy = codec.lower() in SUPPORTED_LOSSY
    q = quality if is_lossy else (100 if "webp" in codec.lower() else None)
    
    # 1. Measure encode time
    t0 = time.perf_counter()
    compressed_bytes = compress_image(rgb_img, codec=codec, quality=q if q is not None else 75)
    t1 = time.perf_counter()
    encode_time_ms = float((t1 - t0) * 1000.0)
    
    # 2. Measure decode time
    t2 = time.perf_counter()
    decompressed = decompress_image(compressed_bytes)
    t3 = time.perf_counter()
    decode_time_ms = float((t3 - t2) * 1000.0)
    
    compressed_size = len(compressed_bytes)
    compression_ratio = float(raw_bytes / max(1, compressed_size))
    
    return CompressionResult(
        codec=codec,
        is_lossy=is_lossy,
        quality=q,
        raw_bytes=raw_bytes,
        compressed_bytes=compressed_size,
        compression_ratio=compression_ratio,
        encode_time_ms=encode_time_ms,
        decode_time_ms=decode_time_ms,
        decompressed_img=decompressed
    )

def run_codec_suite(
    rgb_img: np.ndarray,
    lossless_codecs: List[str] = ["png", "webp_lossless"],
    lossy_codecs: List[str] = ["jpeg", "webp_lossy"],
    lossy_qualities: List[int] = [50, 75, 85, 95]
) -> List[CompressionResult]:
    """
    Runs an exhaustive benchmark suite over specified codecs and quality levels.
    """
    results: List[CompressionResult] = []
    
    # Run lossless
    for codec in lossless_codecs:
        results.append(benchmark_compression(rgb_img, codec=codec))
        
    # Run lossy
    for codec in lossy_codecs:
        for q in lossy_qualities:
            results.append(benchmark_compression(rgb_img, codec=codec, quality=q))
            
    return results
