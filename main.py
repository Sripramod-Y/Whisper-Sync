import argparse
import json
from utils.audio_utils import resample_audio
from utils.sst_client import transcribe_audio
from utils.text_cleaner import clean_transcript
from utils.chunking import chunk_by_pauses
from utils.summarizer import extract_keyphrases, find_action_items
from utils.exporters import export_txt
from utils.exporters import export_html
from utils.exporters import export_pdf

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Path to audio file", required= True)
    parser.add_argument("--output", help="Ouput format (txt/json)", default = "txt")
    parser.add_argument("--summarize", help = "Enable smart summarization", action = "store_true")
    parser.add_argument("--format", help = "Output format (txt/html/pdf)", default = "pdf")
    parser.add_argument("--export_dir", help = "Custom output directory")
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

        with open("outputs/summaries/summary.json","w") as f:
            json.dump(summary, f, indent = 2)

        # Export summary
        if args.format == "pdf":
            export_pdf(summary, f"{args.export_dir}/summaries/summary.pdf")
        elif args.format == "html":
            export_html(summary, f"{args.export_dir}/summaries/summary.html")
        else:
            export_txt(summary, f"{args.export_dir}/summaries/summary.txt")

    # Save raw and clean transcript 
    if args.output == "json":
        with open("outputs/transcripts/output.json","w") as f:
            json.dump({"raw" : raw_transcript, "cleaned" : cleaned_text}, f, indent = 2)
    else:
        with open("outputs/transcripts/output.txt","w") as f:
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