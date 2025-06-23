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
st.title("🔍 AI Coach Prompt Highlighter — Inline with Index")

st.markdown("""
**Paste your raw prompt below.**  
This tool auto-highlights each phrase by category (Role & Goal, Steps, Pedagogy, Constraints, Personalization)  
and shows a color index for quick comparison.
""")

prompt = st.text_area("📋 Paste your prompt here:", height=300)

if st.button("✨ Highlight Prompt"):
    with st.spinner("Analyzing and tagging..."):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a prompt highlighter. Break any prompt into meaningful phrases or sentences. "
                        "For each, tag it as: Role & Goal, Steps, Pedagogy, Constraints, or Personalization. "
                        "Output ONLY valid JSON array using double quotes, no extra text or explanations. "
                        "Example: [{\"text\": \"...\", \"label\": \"...\"}]."
                    )
                },
                {"role": "user", "content": prompt}
            ]
        )

        raw = response.choices[0].message.content.strip()

        # Fallback: Extract JSON if wrapped in ```json
        if "```" in raw:
            raw = raw.split("```")[1].strip()
            if raw.lower().startswith("json"):
                raw = raw.split("\n", 1)[1]

        try:
            tagged = json.loads(raw)
        except Exception as e:
            st.error(f"⚠️ Couldn't parse AI JSON. Raw output:\n\n{raw}\n\nError: {e}")
            st.stop()

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
