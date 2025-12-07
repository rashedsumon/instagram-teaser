import os
import tempfile
from pathlib import Path
from typing import List

import streamlit as st
from PIL import Image

# Safe MoviePy imports with graceful error handling
try:
    from moviepy.editor import (
        ImageClip,
        concatenate_videoclips,
        CompositeVideoClip,
        AudioFileClip,
        TextClip,
    )
    from moviepy.video.fx.all import resize, crop
except ModuleNotFoundError as e:
    st.error(
        "MoviePy or one of its dependencies is missing.\n"
        "Ensure your requirements.txt includes:\n"
        "- moviepy>=2.0.0\n- imageio\n- imageio-ffmpeg\n- decorator\n- Pillow\n- numpy\n- opencv-python-headless"
    )
    st.stop()

# Local module for Kaggle dataset download
try:
    from data_loader import download_dataset
except ModuleNotFoundError:
    st.warning(
        "data_loader module not found. Dataset download will be disabled."
    )
    download_dataset = None

# Constants
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)
DEFAULT_FPS = 24
TARGET_RESOLUTION = (1080, 1920)  # Portrait 9:16

# Streamlit page setup
st.set_page_config(
    page_title="AI Teaser Generator — Instagram Reel (9:16)",
    layout="centered"
)
st.title("🎬 AI Teaser Generator — Instagram Reel (9:16)")
st.markdown(
    """
Create a short, cinematic **5–10 second** teaser suitable for Instagram Reels (1080×1920, MP4 H.264).
Choose a generation mode, supply script / reference images, and click *Generate*.
"""
)
