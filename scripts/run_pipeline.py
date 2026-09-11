import os
import sys
import yaml
import argparse
import subprocess

# Add repo root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.utils.logger import setup_logger

logger = setup_logger("run_pipeline")

def run_step(script_name: str, config_path: str):
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    logger.info(f">>> Executing pipeline step: {script_name} <<<")
    # Use the active python interpreter
    cmd = [sys.executable, script_path, "--config", config_path]
    result = subprocess.run(cmd, check=True)
    if result.returncode != 0:
        logger.error(f"Step {script_name} failed with code {result.returncode}")
        sys.exit(result.returncode)

def main():
    parser = argparse.ArgumentParser(description="Run End-to-End Milestone 1 Pipeline")
    parser.add_argument("--config", default="configs/config.yaml", help="Path to config.yaml")
    args = parser.parse_args()
    
    logger.info("Starting Samsung PRISM Milestone 1 Automated Pipeline...")
    
    steps = [
        "01_prepare_dataset.py",
        "02_run_compression_benchmark.py",
        "03_extract_features.py",
        "04_generate_labels.py",
        "05_train_baselines.py",
        "06_evaluate_system.py"
    ]
    
    for step in steps:
        run_step(step, args.config)
        
    logger.info("Samsung PRISM Milestone 1 Pipeline Finished Successfully!")

if __name__ == "__main__":
    main()
