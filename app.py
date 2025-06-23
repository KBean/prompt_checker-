import streamlit as st
import os
from openai import OpenAI
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

colors = {
    "Role & Goal": "#C70039",
    "Steps": "#0B3C5D",
    "Pedagogy": "#0099CC",
    "Constraints": "#800080",
    "Personalization": "#8B8000"
}

st.set_page_config(page_title="AI Coach Inline Highlighter", page_icon="✅", layout="wide")
st.title("🔍 AI Coach Prompt Highlighter — Clean & Fixed Width")

st.markdown("""
**Paste your raw prompt below.**  
This tool keeps your prompt input area neat and narrow, shows inline highlights below,  
and keeps the Index aligned to the right.
""")

# === Add custom CSS for fixed width ===
st.markdown("""
    <style>
    .prompt-container {
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    .highlighted-output {
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
""", unsafe_allow_html=True)

# === Columns for layout ===
left, right = st.columns([2, 1])

with left:
    st.markdown('<div class="prompt-container">', unsafe_allow_html=True)

    prompt = st.text_area(
        "📋 Paste your prompt here:",
        height=150,
        placeholder="e.g. Please help me write a PPT as a marketing leader",
    )

    if st.button("✨ Highlight Prompt"):
        with st.spinner("Analyzing..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a prompt highlighter. Break the prompt into sentences or phrases. "
                            "Tag each as: Role & Goal, Steps, Pedagogy, Constraints, Personalization. "
                            "Output ONLY valid JSON array using double quotes. Example: "
                            "[{\"text\": \"...\", \"label\": \"...\"}]."
                        )
                    },
                    {"role": "user", "content": prompt}
                ]
            )

            raw = response.choices[0].message.content.strip()
            if "```" in raw:
                raw = raw.split("```")[1].strip()
                if raw.lower().startswith("json"):
                    raw = raw.split("\n", 1)[1]

            try:
                tagged = json.loads(raw)
            except Exception as e:
                st.error(f"⚠️ Couldn't parse JSON. Raw:\n\n{raw}\n\nError: {e}")
                st.stop()

            st.markdown('<div class="highlighted-output">', unsafe_allow_html=True)
            html = ""
            for item in tagged:
                text = item['text']
                label = item['label']
                color = colors.get(label, "#ddd")
                html += f'<span style="background-color:{color}; padding:2px 4px; border-radius:4px; margin:1px; color:white;">{text} </span>'
            st.markdown("### ✅ Highlighted Prompt")
            st.markdown(html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown("### 📌 Index")
    for label, color in colors.items():
        st.markdown(
            f'<div style="background-color:{color}; color:white; padding:8px; border-radius:4px; margin-bottom:8px;">{label}</div>',
            unsafe_allow_html=True
        )
