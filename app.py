import os
import cv2
import numpy as np
import tempfile
from pathlib import Path
from typing import List

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# Constants
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)
TARGET_RESOLUTION = (1080, 1920)  # Portrait 9:16
FPS = 24

st.set_page_config(page_title="AI Teaser Generator — Instagram Reel", layout="centered")
st.title("🎬 AI Teaser Generator — Instagram Reel (9:16)")

# Inputs
st.header("Upload reference images (1–4)")
uploaded_files = st.file_uploader(
    "Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True
)

st.subheader("Style & Text")
brand_color = st.color_picker("Brand color", "#FF6B6B")
text_overlay = st.text_input("Overlay text (optional)", "Brand Teaser")
font_size = st.slider("Text size", 36, 160, 96)

st.subheader("Audio (optional)")
add_audio = st.checkbox("Add background music")
uploaded_music = st.file_uploader("Upload MP3/WAV", type=["mp3", "wav"])

duration = st.slider("Video duration (seconds)", 5, 10, 7)

# Generate button
if st.button("Generate teaser"):
    st.info("Generating teaser...")

    # Prepare images
    pil_images: List[Image.Image] = []
    if uploaded_files:
        for f in uploaded_files:
            pil_images.append(Image.open(f).convert("RGB"))
    else:
        # fallback solid color
        img = Image.new("RGB", TARGET_RESOLUTION, color=brand_color)
        pil_images.append(img)

    # Resize and add text overlay
    processed_images = []
    for img in pil_images:
        img = img.resize(TARGET_RESOLUTION, Image.LANCZOS)
        if text_overlay:
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            text_w, text_h = draw.textsize(text_overlay, font=font)
            draw.text(
                ((TARGET_RESOLUTION[0]-text_w)//2, int(TARGET_RESOLUTION[1]*0.75)),
                text_overlay,
                font=font,
                fill=(255, 255, 255)
            )
        processed_images.append(np.array(img))

    # Prepare video writer
    out_path = OUTPUT_DIR / f"teaser_{os.getpid()}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # mp4
    out = cv2.VideoWriter(str(out_path), fourcc, FPS, TARGET_RESOLUTION)

    n_images = len(processed_images)
    frames_per_image = int(FPS * duration / n_images)

    for i, img in enumerate(processed_images):
        for _ in range(frames_per_image):
            out.write(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    out.release()

    # Add audio using ffmpeg if uploaded
    if add_audio and uploaded_music:
        temp_video = str(out_path)
        temp_audio = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
        with open(temp_audio, "wb") as f:
            f.write(uploaded_music.getbuffer())
        final_path = OUTPUT_DIR / f"teaser_audio_{os.getpid()}.mp4"
        os.system(f'ffmpeg -y -i "{temp_video}" -i "{temp_audio}" -c:v copy -c:a aac -shortest "{final_path}"')
        out_path = final_path

    st.success("Video generated!")
    st.video(str(out_path))
    st.markdown(f"**Download:** [Download video]({out_path})")
