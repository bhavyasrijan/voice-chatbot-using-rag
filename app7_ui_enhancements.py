import streamlit as st
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text, translate_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *
import os
from rag_model import get_query_engine

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'my_service_account.json'
query_engine = get_query_engine()

# Initialize floating features for the interface
float_init()

# Initialize session state
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "¡Hola! ¿Cómo puedo ayudarte hoy?", "content_eng": "Hello! How can I help you today?"}]
    if "stop_audio" not in st.session_state:
        st.session_state.stop_audio = False
    if "user_query_eng" not in st.session_state:
        st.session_state.user_query_eng = ""
    if "user_query_span" not in st.session_state:
        st.session_state.user_query_span = ""
    if "widget" not in st.session_state:
        st.session_state.widget = ""

def submit():
    st.session_state.user_query_eng = st.session_state.widget
    st.session_state.widget = ''  # Clear the input after submission

initialize_session_state()

st.title("Conversational Voice Chatbot 🤖")

# Chat history display
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.write(message['content'])
        if "content_eng" in message:
            st.write(f"*{message['content_eng']}*")


# Floating footer container
footer_container = st.container()
with footer_container:
    col1, col2, col3 = st.columns([4, 1, 1])  # Adjusted column widths
    with col1:
        st.text_input("Type your query here...", key="widget", on_change=submit)
    with col2:
        audio_bytes = audio_recorder(text='',recording_color="#e8b62c",
    neutral_color="#6aa36f",
    
    icon_size="3x")
    with col3:
        stop_button = st.button("Stop Audio")

# Handle audio stop
if stop_button:
    st.session_state.stop_audio = True

# Process input (either text or audio)
if (audio_bytes or st.session_state.user_query_eng) and not st.session_state.stop_audio:
    if audio_bytes:
        print('entering the audio bytes...')
        with st.spinner("Transcribing..."):
            webm_file_path = "temp_audio.mp3"
            with open(webm_file_path, "wb") as f:
                f.write(audio_bytes)

            transcript_span = speech_to_text(webm_file_path)
            transcript_eng = translate_text(transcript_span)
            print("English Translation:", transcript_eng)

            st.session_state.user_query_span = transcript_span
            st.session_state.user_query_eng = transcript_eng

            if transcript_eng:
                st.session_state.messages.append({"role": "user", "content": transcript_span, "content_eng": transcript_eng})
                with st.chat_message("user"):
                    st.write(transcript_span)
                    st.write(f"*{transcript_eng}*")
                os.remove(webm_file_path)

    elif st.session_state.user_query_eng:
        print('entering the user input...')
        st.session_state.user_query_span = translate_text(st.session_state.user_query_eng, target_language='es')

        st.session_state.messages.append({"role": "user", "content": st.session_state.user_query_span, "content_eng": st.session_state.user_query_eng})
        with st.chat_message("user"):
            st.write(st.session_state.user_query_span)
            st.write(f"*{st.session_state.user_query_eng}*")

# Process the assistant's response
if st.session_state.user_query_eng and st.session_state.messages[-1]["role"] == "user" and not st.session_state.stop_audio:
    with st.chat_message("assistant"):
        with st.spinner("Thinking🤔..."):
            response = query_engine.query(st.session_state.user_query_eng)
            final_response = response.response if hasattr(response, 'response') else str(response)
            print("LLM Response in English: ", final_response)
            final_response_spanish = translate_text(final_response, target_language='es')
        with st.spinner("Generating response..."):
            audio_file = text_to_speech(str(final_response_spanish))
            if not st.session_state.stop_audio:
                autoplay_audio(audio_file)
        st.write(final_response_spanish)
        st.write(f"*{final_response}*")
        st.session_state.messages.append({"role": "assistant", "content": final_response_spanish, "content_eng": final_response})
        os.remove(audio_file)

    st.session_state.user_query_eng = ""
    st.session_state.user_query_span = ""

# Reset the stop_audio flag
if st.session_state.stop_audio:
    st.session_state.stop_audio = False

# Float the footer container to the bottom
footer_container.float("bottom: 0rem; color: white; background-color: #333; padding: 10px;")
