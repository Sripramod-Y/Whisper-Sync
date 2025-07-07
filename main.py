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
from utils.gcs_utils import upload_to_gcs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Path to audio file", required= True)
    parser.add_argument("--output", help="Ouput format (txt/json)", default = "txt")
    parser.add_argument("--summarize", help = "Enable smart summarization", action = "store_true")
    parser.add_argument("--format", help = "Output format (txt/html/pdf)", default = "pdf")
    parser.add_argument("--export_dir", help = "Custom output directory")
    parser.add_argument("--long", help = "Use long_running_recognise (for > 1min files)", action = "store_true")
    parser.add_argument("--gcs_bucket", help = "GCS Bucket name (required for long files)", default = None)
    args = parser.parse_args()

    if args.long and not args.gcs_bucket:
        raise ValueError("--gcs_bucket required for long files")
    
    # Preprocess audio and Generate Transcript
    if args.long:
        processed_audio = resample_audio(args.input)
        gcs_uri = upload_to_gcs(processed_audio, args.gcs_bucket)
        raw_transcript = transcribe_audio(audio_path=None, is_long_file = True, gcs_uri = gcs_uri)
    else : 
        processed_audio = resample_audio(args.input)
        raw_transcript = transcribe_audio(processed_audio)
    
    # Clean the received raw transcript 
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
        export_dir = args.export_dir or "outputs"
        if args.format == "pdf":
            export_pdf(summary, f"{export_dir}/summaries/summary.pdf")
        elif args.format == "html":
            export_html(summary, f"{export_dir}/summaries/summary.html")
        else:
            export_txt(summary, f"{export_dir}/summaries/summary.txt")

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
    
# Add this function to make core functionality importable
def process_audio(input_path: str, summarize: bool = False, long_file: bool = False, gcs_bucket: str = None) -> dict:
    """Unified processing function for both CLI and UI"""
    from utils.audio_utils import resample_audio
    from utils.sst_client import transcribe_audio
    from utils.text_cleaner import clean_transcript
    from utils.summarizer import extract_keyphrases, find_action_items
    
    # Processing pipeline
    processed_audio = resample_audio(input_path)
    if long_file:
        from utils.gcs_utils import upload_to_gcs
        gcs_uri = upload_to_gcs(processed_audio, gcs_bucket)
        raw_transcript = transcribe_audio(processed_audio, is_long_file=True, gcs_uri=gcs_uri)
    else:
        raw_transcript = transcribe_audio(processed_audio)
    
    cleaned_text = clean_transcript(raw_transcript["text"])
    
    result = {"transcript": cleaned_text, "words": raw_transcript["words"]}
    
    if summarize:
        chunks = chunk_by_pauses(raw_transcript)
        result.update({
            "summary": {
                "key_points": extract_keyphrases(cleaned_text),
                "action_items": find_action_items(cleaned_text),
                "chunks" : chunks
            }
        })
    
    return result



if __name__ == "__main__":
    main()