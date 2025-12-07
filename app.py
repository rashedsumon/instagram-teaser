# app.py
"""
Streamlit app: AI-generated 5-10s Instagram Reel teaser (1080x1920).
Supports:
 - Remote AI provider (placeholder - insert your API code & set API key in Streamlit secrets)
 - Local cinematic fallback (Ken Burns style + text + transitions + optional audio)
Main entrypoint for Streamlit Cloud deployment.
"""

import os
import tempfile
from pathlib import Path
from typing import List, Optional

import streamlit as st
from PIL import Image
from data_loader import download_dataset  # local module (uses kagglehub)
from moviepy.editor import (
    ImageClip,
    concatenate_videoclips,
    CompositeVideoClip,
    AudioFileClip,
    TextClip,
)

# Constants
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)
DEFAULT_FPS = 24
TARGET_RESOLUTION = (1080, 1920)  # width, height (portrait 9:16)


st.set_page_config(page_title="AI Teaser Generator — Instagram Reel (9:16)", layout="centered")

st.title("🎬 AI Teaser Generator — Instagram Reel (9:16)")
st.markdown(
    """
Create a short, cinematic **5–10 second** teaser suitable for Instagram Reels (1080×1920, MP4 H.264).
Choose a generation mode, supply script / reference images, and click *Generate*.
"""
)

# Sidebar: options & dataset download
with st.sidebar:
    st.header("Project / Data")
    if st.button("Download example dataset (kagglehub)"):
        try:
            with st.spinner("Downloading dataset via kagglehub ..."):
                path = download_dataset("yogendras843/online-casino-dataset")
            st.success("Downloaded dataset.")
            st.write("Path to dataset files:", path)
        except Exception as e:
            st.error(f"Dataset download failed: {e}")

    st.markdown("---")
    st.header("Generation settings")
    duration = st.slider("Duration (seconds)", min_value=5, max_value=10, value=7, step=1)
    fps = st.selectbox("Frame rate", options=[24, 25, 30], index=0)
    mode = st.selectbox("Generation Mode", options=["Local cinematic (fallback)", "Remote AI provider (requires API)"])
    add_music = st.checkbox("Add background music (optional)", value=True)
    # optional music upload
    uploaded_music = st.file_uploader("Upload music (MP3, <= 30s) — optional", type=["mp3", "wav"])

