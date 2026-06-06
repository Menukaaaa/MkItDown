import streamlit as st
# Fixed: Imported StreamInfo alongside MarkItDown
from markitdown import MarkItDown, StreamInfo 

# Initialize MarkItDown
md = MarkItDown()

st.title("📄 PDF to Markdown Converter")
st.write("Upload a PDF file to convert it into clean Markdown.")

# File uploader widget
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Converting file..."):
        try:
            # Fixed: Passed an actual StreamInfo object instead of a dict {'extension': '.pdf'}
            result = md.convert_stream(
                uploaded_file, 
                stream_info=StreamInfo(extension=".pdf")
            )
            md_text = result.text_content
            
            st.success("Conversion successful!")
            
            # Show a small preview of the text
            st.text_area("Preview", md_text, height=200)
            
            # Download button for the converted .md file
            st.download_button(
                label="📥 Download Markdown File",
                data=md_text,
                file_name=uploaded_file.name.replace(".pdf", ".md"),
                mime="text/markdown"
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")
