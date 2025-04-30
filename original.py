import os
import time
import pygame
from gtts import gTTS
import streamlit as st
import speech_recognition as sr
from googletrans import LANGUAGES, Translator

# Set page configuration and styling
st.set_page_config(
    page_title="Real-Time Language Translator",
    page_icon="🌐",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1E88E5;
    text-align: center;
    margin-bottom: 1rem;
    padding: 1rem;
    border-bottom: 2px solid #1E88E5;
}
.sub-header {
    font-size: 1.8rem;
    color: #0D47A1;
    padding: 0.5rem;
    margin-top: 2rem;
    border-bottom: 1px solid #90CAF9;
}
.status-box {
    padding: 1rem;
    border-radius: 10px;
    background-color: #5E5E5E;
    color: white;
    text-align: center;
    font-size: 1.2rem;
    margin: 1rem 0;
}
.button-container {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin: 1.5rem 0;
}
.language-section {
    background-color: #F5F5F5;
    padding: 1.5rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
}
.conversation-entry {
    margin-bottom: 0.5rem;
    padding: 0.5rem;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

isTranslateOn = False

translator = Translator() # Initialize the translator module.
pygame.mixer.init()  # Initialize the mixer module.

# Create a mapping between language names and language codes
language_mapping = {name: code for code, name in LANGUAGES.items()}

# Initialize conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

def get_language_code(language_name):
    return language_mapping.get(language_name, language_name)

def translator_function(spoken_text, from_language, to_language):
    return translator.translate(spoken_text, src='{}'.format(from_language), dest='{}'.format(to_language))

def text_to_voice(text_data, to_language):
    myobj = gTTS(text=text_data, lang='{}'.format(to_language), slow=False)
    myobj.save("cache_file.mp3")
    audio = pygame.mixer.Sound("cache_file.mp3")  # Load a sound.
    audio.play()
    os.remove("cache_file.mp3")

def main_process(output_placeholder, from_language, to_language, from_language_name, to_language_name):
    
    global isTranslateOn
    
    while isTranslateOn:

        rec = sr.Recognizer()
        with sr.Microphone() as source:
            output_placeholder.markdown("<div class='status-box'>🎤 Listening...</div>", unsafe_allow_html=True)
            rec.pause_threshold = 1
            audio = rec.listen(source, phrase_time_limit=10)
        
        try:
            output_placeholder.markdown("<div class='status-box'>⚙️ Processing...</div>", unsafe_allow_html=True)
            spoken_text = rec.recognize_google(audio, language='{}'.format(from_language))
            
            output_placeholder.markdown("<div class='status-box'>🔄 Translating...</div>", unsafe_allow_html=True)
            translated_text = translator_function(spoken_text, from_language, to_language)

            # Add to conversation history
            st.session_state.conversation_history.append({
                "original": spoken_text,
                "original_language": from_language_name,
                "translated": translated_text.text,
                "translated_language": to_language_name,
                "timestamp": time.strftime("%H:%M:%S")
            })

            text_to_voice(translated_text.text, to_language)
    
        except Exception as e:
            output_placeholder.markdown("<div class='status-box'>❌ Error: Could not process audio. Please try again.</div>", unsafe_allow_html=True)
            print(e)

# UI layout
st.markdown("<h1 class='main-header'>🌐 Real-Time Language Translator</h1>", unsafe_allow_html=True)

# Add a brief description
st.markdown("""<div style='text-align: center; margin-bottom: 2rem;'>
    Speak in one language and instantly translate to another! 
    Perfect for conversations across language barriers.
</div>""", unsafe_allow_html=True)

# Create two columns for language selection
col1, col2 = st.columns(2)

with st.container():
    st.markdown("<div class='language-section'>", unsafe_allow_html=True)
    # Dropdowns for selecting languages
    with col1:
        st.markdown("### 🗣️ Source Language")
        from_language_name = st.selectbox("Select the language you'll speak in:", list(LANGUAGES.values()))
    
    with col2:
        st.markdown("### 🎯 Target Language")
        to_language_name = st.selectbox("Select the language to translate to:", list(LANGUAGES.values()))
    
    # Convert language names to language codes
    from_language = get_language_code(from_language_name)
    to_language = get_language_code(to_language_name)
    st.markdown("</div>", unsafe_allow_html=True)

# Button to trigger translation with better styling
st.markdown("<div class='button-container'>", unsafe_allow_html=True)
col3, col4 = st.columns([1, 1])
with col3:
    start_button = st.button("🎙️ Start Translation", use_container_width=True, type="primary")
with col4:
    stop_button = st.button("⏹️ Stop Translation", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Status placeholder
status_placeholder = st.empty()

# Check if "Start" button is clicked
if start_button:
    if not isTranslateOn:
        isTranslateOn = True
        output_placeholder = st.empty()
        main_process(output_placeholder, from_language, to_language, from_language_name, to_language_name)

# Check if "Stop" button is clicked
if stop_button:
    isTranslateOn = False
    status_placeholder.markdown("<div class='status-box'>✅ Translation stopped</div>", unsafe_allow_html=True)

# Display conversation history
st.markdown("<h2 class='sub-header'>💬 Conversation History</h2>", unsafe_allow_html=True)
if st.session_state.conversation_history:
    for i, entry in enumerate(reversed(st.session_state.conversation_history)):
        with st.expander(f"🔄 Conversation {len(st.session_state.conversation_history) - i} - {entry['timestamp']}"):
            st.markdown(f"""<div class='conversation-entry' style='background-color: #4CAF50; color: white;'>
                <strong>🗣️ Original ({entry['original_language']}):</strong> {entry['original']}
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class='conversation-entry' style='background-color: #2196F3; color: white;'>
                <strong>🎯 Translation ({entry['translated_language']}):</strong> {entry['translated']}
            </div>""", unsafe_allow_html=True)
else:
    st.info("📝 No conversation history yet. Start translating to see your conversation here.")

# Add a footer
# Add a footer with copyright
st.markdown("""<div style='text-align: center; margin-top: 3rem; padding: 1rem; border-top: 1px solid #90CAF9; color: #757575;'>
    © 2025 [dsnp01555]. All rights reserved. | 🌐 Real-Time Language Translator | Made using Streamlit
</div>""", unsafe_allow_html=True)
