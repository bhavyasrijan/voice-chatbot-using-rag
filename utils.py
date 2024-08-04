from google.cloud import speech
from google.cloud import texttospeech
from google.cloud import translate_v2 as translate
from llama_index.core.query_engine import RetrieverQueryEngine
#from rag import rag_model
from llama_index.core import get_response_synthesizer
#from pybase64 import b64encode
import base64
import streamlit as st
import os
#import wave
#from pydub import AudioSegment
import librosa
import soundfile as sf

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'my_service_account.json'


def convert_mp3_to_mono_wav(mp3_file_path):
    try:
        # Load the MP3 file
        audio, sr = librosa.load(mp3_file_path, sr=16000, mono=True)
        print("MP3 file loaded successfully")

        # Write to WAV file
        mono_wav_file_path = os.path.splitext(mp3_file_path)[0] + "_mono.wav"
        sf.write(mono_wav_file_path, audio, sr, format='WAV')
        print("Conversion to mono WAV successful")

        return mono_wav_file_path
    except Exception as e:
        #print(f"Error loading or converting MP3 file: {e}")
        return None


#convert_mp3_to_mono_wav('temp_audio.mp3')

'''def get_sample_rate(file_path):
    with wave.open(file_path, 'rb') as wave_file:
        return wave_file.getframerate()'''

def speech_to_text(audio_data):
    # Convert MP3 to mono WAV
    audio_data_wav = convert_mp3_to_mono_wav(audio_data)
    if not audio_data_wav:
        return "Error converting audio file or your code just initialized and there is no audio yet..."

    # Initialize the client
    client = speech.SpeechClient()

    # Load the audio into memory
    with open(audio_data_wav, "rb") as audio_file:
        content = audio_file.read()

    # Configure the request
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="es-ES"
    )

    # Perform the speech recognition request
    response = client.recognize(config=config, audio=audio)

    # Process the response and concatenate the transcriptions
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript

    return transcript



def text_to_speech(input_text):
    # Initialize the client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=input_text)

    # Build the voice request, select the language code and the voice
    voice = texttospeech.VoiceSelectionParams(
        language_code="es-ES",
        name="es-ES-Wavenet-C"
)

    

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # The response's audio_content is binary.
    webm_file_path = "temp_audio_play.mp3"
    with open(webm_file_path, "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)

    return webm_file_path



def translate_text(text, target_language='en'):
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language=target_language)
    #print("English Translation: ",result['translatedText'])
    return result['translatedText']



'''calling RAG inside get_answer function'''

def get_answer(messages):
    '''response_synthesizer = get_response_synthesizer()
    # Assemble query engine
    query_engine = RetrieverQueryEngine(
    retriever=rag_model.retriever_func(),
    response_synthesizer=response_synthesizer,
)'''
    #response = rag_model.query(messages)
    #return response

    


def autoplay_audio(file_path:str):

    with open(file_path,'rb') as f:
        data = f.read()
    b64= base64.b64encode(data).decode('utf-8')

    #using markdown and html audio tag to play our audio on any web page
    md=f"""<audio autoplay>                                       
    <source src= "data: audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """

    st.markdown(md,unsafe_allow_html=True)
    


audio_file_path = "temp_audio.mp3"
print(speech_to_text(audio_file_path))