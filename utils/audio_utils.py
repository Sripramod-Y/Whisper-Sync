from pydub import AudioSegment


def resample_audio(input_path : str, output_path : str = "processed.wav") -> str:
    """ Convert raw audio to 16kHz mono wav format """
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(output_path, format="wav")
    return output_path