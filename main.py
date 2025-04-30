import os
import time
import pygame
import tempfile
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
.warning-box {
    background-color: #FFF3CD;
    color: #856404;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    border-left: 5px solid #FFD700;
}
.info-box {
    background-color: #CCE5FF;
    color: #004085;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    border-left: 5px solid #2196F3;
}
</style>
""", unsafe_allow_html=True)

isTranslateOn = False

# Initialize the translator module
translator = Translator()

# Check if pygame mixer can be initialized
try:
    pygame.mixer.init()
    audio_output_available = True
except:
    audio_output_available = False

# Create a mapping between language names and language codes
language_mapping = {name: code for code, name in LANGUAGES.items()}

# Initialize conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Check if microphone is available
def is_microphone_available():
    try:
        with sr.Microphone() as source:
            return True
    except (sr.RequestError, OSError):
        return False

microphone_available = is_microphone_available()

def get_language_code(language_name):
    return language_mapping.get(language_name, language_name)

def translator_function(spoken_text, from_language, to_language):
    try:
        return translator.translate(spoken_text, src=from_language, dest=to_language)
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return None

def text_to_voice(text_data, to_language):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_filename = temp_file.name
        
        myobj = gTTS(text=text_data, lang=to_language, slow=False)
        myobj.save(temp_filename)
        
        if audio_output_available:
            audio = pygame.mixer.Sound(temp_filename)
            audio.play()
            # Wait for playback to finish
            pygame.time.wait(int(audio.get_length() * 1000))
        
        # Clean up the temporary file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
    except Exception as e:
        st.error(f"Text-to-speech error: {str(e)}")

def main_process(output_placeholder, from_language, to_language, from_language_name, to_language_name):
    global isTranslateOn
    
    while isTranslateOn:
        try:
            rec = sr.Recognizer()
            with sr.Microphone() as source:
                output_placeholder.markdown("<div class='status-box'>🎤 Listening...</div>", unsafe_allow_html=True)
                rec.pause_threshold = 1
                audio = rec.listen(source, phrase_time_limit=10)
            
            output_placeholder.markdown("<div class='status-box'>⚙️ Processing...</div>", unsafe_allow_html=True)
            spoken_text = rec.recognize_google(audio, language=from_language)
            
            output_placeholder.markdown("<div class='status-box'>🔄 Translating...</div>", unsafe_allow_html=True)
            translated_result = translator_function(spoken_text, from_language, to_language)
            
            if translated_result:
                # Add to conversation history
                st.session_state.conversation_history.append({
                    "original": spoken_text,
                    "original_language": from_language_name,
                    "translated": translated_result.text,
                    "translated_language": to_language_name,
                    "timestamp": time.strftime("%H:%M:%S")
                })
                
                # Play the audio if available
                text_to_voice(translated_result.text, to_language)
                
                # Update the conversation display
                output_placeholder.empty()
        
        except sr.UnknownValueError:
            output_placeholder.markdown("<div class='status-box'>❓ Could not understand audio. Please try again.</div>", unsafe_allow_html=True)
            time.sleep(2)
        except sr.RequestError as e:
            output_placeholder.markdown(f"<div class='status-box'>❌ Error: {str(e)}</div>", unsafe_allow_html=True)
            isTranslateOn = False
        except Exception as e:
            output_placeholder.markdown(f"<div class='status-box'>❌ Error: {str(e)}</div>", unsafe_allow_html=True)
            isTranslateOn = False

def manual_translation_mode(text_input, from_language, to_language, from_language_name, to_language_name):
    if text_input:
        st.markdown("<div class='status-box'>🔄 Translating...</div>", unsafe_allow_html=True)
        translated_result = translator_function(text_input, from_language, to_language)
        
        if translated_result:
            # Add to conversation history
            st.session_state.conversation_history.append({
                "original": text_input,
                "original_language": from_language_name,
                "translated": translated_result.text,
                "translated_language": to_language_name,
                "timestamp": time.strftime("%H:%M:%S")
            })
            
            # Play the audio if available
            if audio_output_available:
                text_to_voice(translated_result.text, to_language)
            
            return translated_result.text
    
    return None

# UI layout
st.markdown("<h1 class='main-header'>🌐 Real-Time Language Translator</h1>", unsafe_allow_html=True)

# Add a brief description
st.markdown("""<div style='text-align: center; margin-bottom: 2rem;'>
    Speak in one language and instantly translate to another! 
    Perfect for conversations across language barriers.
</div>""", unsafe_allow_html=True)

# Display hardware status
if not microphone_available:
    st.markdown("""
    <div class='warning-box'>
        <strong>⚠️ Microphone Not Available:</strong> 
        No microphone device found or access is restricted. You can still use the text input method below.
    </div>
    """, unsafe_allow_html=True)
    
if not audio_output_available:
    st.markdown("""
    <div class='info-box'>
        <strong>ℹ️ Audio Output Unavailable:</strong>
        Audio playback is not available in this environment. Translations will be displayed as text only.
    </div>
    """, unsafe_allow_html=True)

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

# Add text input as an alternative to speech
text_input = st.text_area("📝 Or type text to translate:", height=100)
translate_text_button = st.button("🔄 Translate Text", use_container_width=True, type="primary")

# Process text input if the button is clicked
if translate_text_button and text_input:
    translated_text = manual_translation_mode(text_input, from_language, to_language, from_language_name, to_language_name)
    if translated_text:
        st.markdown(f"""
        <div style='background-color: #2196F3; color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0;'>
            <strong>🎯 Translation:</strong> {translated_text}
        </div>
        """, unsafe_allow_html=True)

# Only show microphone-based translation if available
if microphone_available:
    # Button to trigger translation with better styling
    st.markdown("<div class='button-container'>", unsafe_allow_html=True)
    col3, col4 = st.columns([1, 1])
    with col3:
        start_button = st.button("🎙️ Start Speech Translation", use_container_width=True, type="primary")
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

# Add app configuration settings
with st.expander("⚙️ App Settings"):
    st.markdown("### Clear History")
    if st.button("🗑️ Clear Conversation History"):
        st.session_state.conversation_history = []
        st.experimental_rerun()
    
    st.markdown("### About This App")
    st.markdown("""
    This app uses:
    - Google's Speech Recognition API for speech-to-text
    - Google Translate API for translations
    - gTTS (Google Text-to-Speech) for audio output
    
    Note: This app works best in local environments where microphone access is available.
    """)

# Add a footer with copyright
st.markdown("""<div style='text-align: center; margin-top: 3rem; padding: 1rem; border-top: 1px solid #90CAF9; color: #757575;'>
    © 2025 [dsnp01555]. All rights reserved. | 🌐 Real-Time Language Translator | Made using Streamlit
</div>""", unsafe_allow_html=True)