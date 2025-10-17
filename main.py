import streamlit as st
import numpy as np
import cv2
from moviepy.editor import ImageSequenceClip, AudioFileClip
from PIL import Image
import os

# streamlit run "/Users/matteolemesre/Desktop/Projet/main.py"

st.title("🎨 Animation de dessin synchronisée à l'audio")

uploaded_image = st.file_uploader("📷 Importez votre dessin (PNG ou JPG)", type=["png", "jpg", "jpeg"])
uploaded_audio = st.file_uploader("🎙️ Importez votre audio (MP3 ou WAV)", type=["mp3", "wav"])

if uploaded_image and uploaded_audio:
    image = Image.open(uploaded_image).convert("RGBA")
    image_np = np.array(image)

    if not os.path.exists("temp"):
        os.makedirs("temp")

    audio_path = f"temp/{uploaded_audio.name}"
    with open(audio_path, "wb") as f:
        f.write(uploaded_audio.read())

    num_frames = 200  
    height, width, _ = image_np.shape
    mask = np.zeros((height, width), dtype=np.uint8)
    frames = []

    gray = cv2.cvtColor(image_np, cv2.COLOR_RGBA2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_points = np.column_stack(np.where(edges > 0))
    np.random.shuffle(edge_points)

    points_per_frame = len(edge_points) // num_frames
    for i in range(num_frames):
        start = i * points_per_frame
        end = start + points_per_frame
        mask[:] = 0
        mask[tuple(edge_points[:end].T)] = 255
        revealed = cv2.bitwise_and(image_np, image_np, mask=mask)
        frames.append(revealed)

    fps = 30
    clip = ImageSequenceClip([cv2.cvtColor(f, cv2.COLOR_RGBA2RGB) for f in frames], fps=fps)

    audio_clip = AudioFileClip(audio_path)
    final_clip = clip.set_audio(audio_clip).set_duration(audio_clip.duration)

    output_path = "temp/final_video.mp4"
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

    st.success("✅ Vidéo générée avec succès !")
    st.video(output_path)

    with open(output_path, "rb") as f:
        st.download_button(
            label="⬇️ Télécharger la vidéo",
            data=f,
            file_name="animation_dessin.mp4",
            mime="video/mp4"
        )
