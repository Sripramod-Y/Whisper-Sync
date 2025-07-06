from google.cloud import speech

def transcribe_audio(audio_path: str) -> dict:
    client = speech.SpeechClient()

    with open(audio_path, "rb") as f:
        content = f.read()
    
    audio = speech.RecognitionAudio(content = content)
    config = speech.RecognitionConfig(
        encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz = 16000,
        language_code = "en-US",
        enable_word_time_offsets = True
    )

    response = client.recognize(config = config, audio = audio)
    transcript = {
        "text": response.results[0].alternatives[0].transcript,
        "words": [{
            "word": word.word,
            "start": word.start_time.total_seconds(),
            "end": word.end_time.total_seconds()
        } for word in response.results[0].alternatives[0].words]
    }

    return transcript