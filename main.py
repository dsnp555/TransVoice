import os
import time
import pygame
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from googletrans import Translator
from io import BytesIO  # For handling in-memory audio playback

# Set page configuration
st.set_page_config(
    page_title="Real-Time Language Translator",
    page_icon="🌐",
    layout="wide"
)

# Apply Custom Styling
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

# Translator setup
try:
    translator = Translator()
    # Test the translator
    translator.translate('Hello', dest='es')
except Exception as e:
    st.error(f"Failed to initialize translator: {str(e)}")
    translator = None

languages = {
    'af': 'afrikaans', 'sq': 'albanian', 'am': 'amharic', 'ar': 'arabic', 'hy': 'armenian',
    'az': 'azerbaijani', 'eu': 'basque', 'be': 'belarusian', 'bn': 'bengali', 'bs': 'bosnian',
    'bg': 'bulgarian', 'ca': 'catalan', 'ceb': 'cebuano', 'ny': 'chichewa', 'zh-cn': 'chinese (simplified)',
    'zh-tw': 'chinese (traditional)', 'co': 'corsican', 'hr': 'croatian', 'cs': 'czech', 'da': 'danish',
    'nl': 'dutch', 'en': 'english', 'eo': 'esperanto', 'et': 'estonian', 'tl': 'filipino',
    'fi': 'finnish', 'fr': 'french', 'fy': 'frisian', 'gl': 'galician', 'ka': 'georgian',
    'de': 'german', 'el': 'greek', 'gu': 'gujarati', 'ht': 'haitian creole', 'ha': 'hausa',
    'haw': 'hawaiian', 'iw': 'hebrew', 'he': 'hebrew', 'hi': 'hindi', 'hmn': 'hmong',
    'hu': 'hungarian', 'is': 'icelandic', 'ig': 'igbo', 'id': 'indonesian', 'ga': 'irish',
    'it': 'italian', 'ja': 'japanese', 'jw': 'javanese', 'kn': 'kannada', 'kk': 'kazakh',
    'km': 'khmer', 'ko': 'korean', 'ku': 'kurdish (kurmanji)', 'ky': 'kyrgyz', 'lo': 'lao',
    'la': 'latin', 'lv': 'latvian', 'lt': 'lithuanian', 'lb': 'luxembourgish', 'mk': 'macedonian',
    'mg': 'malagasy', 'ms': 'malay', 'ml': 'malayalam', 'mt': 'maltese', 'mi': 'maori',
    'mr': 'marathi', 'mn': 'mongolian', 'my': 'myanmar (burmese)', 'ne': 'nepali', 'no': 'norwegian',
    'or': 'odia', 'ps': 'pashto', 'fa': 'persian', 'pl': 'polish', 'pt': 'portuguese',
    'pa': 'punjabi', 'ro': 'romanian', 'ru': 'russian', 'sm': 'samoan', 'gd': 'scots gaelic',
    'sr': 'serbian', 'st': 'sesotho', 'sn': 'shona', 'sd': 'sindhi', 'si': 'sinhala',
    'sk': 'slovak', 'sl': 'slovenian', 'so': 'somali', 'es': 'spanish', 'su': 'sundanese',
    'sw': 'swahili', 'sv': 'swedish', 'tg': 'tajik', 'ta': 'tamil', 'te': 'telugu',
    'th': 'thai', 'tr': 'turkish', 'uk': 'ukrainian', 'ur': 'urdu', 'ug': 'uyghur',
    'uz': 'uzbek', 'vi': 'vietnamese', 'cy': 'welsh', 'xh': 'xhosa', 'yi': 'yiddish',
    'yo': 'yoruba', 'zu': 'zulu'
}

# Update language mapping
language_mapping = {name: code for code, name in languages.items()}
isTranslateOn = False

# Initialize conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

def get_language_code(language_name):
    return language_mapping.get(language_name, language_name)

def translator_function(spoken_text, from_language, to_language):
    try:
        if translator is None:
            raise Exception("Translator not initialized")
        
        # Add retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = translator.translate(spoken_text, src=from_language, dest=to_language)
                return result
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(1)  # Wait before retrying
                
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return None

