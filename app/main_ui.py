import streamlit as st
from datetime import datetime
import base64
import sys
from pathlib import Path
import os

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from main import process_audio
from utils.exporters import export_pdf, export_html, export_txt

# Inject dark theme CSS
def inject_css():
    st.markdown("""
        <style>
        body {
            background-color: #1e1e1e;
            color: #f5f5f5;
        }
        .stApp {
            background: linear-gradient(to right, #1c1c1c, #2a2a2a);
            color: #f5f5f5;
        }
        .stButton > button {
            border-radius: 10px;
            border: none;
            background-color: #ff4b4b;
            color: white;
        }
        .stDownloadButton > button {
            background-color: #4CAF50;
            color: white;
            border-radius: 10px;
        }
        .css-1v0mbdj {  /* hide Streamlit’s default hamburger */
            visibility: hidden;
        }
        audio {
            width: 100%;
            margin-top: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

# Audio player component
def audio_player(audio_bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    html = f"""
    <audio controls>
    <source src="data:audio/wav;base64,{b64}" type="audio/wav">
    </audio>
    """
    st.markdown(html, unsafe_allow_html=True)

# Export summary to desired format
def generate_export(result: dict, export_format: str) -> bytes:
    filename = "streamlit_export_output"
    export_dir = "app/temp_export"
    os.makedirs(export_dir, exist_ok=True)
    filepath = os.path.join(export_dir, f"{filename}.{export_format}")

    if export_format == "pdf":
        export_pdf(result["summary"], filepath)
    elif export_format == "html":
        export_html(result["summary"], filepath)
    else:
        export_txt(result["summary"], filepath)

    with open(filepath, "rb") as f:
        return f.read()

# Main UI
def main():
    st.set_page_config(
        page_title="WhisprSync Pro",
        page_icon="🎙️",
        layout="wide"
    )
    inject_css()

    # Warning block (important usage hint)
    st.warning(
        "⚠️ Before uploading:\n"
        "- Select export format from the sidebar.\n"
        "- If your audio is longer than 1 minute, enable 'Cloud Processing' and enter your GCS bucket name.",
        icon="⚠️"
    )

    # Sidebar
    with st.sidebar:
        st.title("⚙️ Meeting Settings")
        auto_summarize = st.checkbox("✨ Auto-Summarize", True)
        export_format = st.selectbox("📤 Export Format", options=["pdf", "html", "txt"], index=0)
        advanced = st.expander("🔧 Advanced Options")
        with advanced:
            use_gcs = st.checkbox("Enable Cloud Processing (for long audio files)")
            gcs_bucket = st.text_input("GCS Bucket Name") if use_gcs else None

    # Main Area
    st.header("🎙️ Upload Meeting Recording")
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("### Select audio file")
        audio_file = st.file_uploader("Upload audio file", type=["wav", "mp3"], label_visibility="collapsed")

        if audio_file:
            audio_bytes = audio_file.read()

            if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != audio_file.name:
                st.session_state.last_uploaded = audio_file.name

                with st.spinner("Processing..."):
                    with open("temp_audio.wav", "wb") as f:
                        f.write(audio_bytes)

                    result = process_audio(
                        "temp_audio.wav",
                        summarize=auto_summarize,
                        long_file=use_gcs,
                        gcs_bucket=gcs_bucket
                    )

                    st.session_state.result = result
            else:
                result = st.session_state.result

            st.success("✅ Processing Complete")
            audio_player(audio_bytes)

            # Transcript section
            with st.expander("📝 Full Transcript", expanded=True):
                st.write(result["transcript"])

            # Summary
            if auto_summarize:
                st.subheader("📌 AI Summary")
                tab1, tab2 = st.tabs(["Key Points", "Action Items"])
                for point in result["summary"].get("key_points", []):
                    tab1.markdown(f"- {point}")
                for action in result["summary"].get("action_items", []):
                    tab2.markdown(f"✅ {action}")

    with col2:
        st.subheader("💡 Insights")
        if audio_file:
            st.info("📊 Visualizations (speaker timeline/sentiment) coming soon!")

            # Export
            exported_bytes = generate_export(result, export_format)
            st.download_button(
                label="📥 Export Summary",
                data=exported_bytes,
                file_name=f"meeting_summary_{datetime.now().date()}.{export_format}",
                mime="application/octet-stream"
            )

if __name__ == "__main__":
    main()
