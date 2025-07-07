import argparse
import json
from utils.audio_utils import resample_audio
from utils.sst_client import transcribe_audio
from utils.text_cleaner import clean_transcript
from utils.chunking import chunk_by_pauses
from utils.summarizer import extract_keyphrases, find_action_items


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Path to audio file", required= True)
    parser.add_argument("--output", help="Ouput format (txt/json)", default = "txt")
    parser.add_argument("--summarize", help = "Enable smart summarization", action = "store_true")
    args = parser.parse_args()

    # Preprocess audio
    processed_audio = resample_audio(args.input)

    # Transcribe using Google SST 
    raw_transcript = transcribe_audio(processed_audio)
    cleaned_text = clean_transcript(raw_transcript["text"])

    summary = None
    # Summarization (if enabled)
    if args.summarize:
        chunks = chunk_by_pauses(raw_transcript)

        summary = {
            "key_points" : extract_keyphrases(cleaned_text),
            "action_items" : find_action_items(cleaned_text),
            "chunks" : chunks
        }

        with open("outputs/summary.json","w") as f:
            json.dump(summary, f, indent = 2)

    # Save raw and clean transcript 
    if args.output == "json":
        with open("outputs/output.json","w") as f:
            json.dump({"raw" : raw_transcript, "cleaned" : cleaned_text}, f, indent = 2)
    else:
        with open("outputs/output.txt","w") as f:
            f.write(cleaned_text)
            if args.summarize:
                f.write("\n\n Meeting Summary: \n")
                f.write("- Key Points: \n")
                for point in summary["key_points"]:
                    f.write(f" - {point}\n")
                f.write("\n - Action Items: \n")
                for action in summary["action_items"]:
                    f.write(f"- {action}\n")
    

if __name__ == "__main__":
    main()