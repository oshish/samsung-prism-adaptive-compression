import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, Any, List

# Set clean aesthetic styling
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"

def plot_class_distribution(labels_df: pd.DataFrame, output_path: str) -> None:
    """Plots class balance distribution overall and per split."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.figure(figsize=(8, 4.5))
    
    ax = sns.countplot(
        data=labels_df,
        x="split",
        hue="label",
        palette={"LOSSY": "#2ecc71", "LOSSLESS": "#e74c3c"}
    )
    plt.title("Compression Strategy Distribution across Dataset Splits", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Split", fontsize=11)
    plt.ylabel("Number of Frames", fontsize=11)
    plt.legend(title="Assigned Strategy")
    
    for p in ax.patches:
        height = p.get_height()
        if not np.isnan(height) and height > 0:
            ax.annotate(f"{int(height)}",
                        (p.get_x() + p.get_width() / 2., height / 2.),
                        ha="center", va="center", fontsize=10, color="white", fontweight="bold")
            
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

def plot_feature_distributions(features_df: pd.DataFrame, labels_df: pd.DataFrame, output_path: str) -> None:
    """Plots key feature distributions separated by compression label."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    merged = pd.merge(features_df, labels_df[["image_id", "label"]], on="image_id")
    
    key_features = [
        "mean_luminance", "dark_pixel_ratio", "laplacian_variance",
        "noise_estimate", "shannon_entropy_y", "colorfulness"
    ]
    
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes = axes.flatten()
    
    for i, feat in enumerate(key_features):
        if feat in merged.columns:
            sns.boxplot(
                data=merged,
                x="label",
                y=feat,
                ax=axes[i],
                palette={"LOSSY": "#2ecc71", "LOSSLESS": "#e74c3c"}
            )
            axes[i].set_title(feat.replace("_", " ").title(), fontsize=11, fontweight="bold")
            axes[i].set_xlabel("")
            axes[i].set_ylabel("Value")
            
    plt.suptitle("Pre-Compression Feature Distributions by Ground-Truth Strategy", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()

def plot_confusion_matrices(cm_dict: Dict[str, Dict[str, int]], output_path: str) -> None:
    """Plots heatmaps of confusion matrices for multiple baseline models."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    n_models = len(cm_dict)
    fig, axes = plt.subplots(1, n_models, figsize=(4 * n_models, 3.8))
    if n_models == 1:
        axes = [axes]
        
    for ax, (model_name, cm) in zip(axes, cm_dict.items()):
        matrix = np.array([
            [cm["tn"], cm["fp"]],
            [cm["fn"], cm["tp"]]
        ])
        sns.heatmap(
            matrix,
            annot=True,
            fmt="d",
            cmap="Blues",
            cbar=False,
            ax=ax,
            xticklabels=["LOSSLESS", "LOSSY"],
            yticklabels=["LOSSLESS", "LOSSY"]
        )
        ax.set_title(model_name.replace("_", " ").title(), fontsize=11, fontweight="bold")
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
        
    plt.suptitle("Confusion Matrices across Evaluated Baselines", fontsize=13, fontweight="bold", y=1.05)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()

def plot_storage_quality_tradeoff(system_eval: Dict[str, Any], output_path: str) -> None:
    """Visualizes the fundamental storage vs quality Pareto frontier."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    strategies = system_eval["strategies"]
    
    names = []
    savings = []
    ssims = []
    failures = []
    
    for name, data in strategies.items():
        names.append(name.replace("_", " ").title())
        savings.append(data["saving_vs_lossless_pct"])
        ssims.append(data["mean_ssim"])
        failures.append(data["critical_failures"])
        
    fig, ax1 = plt.subplots(figsize=(10, 5))
    
    color = "tab:blue"
    ax1.set_xlabel("Compression Strategy", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Storage Savings vs Always Lossless (%)", color=color, fontsize=11, fontweight="bold")
    bars = ax1.bar(names, savings, color=color, alpha=0.7, width=0.45)
    ax1.tick_params(axis="y", labelcolor=color)
    
    for bar in bars:
        h = bar.get_height()
        ax1.annotate(f"{h:.1f}%",
                    (bar.get_x() + bar.get_width() / 2., max(0, h)),
                    ha="center", va="bottom", fontsize=10, color=color, fontweight="bold")
                    
    # Overlay Mean SSIM
    ax2 = ax1.twinx()
    color2 = "tab:red"
    ax2.set_ylabel("Mean Structural Similarity (SSIM)", color=color2, fontsize=11, fontweight="bold")
    ax2.plot(names, ssims, color=color2, marker="o", linewidth=2.5, markersize=8)
    ax2.tick_params(axis="y", labelcolor=color2)
    ax2.set_ylim(0.85, 1.01)
    
    plt.title("System-Level Memory Optimization vs Visual Quality Preservation", fontsize=13, fontweight="bold", pad=14)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

def plot_feature_importances(importance_dict: Dict[str, float], output_path: str) -> None:
    """Plots feature importance rankings from Random Forest / Tree."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    if not importance_dict:
        return
        
    s = pd.Series(importance_dict).sort_values(ascending=True)
    top_s = s.tail(10)
    
    plt.figure(figsize=(8, 4.5))
    top_s.plot(kind="barh", color="#3498db")
    plt.title("Top Feature Importances (Random Forest)", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Gini Importance", fontsize=11)
    plt.ylabel("Pre-Compression Feature", fontsize=11)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
