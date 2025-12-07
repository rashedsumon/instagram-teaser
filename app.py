import os
import tempfile
from pathlib import Path
from typing import List

import streamlit as st
from PIL import Image

# Safe MoviePy imports
try:
    from moviepy.editor import (
        ImageClip,
        concatenate_videoclips,
        CompositeVideoClip,
        AudioFileClip,
        TextClip,
    )
    from moviepy.video.fx.all import resize, crop
except ModuleNotFoundError:
    st.error(
        "MoviePy or one of its dependencies is missing.\n"
        "Ensure your requirements.txt includes:\n"
        "- moviepy>=2.0.0\n- imageio\n- imageio-ffmpeg\n- decorator\n- Pillow\n- numpy\n- opencv-python-headless"
    )
    st.stop()

# Constants
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)
TARGET_RESOLUTION = (1080, 1920)  # Portrait 9:16
DEFAULT_FPS = 24

# Streamlit page setup
st.set_page_config(
    page_title="AI Teaser Generator — Instagram Reel (9:16)",
    layout="centered"
)
st.title("🎬 AI Teaser Generator — Instagram Reel (9:16)")
st.markdown(
    "Create a **5–10 second** cinematic teaser for Instagram Reels (1080×1920, MP4)."
)

# Sidebar options
with st.sidebar:
    st.header("Generation Settings")
    duration = st.slider("Duration (seconds)", min_value=5, max_value=10, value=7)
    fps = st.selectbox("Frame rate", [24, 25, 30], index=0)
    add_music = st.checkbox("Add background music (optional)", value=True)
    uploaded_music = st.file_uploader("Upload music (MP3/WAV)", type=["mp3", "wav"])

# Main inputs
st.header("Source inputs")
script = st.text_area("Short script / concept", value="Cinematic brand reveal.")
uploaded_files = st.file_uploader(
    "Reference image(s) — upload 1 to 4 images", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

st.subheader("Style & Branding")
brand_color = st.color_picker("Brand color", value="#FF6B6B")
text_overlay = st.text_input("Text overlay (optional)", value="Brand Teaser")
font_size = st.slider("Text size", 36, 160, 96)

# Generate button
if st.button("Generate teaser"):
    st.info("Generating teaser...")

    # Prepare images
    pil_images: List[Image.Image] = []
    if uploaded_files:
        for f in uploaded_files:
            pil_images.append(Image.open(f).convert("RGB"))
    else:
        # Fallback: solid color image
        img = Image.new("RGB", TARGET_RESOLUTION, color=brand_color)
        pil_images.append(img)

    # Local cinematic generation
    clips = []
    n_images = len(pil_images)
    single_dur = max(1.5, duration / max(1, n_images))

    for pil in pil_images:
        # Resize to target while preserving aspect ratio
        img_w, img_h = pil.size
        scale = max(TARGET_RESOLUTION[0] / img_w, TARGET_RESOLUTION[1] / img_h) * 1.05
        new_w, new_h = int(img_w * scale), int(img_h * scale)
        pil_resized = pil.resize((new_w, new_h), Image.LANCZOS)
        temp_img_path = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        pil_resized.save(temp_img_path)

        clip = ImageClip(temp_img_path).set_duration(single_dur)
        # Crop to target resolution
        clip = clip.crop(
            x_center=clip.w // 2, y_center=clip.h // 2,
            width=TARGET_RESOLUTION[0], height=TARGET_RESOLUTION[1]
        )
        clips.append(clip)

    final_clip = concatenate_videoclips(clips, method="compose")

    # Add text overlay
    if text_overlay:
        txt_clip = TextClip(
            text_overlay, fontsize=font_size, color="white", font="Arial-Bold"
        ).set_duration(final_clip.duration).set_position(("center", "bottom"))
        final_clip = CompositeVideoClip([final_clip, txt_clip])

    # Add audio
    if add_music and uploaded_music:
        music_temp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
        with open(music_temp, "wb") as f:
            f.write(uploaded_music.getbuffer())
        audio = AudioFileClip(music_temp).subclip(0, min(duration, AudioFileClip(music_temp).duration))
        final_clip = final_clip.set_audio(audio)

    # Export video
    out_path = OUTPUT_DIR / f"teaser_{os.getpid()}.mp4"
    final_clip.write_videofile(
        str(out_path),
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
        ffmpeg_params=["-profile:v", "high", "-level", "4.0", "-crf", "18"],
        verbose=False,
        logger=None
    )

    st.success("Video generated!")
    st.video(str(out_path))
    st.markdown(f"**Download:** [Download video]({out_path})")
