import streamlit as st
from markitdown import MarkItDown, StreamInfo
from openai import OpenAI

# --- Format registry ---
FORMAT_MAP = {
    ".pdf":   ".pdf",
    ".docx":  ".docx",
    ".pptx":  ".pptx",
    ".xlsx":  ".xlsx",
    ".xls":   ".xls",
    ".html":  ".html",
    ".htm":   ".htm",
    ".csv":   ".csv",
    ".json":  ".json",
    ".xml":   ".xml",
    ".txt":   ".txt",
    ".md":    ".md",
    ".rst":   ".rst",
    ".jpg":   ".jpg",
    ".jpeg":  ".jpeg",
    ".png":   ".png",
    ".gif":   ".gif",
    ".bmp":   ".bmp",
    ".webp":  ".webp",
    ".tiff":  ".tiff",
    ".tif":   ".tif",
    ".mp3":   ".mp3",
    ".wav":   ".wav",
    ".m4a":   ".m4a",
    ".ogg":   ".ogg",
    ".flac":  ".flac",
    ".zip":   ".zip",
    ".rss":   ".rss",
    ".atom":  ".atom",
    ".epub":  ".epub",
    ".msg":   ".msg",
    ".eml":   ".eml",
}

ALL_EXTENSIONS = list(FORMAT_MAP.keys())
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}

# ---- Page config (must be first) ----
st.set_page_config(page_title="MarkItDown Converter", page_icon="📄", layout="centered")

# ---- Sidebar ----
with st.sidebar:
    st.header("🤖 LLM Settings")
    st.caption("Required for images and audio files. Not needed for PDFs, Office docs, etc.")

    provider = st.selectbox("Provider", ["None", "OpenAI", "Gemini"])
    api_key = st.text_input("API Key", type="password", placeholder="Paste your API key...")

    if provider == "OpenAI":
        model = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini"], index=1)
    elif provider == "Gemini":
        model = st.selectbox("Model", ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"], index=0)
    else:
        model = None

    if api_key and provider != "None":
        st.success(f"{provider} enabled ✅")
    else:
        st.info("No LLM — text-based files only.")

# ---- Init MarkItDown ----
if api_key and provider == "OpenAI":
    client = OpenAI(api_key=api_key)
    md = MarkItDown(llm_client=client, llm_model=model)

elif api_key and provider == "Gemini":
    client = OpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    md = MarkItDown(llm_client=client, llm_model=model)

else:
    md = MarkItDown()

# ---- Main UI ----
st.title("📄 MarkItDown Converter")
st.write("Convert **any supported file** to clean Markdown — PDFs, Office docs, images, audio, archives, and more.")

with st.expander("📋 Supported formats"):
    cols = st.columns(4)
    for i, ext in enumerate(sorted(ALL_EXTENSIONS)):
        cols[i % 4].code(ext)

uploaded_file = st.file_uploader(
    "Choose a file",
    type=[e.lstrip(".") for e in ALL_EXTENSIONS],
    help="Supports PDF, DOCX, PPTX, XLSX, HTML, CSV, JSON, images, audio, ZIP, EPUB, MSG and more."
)

if uploaded_file is not None:
    filename = uploaded_file.name
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    st.info(f"**File:** `{filename}` — detected as `{ext or 'unknown'}`")

    needs_llm = ext in IMAGE_EXTS | AUDIO_EXTS

    if needs_llm and not api_key:
        st.warning("⚠️ Images and audio require an LLM API key. Add it in the sidebar to proceed.")
        st.stop()

    if ext not in FORMAT_MAP:
        st.warning(f"Extension `{ext}` isn't in the known list. Attempting conversion anyway — results may vary.")

    stream_ext = FORMAT_MAP.get(ext, ext)

    with st.spinner(f"Converting `{filename}` …"):
        try:
            result = md.convert_stream(
                uploaded_file,
                stream_info=StreamInfo(extension=stream_ext)
            )
            md_text = result.text_content

            if not md_text or not md_text.strip():
                st.warning("Conversion succeeded but the output is empty.")
            else:
                st.success(f"✅ Conversion successful! ({len(md_text):,} characters)")
                st.text_area("Preview", md_text, height=300)

                out_name = filename.rsplit(".", 1)[0] + ".md" if "." in filename else filename + ".md"
                st.download_button(
                    label="📥 Download .md file",
                    data=md_text,
                    file_name=out_name,
                    mime="text/markdown",
                )

        except Exception as e:
            st.error(f"Conversion failed: {e}")