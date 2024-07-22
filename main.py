import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from moviepy.editor import *
import os

load_dotenv()
client = OpenAI()

st.title("Sentiment Analysis")

uploaded_file = st.sidebar.file_uploader("Choose a video file...", type=["mp4", "mpeg"])

if uploaded_file is not None:
    try:
        video_path = Path(uploaded_file.name)
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        video = VideoFileClip(str(video_path))
        audio = video.audio
        audio_path = "temp_audio.ogg"
        audio.write_audiofile(audio_path, codec='libvorbis')
        st.subheader("Soundtrack")
        st.audio(audio_path, format='audio/ogg')

        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            st.subheader("Transcript")
            text = transcript.text
            st.write(text)
        os.remove(audio_path)

        response = client.moderations.create(input=text)
        output = response.results[0]

        analysis_result = output.categories
        category_scores = output.category_scores
        
        st.subheader("Analysis Result")
        st.write(analysis_result)
        st.subheader("Category Score")
        st.write(category_scores)
        
        analysis_text = f"Transcript: {text}\n\nAnalysis results: {analysis_result}. Category scores: {category_scores}."
        st.write(analysis_text)
    except Exception as e:
        st.warning(f"Error processing the video: {e}")
