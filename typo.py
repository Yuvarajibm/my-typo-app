#  streamlit run typo.py

import streamlit as st
import requests
from bs4 import BeautifulSoup
from spellchecker import SpellChecker
import re
import os

# ---------------- Configuration ----------------
EXCLUDED_PHRASES = {"short form"}
CUSTOM_DICT_FILE = "custom_dictionary.txt"

# ---------------- Utility Functions ----------------
def load_custom_dictionary():
    """Load custom words from file."""
    if os.path.exists(CUSTOM_DICT_FILE):
        with open(CUSTOM_DICT_FILE, "r") as f:
            return set(line.strip().lower() for line in f if line.strip())
    return set()

def save_to_custom_dictionary(word):
    """Add a word to the custom dictionary file (if not already there)."""
    custom_words = load_custom_dictionary()
    if word.lower() not in custom_words:
        with open(CUSTOM_DICT_FILE, "a") as f:
            f.write(word.lower() + "\n")

# ---------------- Content Extractor ----------------
def extract_text_from_url(url):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        texts = soup.stripped_strings
        return " ".join(texts)
    except Exception as e:
        return f"Error fetching content: {e}"

# ---------------- Typo Checker ----------------
def find_typos(text):
    spell = SpellChecker()
    text_lower = text.lower()

    for phrase in EXCLUDED_PHRASES:
        text_lower = text_lower.replace(phrase, "")

    words = re.findall(r"\b[a-zA-Z]+\b", text_lower)
    misspelled = spell.unknown(words)

    # Exclude words already in custom dictionary
    custom_words = load_custom_dictionary()
    final_typos = [word for word in misspelled if word.lower() not in custom_words]

    return sorted(final_typos)

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Typo Checker with Dictionary", layout="wide")
st.title("📋 Email Content Analyzer – Typo Checker")

url = st.text_input("🔗 Enter a URL to analyze:")

if url:
    with st.spinner("Fetching and analyzing..."):
        content = extract_text_from_url(url)

        if content.startswith("Error"):
            st.error(content)
        else:
            # --- Typo Analysis ---
            typos = find_typos(content)
            st.subheader("🔍 Possible Typos")

            if typos:
                for typo in typos:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.error(f"- {typo}")
                    with col2:
                        if st.button("Add to Dictionary", key=typo):
                            save_to_custom_dictionary(typo)
                            st.success(f"✅ Added '{typo}' to dictionary!")
                            st.rerun()
            else:
                st.success("✅ No typos found!")
