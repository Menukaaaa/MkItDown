import streamlit as st
from markitdown import MarkItDown, StreamInfo

# Initialize MarkItDown
md = MarkItDown()

# --- Format registry ---
# Maps file extension -> StreamInfo extension hint
FORMAT_MAP = {
    # Office documents
    ".pdf":   ".pdf",
    ".docx":  ".docx",
    ".pptx":  ".pptx",
    ".xlsx":  ".xlsx",
    ".xls":   ".xls",
    # Web
    ".html":  ".html",
    ".htm":   ".htm",
    # Data / text
    ".csv":   ".csv",
    ".json":  ".json",
    ".xml":   ".xml",
    ".txt":   ".txt",
    ".md":    ".md",
    ".rst":   ".rst",
    # Images
    ".jpg":   ".jpg",
    ".jpeg":  ".jpeg",
    ".png":   ".png",
    ".gif":   ".gif",
    ".bmp":   ".bmp",
    ".webp":  ".webp",
    ".tiff":  ".tiff",
    ".tif":   ".tif",
    # Audio
    ".mp3":   ".mp3",
    ".wav":   ".wav",
    ".m4a":   ".m4a",
    ".ogg":   ".ogg",
    ".flac":  ".flac",
    # Archives
    ".zip":   ".zip",
    # Feeds
    ".rss":   ".rss",
    ".atom":  ".atom",
    # E-book
    ".epub":  ".epub",
    # Email
    ".msg":   ".msg",
    ".eml":   ".eml",
}

ALL_EXTENSIONS = list(FORMAT_MAP.keys())

# ---- UI ----
st.set_page_config(page_title="MarkItDown Converter", page_icon="📄", layout="centered")
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

    if ext not in FORMAT_MAP:
        st.warning(
            f"Extension `{ext}` isn't in the known list. "
            "Attempting conversion anyway — results may vary."
        )

    stream_ext = FORMAT_MAP.get(ext, ext)

    with st.spinner(f"Converting `{filename}` …"):
        try:
            result = md.convert_stream(
                uploaded_file,
                stream_info=StreamInfo(extension=stream_ext)
            )
            md_text = result.text_content

            if not md_text or not md_text.strip():
                st.warning("Conversion succeeded but the output is empty. The file may require an LLM client for image/audio description.")
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
            st.caption("If this is an image or audio file, MarkItDown may need an LLM client (e.g. OpenAI GPT-4o) to generate descriptions.")