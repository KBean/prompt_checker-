import streamlit as st
import os
from openai import OpenAI
import json

# === Setup your OpenAI key ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Color map ===
colors = {
    "Role & Goal": "#C70039",         # Red
    "Steps": "#0B3C5D",               # Dark Blue
    "Pedagogy": "#0099CC",            # Light Blue
    "Constraints": "#800080",         # Purple
    "Personalization": "#8B8000"      # Olive
}

# === Streamlit settings ===
st.set_page_config(page_title="AI Coach Inline Highlighter", page_icon="✅", layout="wide")
st.title("🔍 AI Coach Prompt Highlighter — Inline with Index")

st.markdown("""
Paste your **natural prompt** below.  
The app will **automatically highlight** each part (Role & Goal, Steps, Pedagogy, Constraints, Personalization)  
**inline** in your original text — and show a color index for easy comparison.
""")

# === User input ===
prompt = st.text_area("📋 Paste your prompt here:", height=300)

if st.button("✨ Highlight Prompt"):
    with st.spinner("Analyzing and tagging..."):
        # === Call OpenAI to tag ===
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a prompt highlighter. For any input prompt, break it into meaningful sentences or phrases. "
                        "Tag each with one of: Role & Goal, Steps, Pedagogy, Constraints, Personalization. "
                        "Output JSON: [{'text': '...', 'label': '...'}]."
                    )
                },
                {"role": "user", "content": prompt}
            ]
        )

        # === Parse ===
        try:
            tagged = json.loads(response.choices[0].message.content)
        except Exception as e:
            st.error(f"⚠️ Couldn't parse AI response: {e}")
            st.stop()

        # === Layout: prompt with inline colors + side index ===
        col1, col2 = st.columns([4, 1])

        with col1:
            html = ""
            for item in tagged:
                text = item['text']
                label = item['label']
                color = colors.get(label, "#ddd")
                html += f'<span style="background-color:{color}; padding:2px 4px; border-radius:4px; margin:1px; color:white;">{text} </span>'
            st.markdown(html, unsafe_allow_html=True)

        with col2:
            st.markdown("### 📌 Index")
            for label, color in colors.items():
                st.markdown(
                    f'<div style="background-color:{color}; color:white; padding:6px; border-radius:4px; margin-bottom:6px;">{label}</div>',
                    unsafe_allow_html=True
                )
