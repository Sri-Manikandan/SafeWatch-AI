import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from moviepy.editor import VideoFileClip
import os
from langchain_openai import ChatOpenAI
from pytube import YouTube

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def process_video(url):
    try:
        yv = YouTube(url)
        st.write(yv.streams)
        d_video = yv.streams.filter(only_audio=True).first()
        d_video.download(filename="temp.mp3")
        audio_file = open("temp.mp3", 'rb')
        transcription = client.audio.translations.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
        text = transcription.text
        response = client.moderations.create(input=text)
        output = response.results[0]

        analysis_result = output.categories
        category_scores = output.category_scores

        analysis_text = f"Analysis results: {analysis_result}. Category scores: {category_scores}."

        llm = ChatOpenAI(model="gpt-4")
        prompt = f"""
        Here is the transcript of the video:
        {text}
        
        and the response of the OpenAI moderation API is:
        {analysis_text}

        Help me find if the given transcript from the video is kids-friendly or not based on given the transcript and the response of the OpenAI moderation API.
        Provide the output with only the conclusion whether it is kids-friendly or not and justification to support it in a few sentences.
        """

        messages = [
            (
                "system",
                "You are a helpful assistant that helps find if the given transcript from the video is kids-friendly or not, using the transcript and the response of the OpenAI moderation API.",
            ),
            ("human", prompt),
        ]
        ai_msg = llm.invoke(messages)
        st.write(ai_msg.content)

    except Exception as e:
        st.error(f"Error processing the video: {e}")

def main():
    st.title("SafeWatch AI")
    st.write("The SafeWatch AI helps to analyze the content of a video and determine if it contains any harmful or inappropriate content.")
    st.write("Please provide the video link or upload a video file to analyze.")
    url = st.text_input("Enter the YouTube Url", "")
    st.subheader("or")
    uploaded_file = st.file_uploader("Upload your video!", type=["mp4", "mpeg"])

    if st.button("Analyze"):
        if uploaded_file is not None:
            try:
                # Save the uploaded file to disk
                video_path = Path(uploaded_file.name)
                with open(video_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                video = VideoFileClip(str(video_path))

                # Extract audio from the video
                audio = video.audio
                audio_path = "temp_audio.ogg"
                audio.write_audiofile(audio_path, codec='libvorbis')

                # Transcribe the audio
                with open(audio_path, "rb") as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                    text = transcript.text

                # Remove the temporary audio file
                os.remove(audio_path)

                response = client.moderations.create(input=text)
                output = response.results[0]

                analysis_result = output.categories
                category_scores = output.category_scores

                analysis_text = f"Analysis results: {analysis_result}. Category scores: {category_scores}."

                llm = ChatOpenAI(model="gpt-4")
                prompt = f"""
                Here is the transcript of the video:
                {text}
                
                and the response of the OpenAI moderation API is:
                {analysis_text}

                Help me find if the given transcript from the video is kids-friendly or not based on the transcript and the response of the OpenAI moderation API.
                Provide the output with only the conclusion whether it is kids-friendly or not and justification to support it in a few sentences.
                """

                messages = [
                    (
                        "system",
                        "You are a helpful assistant that helps find if the given transcript from the video is kids-friendly or not, using the transcript and the response of the OpenAI moderation API.",
                    ),
                    ("human", prompt),
                ]
                ai_msg = llm.invoke(messages)
                st.write(ai_msg.content)

            except Exception as e:
                st.warning(f"Error processing the video: {e}")
        else:
            process_video(url)

if __name__ == '__main__':
    main()
