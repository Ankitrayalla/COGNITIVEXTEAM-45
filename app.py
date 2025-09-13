import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"  # change if backend is remote

st.set_page_config(page_title="EchoVerse", layout="wide")
st.title("EchoVerse — Tone-adaptive Audiobook Creator")

col1, col2 = st.columns([2,1])

with col1:
    st.header("Input")
    mode = st.radio("Input mode", ["Paste text", "Upload .txt file"])
    text = st.text_area("Paste text here", height=250)
    if mode == "Upload .txt file":
        f = st.file_uploader("Upload a .txt file", type=["txt"])
        if f:
            text = f.getvalue().decode("utf-8")

    tone = st.selectbox("Tone", ["Neutral", "Suspenseful", "Inspiring"])
    max_tokens = st.slider("Max tokens for rewrite", 64, 2048, 512)
    rewrite_btn = st.button("Rewrite")

with col2:
    st.header("TTS & Voices")
    try:
        voices = requests.get(f"{BACKEND_URL}/voices", timeout=5).json()
        voice_list = list(voices.keys())
    except Exception:
        voice_list = []
    selected_voice = st.selectbox("Voice", options=(voice_list or ["Default"]))
    rate = st.slider("Speech rate", 100, 220, 150)
    gen_audio_btn = st.button("Generate Audio from Rewritten")

if rewrite_btn:
    if not text.strip():
        st.error("Please provide text to rewrite")
    else:
        payload = {"text": text, "tone": tone, "max_tokens": max_tokens}
        try:
            resp = requests.post(f"{BACKEND_URL}/rewrite", json=payload, timeout=60)
            resp.raise_for_status()
            rewritten = resp.json().get("rewritten", "")
            st.subheader("Side-by-side")
            c1, c2 = st.columns(2)
            c1.text_area("Original", value=text, height=250)
            c2.text_area("Rewritten", value=rewritten, height=250)
            st.session_state["rewritten"] = rewritten
        except Exception as e:
            st.error(f"Rewrite request failed: {e}")

if gen_audio_btn:
    rewritten = st.session_state.get("rewritten", "")
    if not rewritten:
        st.error("Please run Rewrite first to create text for audio")
    else:
        payload = {"text": rewritten, "voice": None if selected_voice=="Default" else selected_voice, "rate": rate}
        try:
            resp = requests.post(f"{BACKEND_URL}/tts", json=payload, timeout=120)
            resp.raise_for_status()
            mp3_bytes = resp.content
            st.audio(mp3_bytes, format="audio/mp3")
            st.download_button("Download MP3", data=mp3_bytes, file_name="echoverse_narration.mp3", mime="audio/mpeg")
        except Exception as e:
            st.error(f"Audio request failed: {e}")
