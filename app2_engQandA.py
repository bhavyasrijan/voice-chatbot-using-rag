import streamlit as st
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text, translate_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *
import os
from rag_model import get_query_engine

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'my_service_account.json'
# os.environ['GOOGLE_API_KEY'] = 'AIzaSyC-ASsI6zwI9UiDcR9xqEH7SyeHl2MS8HY'

query_engine = get_query_engine()

# Initialize floating features for the interface so that the mic icon always floats and sticks to the bottom
float_init()

# Initialize session state for managing chat messages
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "¡Hola! ¿Cómo puedo ayudarte hoy?", "content_eng": "Hello! How can I help you today?"}]

initialize_session_state()

st.title("Conversational Voice Chatbot 🤖")

# Create a container for the microphone and audio recording
footer_container = st.container()
with footer_container:
    audio_bytes = audio_recorder()

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.write(message['content'])
        if "content_eng" in message:
            st.write(f"*{message['content_eng']}*")

if audio_bytes:
    with st.spinner("Transcribing..."):
        # Write the audio bytes to a temporary file
        webm_file_path = "temp_audio.mp3"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)

        # Convert the audio to text using the speech_to_text function
        transcript_span = speech_to_text(webm_file_path)
        transcript_eng = translate_text(transcript_span)
        print('\n\n')
        print("English Translation:", transcript_eng)
        print('\n\n')

        if transcript_eng:
            st.session_state.messages.append({"role": "user", "content": transcript_span, "content_eng": transcript_eng})
            with st.chat_message("user"):
                st.write(transcript_span)
                st.write(f"*{transcript_eng}*")
            os.remove(webm_file_path)

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking🤔..."):
            response = query_engine.query(transcript_eng)  # LLM response
            final_response = response.response if hasattr(response, 'response') else str(response)
            print("LLM Response in English: ", final_response)
            final_response_spanish = translate_text(final_response, target_language='es')
        with st.spinner("Generating audio response..."):
            audio_file = text_to_speech(str(final_response_spanish))  # converting LLM response back to Spanish voice
            autoplay_audio(audio_file)
        st.write(final_response_spanish)
        st.write(f"*{final_response}*")
        st.session_state.messages.append({"role": "assistant", "content": final_response_spanish, "content_eng": final_response})
        os.remove(audio_file)

# Float the footer container
footer_container.float("bottom: 0rem; color: white;")