def text_to_voice(text_data, to_language):
    """Converts text to speech and returns it as an audio file in memory"""
    myobj = gTTS(text=text_data, lang=to_language, slow=False)
    
    # Store audio in memory instead of saving a file
    audio_bytes = BytesIO()
    myobj.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    
    return audio_bytes

def initialize_microphone():
    """Initialize and test microphone access"""
    try:
        rec = sr.Recognizer()
        with sr.Microphone() as source:
            return True, rec, None
    except OSError as e:
        return False, None, "No microphone device found. Please check your microphone connection and system audio settings."
    except Exception as e:
        return False, None, f"Error initializing microphone: {str(e)}"

def main_process(output_placeholder, from_language, to_language, from_language_name, to_language_name):
    global isTranslateOn

    # Check microphone before starting
    mic_ok, rec, error_msg = initialize_microphone()
    if not mic_ok:
        output_placeholder.error(error_msg)
        isTranslateOn = False
        return

    while isTranslateOn:
        try:
            with sr.Microphone() as source:
                output_placeholder.markdown("<div class='status-box'>🎤 Listening...</div>", unsafe_allow_html=True)
                rec.pause_threshold = 1
                audio = rec.listen(source, phrase_time_limit=10)
            
            output_placeholder.markdown("<div class='status-box'>⚙️ Processing...</div>", unsafe_allow_html=True)
            spoken_text = rec.recognize_google(audio, language=from_language)
            
            output_placeholder.markdown("<div class='status-box'>🔄 Translating...</div>", unsafe_allow_html=True)
            translated_text = translator_function(spoken_text, from_language, to_language)

            if translated_text:
                # Add to conversation history
                st.session_state.conversation_history.append({
                    "original": spoken_text,
                    "original_language": from_language_name,
                    "translated": translated_text.text,
                    "translated_language": to_language_name,
                    "timestamp": time.strftime("%H:%M:%S")
                })

                # Convert to speech and play in Streamlit
                audio_bytes = text_to_voice(translated_text.text, to_language)
                st.audio(audio_bytes, format="audio/mp3")
    
        except OSError as e:
            output_placeholder.error("Microphone error: Please check your microphone connection")
            isTranslateOn = False
            break
        except Exception as e:
            output_placeholder.markdown("<div class='status-box'>❌ Error: Could not process audio. Please try again.</div>", unsafe_allow_html=True)
            print(e)

# UI layout
st.markdown("<h1 class='main-header'>🌐 Real-Time Language Translator</h1>", unsafe_allow_html=True)
st.markdown("""<div style='text-align: center; margin-bottom: 2rem;'>
    Speak in one language and instantly translate to another! 
    Perfect for conversations across language barriers.
</div>""", unsafe_allow_html=True)

# Create two columns for language selection
col1, col2 = st.columns(2)

with st.container():
    st.markdown("<div class='language-section'>", unsafe_allow_html=True)
    with col1:
        st.markdown("### 🗣️ Source Language")
        from_language_name = st.selectbox("Select the language you'll speak in:", list(languages.values()))
    
    with col2:
        st.markdown("### 🎯 Target Language")
        to_language_name = st.selectbox("Select the language to translate to:", list(languages.values()))
    
    from_language = get_language_code(from_language_name)
    to_language = get_language_code(to_language_name)
    st.markdown("</div>", unsafe_allow_html=True)

# Buttons for starting and stopping translation
st.markdown("<div class='button-container'>", unsafe_allow_html=True)
col3, col4 = st.columns([1, 1])
with col3:
    start_button = st.button("🎙️ Start Translation", use_container_width=True, type="primary")
with col4:
    stop_button = st.button("⏹️ Stop Translation", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Status placeholder
status_placeholder = st.empty()

# Handle button clicks
if start_button:
    if not isTranslateOn:
        isTranslateOn = True
        output_placeholder = st.empty()
        main_process(output_placeholder, from_language, to_language, from_language_name, to_language_name)

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

st.markdown("""<div style='text-align: center; margin-top: 3rem; padding: 1rem; border-top: 1px solid #90CAF9; color: #757575;'>
    © 2025 [Your Name]. All rights reserved. | 🌐 Real-Time Language Translator | Made using Streamlit
</div>""", unsafe_allow_html=True)
