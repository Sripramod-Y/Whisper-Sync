from google.cloud import speech
import os
from utils.formatter import format_transcript
from typing import Union 

def transcribe_audio(
        audio_path: str,
        is_long_file: bool = False,
        gcs_uri: str = None  # For files uploaded too Google Cloud Storage          
    ) -> dict:
    client = speech.SpeechClient()

    # Config 
    config = speech.RecognitionConfig(
        encoding  = speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz = 16000,
        language_code = "en-US",
        enable_word_time_offsets = True,
    )

    # Case 1 : Local File (short)
    if not is_long_file:
        with open(audio_path, "rb") as f:
            content = f.read()
        audio = speech.RecognitionAudio(content = content)
        response = client.recognize(config=config, audio=audio)
        return _format_response(response)
    
    # Case 2 : Long Fole (async via GCS)
    audio = speech.RecognitionAudio(uri=gcs_uri)
    operation = client.long_running_recognize(config = config, audio = audio)
    response = operation.result(timeout = 90)
    return _format_response(response)

def _format_response(response) -> dict:
    """ Extract transcript + timestamps from response. """
    full_text = []
    words = []
    for result in response.results:
        transcript = result.alternatives[0].transcript
        if not transcript.endswith(('.','?','!')):
            transcript += '.'
        full_text.append(transcript)
        for word in result.alternatives[0].words:
            words.append({
                "word": word.word,
                "start": word.start_time.total_seconds(),
                "end": word.end_time.total_seconds()
            })
        if not full_text:
            raise ValueError("No speech detected in audio")
    formatted_text = format_transcript(" ".join(full_text))
    return{
        "text" : formatted_text,
        "words" : words
    }