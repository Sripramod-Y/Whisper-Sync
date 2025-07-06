import argparse
from utils.audio_utils import resample_audio
from utils.sst_client import transcribe_audio
from utils.text_cleaner import clean_transcript
from google.cloud import speech

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Path to audio file", required= True)
    parser.add_argument("--output", help="Ouput format (txt/json)", default = "txt")
    args = parser.parse_args()

    #Process audio
    processed_audio = resample_audio(args.input)
    raw_transcript = transcribe_audio(processed_audio)
    cleaned_text = clean_transcript(raw_transcript["text"])

    if args.output == "json":
        import json
        with open("output.json","w") as f:
            json.dump({"raw" : raw_transcript, "cleaned" : cleaned_text}, f)
    else:
        with open("output.txt","w") as f:
            f.write(cleaned_text)


if __name__ == "__main__":
    main()