# Main inputs
st.header("Source inputs from client")
script = st.text_area("Short script / concept (one or two sentences)", value="A cinematic reveal of the brand with dramatic motion.")
st.write("Reference image(s) — upload 1 to 4 images (recommended) or use dataset images.")
uploaded_files = st.file_uploader("Upload reference images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

# Style inputs
st.subheader("Style & Branding")
brand_color = st.color_picker("Brand main color", value="#FF6B6B")
text_overlay = st.text_input("Text to overlay (optional)", value="Brand Teaser")
font_size = st.slider("Overlay text size", min_value=36, max_value=160, value=96, step=4)

# Remote provider settings (placeholder)
st.markdown("#### Remote AI provider (optional)")
remote_provider = st.selectbox("Choose provider", options=["(not configured)", "StabilityAI (example)", "Runway (example)", "Custom API"])
api_key = st.text_input("API Key (if using remote provider) — store securely in Streamlit Secrets for production", type="password")

# Generate button
if st.button("Generate teaser"):
    st.spinner("Generating teaser...")

    # Prepare list of PIL images
    pil_images: List[Image.Image] = []
    if uploaded_files:
        for f in uploaded_files:
            pil_images.append(Image.open(f).convert("RGB"))
    else:
        st.info("No reference images uploaded — using placeholders from assets (or dataset if downloaded).")
        placeholder_path = Path("assets/placeholder.png")
        if placeholder_path.exists():
            pil_images.append(Image.open(placeholder_path).convert("RGB"))
        else:
            # fallback: create a solid color image
            img = Image.new("RGB", (1080, 1920), color=brand_color)
            pil_images.append(img)

    out_path = OUTPUT_DIR / f"teaser_{int(st.session_state.get('run_count', 0)) + 1}.mp4"

    try:
        if mode.startswith("Remote"):
            # Placeholder remote flow - user must replace with actual provider code.
            st.info("Remote AI provider flow started. Insert provider API integration in the code.")
            # Example placeholder function call (not implemented)
            def generate_via_remote_provider(script: str, images: List[Image.Image], duration: int, fps: int, **kwargs) -> str:
                """
                Replace contents of this function with calls to your chosen API.
                Return the path to the produced MP4 video.
                """
                raise NotImplementedError("Insert remote provider integration here (Stability/Runway/Pika/etc).")

            out_file = generate_via_remote_provider(script=script, images=pil_images, duration=duration, fps=fps, api_key=api_key)
            st.success("Remote generation complete.")
            st.video(out_file)
        else:
            # Local cinematic generation
            st.info("Using local cinematic generation (Ken Burns + transitions + text overlay).")
            from moviepy.video.fx.all import resize, crop

            clips = []
            n_images = len(pil_images)
            # split duration across images with small overlap for crossfade
            base_clip_dur = duration / max(1, n_images)
            crossfade = 0.5  # seconds
            single_dur = max(1.5, base_clip_dur + crossfade / n_images)

            for idx, pil in enumerate(pil_images):
                # Resize preserving aspect to cover portrait target (1080x1920)
                img_w, img_h = pil.size
                target_w, target_h = TARGET_RESOLUTION
                # Compute scale to make sure we can pan/crop
                scale = max(target_w / img_w, target_h / img_h) * 1.1  # slight overscale for motion
                new_w, new_h = int(img_w * scale), int(img_h * scale)
                pil_resized = pil.resize((new_w, new_h), Image.LANCZOS)
                temp_img_path = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
                pil_resized.save(temp_img_path)

                # Create an ImageClip and add a slight zoom/pan
                clip = ImageClip(temp_img_path).set_duration(single_dur)
                clip = clip.resize(width=target_w)  # ensure width fits then crop height
                # crop to target resolution centered
                clip = clip.crop(x_center=clip.w // 2, y_center=clip.h // 2, width=target_w, height=target_h)

                # Add subtle zoom effect (scale 1 -> 1.06)
                def zoom(t, clip=clip):
                    zoom_factor = 1 + 0.06 * (t / single_dur)
                    return clip.resize(zoom_factor)

                # MoviePy doesn't support dynamic fx easily in inline; instead use resize with lambda
                clip = clip.fl_image(lambda img: img)  # no-op placeholder but keeps clip structure
                # We'll emulate zoom by setting start and end sizes (using resize)
                clip = clip.resize(lambda t: 1 + 0.06 * (t / single_dur))

                clips.append(clip)

            # Crossfade and concatenate
            final = concatenate_videoclips(clips, method="compose", padding=-crossfade)

            # Add text overlay (centered, with drop shadow)
            if text_overlay:
                txt_clip = TextClip(
                    text_overlay,
                    fontsize=font_size,
                    font="Amiri-Bold" if "Amiri-Bold" in TextClip.fonts() else "Arial-Bold",
                    color="white",
                    method="caption",
                    size=(int(TARGET_RESOLUTION[0] * 0.9), None),
                ).set_duration(final.duration)

                # Add a simple semi-transparent black box behind text for readability
                txt_bg = TextClip(" " * 10, fontsize=10, color=brand_color, size=(int(TARGET_RESOLUTION[0] * 0.94), font_size + 20))
                txt_bg = txt_bg.set_opacity(0.25).set_duration(final.duration)

                # Position at lower third
                txt = txt_clip.set_position(("center", TARGET_RESOLUTION[1] * 0.75))
                # Note: CompositeVideoClip expects same size frames - ensure final is sized to target
                final = final.set_fps(fps).set_duration(duration)
                comp = CompositeVideoClip([final, txt_bg.set_position(("center", TARGET_RESOLUTION[1] * 0.72)), txt])
            else:
                comp = final.set_fps(fps).set_duration(duration)

            # Add audio if requested
            if add_music:
                if uploaded_music:
                    music_temp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
                    with open(music_temp, "wb") as f:
                        f.write(uploaded_music.getbuffer())
                    audio = AudioFileClip(music_temp).subclip(0, min(duration, AudioFileClip(music_temp).duration))
                    comp = comp.set_audio(audio)
                else:
                    # try load bundled sample music if exists
                    sample_music = Path("assets/sample_music.mp3")
                    if sample_music.exists():
                        audio = AudioFileClip(str(sample_music)).subclip(0, min(duration, AudioFileClip(str(sample_music)).duration))
                        comp = comp.set_audio(audio)

            # Write the file — ensure portrait resolution and H.264 codec (libx264). use preset & bitrate for quality.
            out_path = OUTPUT_DIR / f"teaser_local_{os.getpid()}.mp4"
            temp_out = str(out_path)
            st.info("Rendering video (this may take a few seconds)...")
            # moviepy write_videofile uses ffmpeg; Streamlit Cloud should have ffmpeg installed; if not, instruct in README.
            comp.write_videofile(
                temp_out,
                fps=fps,
                codec="libx264",
                audio_codec="aac",
                threads=4,
                preset="medium",
                ffmpeg_params=["-profile:v", "high", "-level", "4.0", "-crf", "18"],
                verbose=False,
                logger=None,
            )
            st.success("Video generated.")
            st.video(str(temp_out))
            st.markdown(f"**Download:** [Download video]({temp_out})")

        # increment run counter
        st.session_state["run_count"] = st.session_state.get("run_count", 0) + 1
    except NotImplementedError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Generation failed: {e}")
