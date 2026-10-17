import streamlit as st
import os
import subprocess
from mutagen.mp3 import MP3
from PIL import Image

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(page_title="AI Video Editor Otomatis", page_icon="🎬", layout="centered")

st.title("🎬 AI Video Editor Otomatis")
st.write("Ubah kumpulan gambar dan voiceover menjadi video durasi panjang secara instan!")

vo_file = st.file_uploader("1. Unggah Voiceover (MP3)", type=["mp3"])
img_files = st.file_uploader("2. Unggah Gambar Mentah (Bisa pilih banyak sekaligus)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if st.button("Mulai Edit Otomatis", type="primary"):
    if not vo_file or not img_files:
        st.error("Harap unggah voiceover dan minimal 1 gambar terlebih dahulu!")
    else:
        with st.spinner("Sedang memproses video... Proses ini berjalan di latar belakang server."):
            try:
                vo_path = os.path.join(UPLOAD_DIR, "voiceover.mp3")
                with open(vo_path, "wb") as f:
                    f.write(vo_file.getbuffer())
                
                audio = MP3(vo_path)
                total_duration = audio.info.length
                
                image_paths = []
                for i, img_file in enumerate(img_files):
                    img = Image.open(img_file)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    img_path = os.path.join(UPLOAD_DIR, f"img_{i}.jpg")
                    img.save(img_path, "JPEG")
                    image_paths.append(img_path)
                
                duration_per_image = total_duration / len(image_paths)
                
                input_list_path = os.path.join(UPLOAD_DIR, "input_list.txt")
                with open(input_list_path, "w") as f:
                    for path in image_paths:
                        f.write(f"file '{os.path.abspath(path)}'\n")
                        f.write(f"duration {duration_per_image}\n")
                    f.write(f"file '{os.path.abspath(image_paths[-1])}'\n")
                
                output_video_path = "hasil_edit_otomatis.mp4"
                if os.path.exists(output_video_path):
                    os.remove(output_video_path)
                
                ffmpeg_cmd = [
                    "ffmpeg", "-f", "concat", "-safe", "0", "-i", input_list_path,
                    "-i", vo_path,
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
                    "-c:a", "aac", "-shortest",
                    output_video_path
                ]
                
                subprocess.run(ffmpeg_cmd, check=True)
                
                st.success("🎉 Selesai! Video Anda berhasil dirakit otomatis.")
                
                with open(output_video_path, "rb") as file:
                    st.download_button(
                        label="📥 Unduh Video Hasil (.mp4)",
                        data=file,
                        file_name="hasil_video_ai.mp4",
                        mime="video/mp4"
                    )
                    
            except Exception as e:
                st.error(f"Terjadi kesalahan saat merender: {str(e)}")
