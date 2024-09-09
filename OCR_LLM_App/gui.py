import streamlit as st
from PIL import Image, ImageEnhance
from preprocessing import preprocess_image
from ocr import extract_text
from llm_integration import correct_text
from chatbot import start_chatbot
from streamlit_cropper import st_cropper

def show_gui():
    # Inject custom CSS
    st.markdown("""
        <style>
        .css-18e3th9 {
            padding-top: 2rem;
            padding-right: 1rem;
            padding-left: 1rem;
            padding-bottom: 1rem;
        }
        .css-1d391kg {
            font-size: 18px;
            font-weight: bold;
            color: #6C63FF;
        }
        .stButton>button {
            background-color: #6C63FF;
            color: white;
            border-radius: 5px;
        }
        .stTextInput>div>input {
            border: 2px solid #6C63FF;
        }
        </style>
        """, unsafe_allow_html=True)

    # Initialize session state
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = ""
    if 'corrected_text' not in st.session_state:
        st.session_state.corrected_text = ""

    uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

    ocr_language = st.selectbox("Select OCR Language", options=["en", "hi", "mr"])
    llm_language = st.selectbox("Select LLM Correction Language", options=["English", "Hindi", "Marathi"])

    if uploaded_image is not None:
        try:
            image = Image.open(uploaded_image)

            # Cropping tool
            st.write("Crop the image (optional):")
            cropped_image = st_cropper(image, realtime_update=True, box_color='#6C63FF')

            # Validate cropped image
            if cropped_image is None:
                st.error("Cropped image is invalid. Please try again.")
                return

            # Brightness adjustment
            st.write("Adjust brightness (optional):")
            brightness = st.slider("Brightness", 0.0, 2.0, 1.0)

            # Ensure the cropped image is in RGB mode for enhancement
            if cropped_image.mode != "RGB":
                cropped_image = cropped_image.convert("RGB")

            # Enhance brightness
            enhancer = ImageEnhance.Brightness(cropped_image)
            enhanced_image = enhancer.enhance(brightness)

            # Display enhanced image
            st.image(enhanced_image, caption='Enhanced Image', use_column_width=True)

            # "Submit" button to confirm enhancement
            if st.button("Submit Enhanced Image"):
                # Process the enhanced image
                processed_image = preprocess_image(enhanced_image)

                st.write("Extracting text...")
                st.session_state.extracted_text = extract_text(processed_image, [ocr_language])

                st.write("Correcting text using Cohere API...")
                st.session_state.corrected_text = correct_text(st.session_state.extracted_text, llm_language)

        except Exception as e:
            st.error(f"An error occurred: {e}")

    # Display the extracted text if available
    if st.session_state.extracted_text:
        st.text_area("Extracted Text", st.session_state.extracted_text, height=150)

    # Display the corrected text if available
    if st.session_state.corrected_text:
        st.text_area("Corrected Text", st.session_state.corrected_text, height=150)

        if st.button("Copy Corrected Text"):
            st.write("Corrected text copied to clipboard.")
            st.code(st.session_state.corrected_text, language='')

    # Start chatbot with the corrected text
    if st.session_state.corrected_text:
        st.write("## Chat with Corrected Text")
        start_chatbot(st.session_state.corrected_text, llm_language)

