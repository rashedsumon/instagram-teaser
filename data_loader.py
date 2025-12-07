# data_loader.py
"""
data_loader.py
Provides a simple wrapper around kagglehub.dataset_download to fetch datasets.
It returns the path to the downloaded files (as provided by kagglehub).
This module is intentionally small so Streamlit can call it when requested.
"""

import os
from pathlib import Path
from typing import Optional

import kagglehub

DOWNLOAD_DIR = Path("data")
DOWNLOAD_DIR.mkdir(exist_ok=True)


def download_dataset(dataset_ref: str, dest: Optional[str] = None) -> str:
    """
    Download a dataset via kagglehub.
    - dataset_ref: "username/dataset-name" (e.g. "yogendras843/online-casino-dataset")
    - dest: optional destination directory
    Returns path to downloaded files.
    """
    dest_dir = Path(dest) if dest else DOWNLOAD_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)

    # kagglehub.dataset_download should mirror your environment / API usage.
    # Some kagglehub wrappers return a path or unzip content — handle both cases.
    print(f"Downloading dataset {dataset_ref} to {dest_dir} ...")
    result = kagglehub.dataset_download(dataset_ref, path=str(dest_dir), unzip=True)
    # result could be path string or object - normalize
    if isinstance(result, str):
        return result
    elif hasattr(result, "__str__"):
        return str(result)
    else:
        # fallback: return dest dir
        return str(dest_dir)
