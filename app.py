# === Custom CSS ===
st.markdown("""
    <style>
    /* Make headings prettier */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
    }

    /* Style for color-coded boxes */
    .checker-box {
        border-left: 8px solid #333;
        background-color: #f9f9f9;
        padding: 1em;
        margin-bottom: 1em;
        border-radius: 8px;
    }

    /* Color overrides (adjust per your palette) */
    .role { border-left-color: #C70039; }         /* Red */
    .steps { border-left-color: #0B3C5D; }        /* Dark Blue */
    .pedagogy { border-left-color: #0099CC; }     /* Light Blue */
    .constraints { border-left-color: #800080; }  /* Purple */
    .personalization { border-left-color: #8B8000; } /* Olive */
    </style>
""", unsafe_allow_html=True)


import streamlit as st
import os
from openai import OpenAI

# Setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="AI Coach Prompt Checker", page_icon="✅", layout="wide")

st.title("🎓 AI Coach Prompt Checker — Visual Version")

st.markdown("""
Paste your prompt below. This tool checks it for:
**Role & Goal, Step-by-Step Instructions, Pedagogy, Constraints, Personalization.**

Then it shows a color-coded breakdown + improvement tips.
""")

# === Layout ===
prompt = st.text_area("📋 Paste your prompt here:", height=300)

if st.button("🔍 Check Prompt"):
    with st.spinner("Analyzing..."):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a prompt quality checker. For any prompt, do 3 tasks:\n"
                        "1) For each of Role & Goal, Steps, Pedagogy, Constraints, Personalization — mark ✅ or ❌.\n"
                        "2) For each ❌, suggest a clear 1-2 line fix.\n"
                        "3) Give an overall quick improvement suggestion."
                    )
                },
                {"role": "user", "content": prompt}
            ]
        )
        result = response.choices[0].message.content

    # === Split output ===
    st.subheader("✅ **Checklist & Suggestions**")
    st.markdown("---")

    # Color-coded display using HTML/CSS
    colors = {
        "Role & Goal": "#C70039",
        "Steps": "#0B3C5D",
        "Pedagogy": "#0099CC",
        "Constraints": "#800080",
        "Personalization": "#8B8000"
    }

    # Simple fallback parse: assume response is structured as:
    # Checklist:
    # ✅ Role & Goal
    # ❌ Steps ...
    # Suggestion: ....

    for section, color in colors.items():
        found = f"✅ {section}" in result
        mark = "✅" if found else "❌"
        st.markdown(
            f"""
            <div style="
                border-left: 8px solid {color};
                background-color: #f9f9f9;
                padding: 0.8em;
                margin-bottom: 0.5em;
            ">
            <strong style="color:{color}; font-size: 1.1em;">{section}</strong>: <span style="font-size: 1.2em;">{mark}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Show raw suggestions below
    st.subheader("📌 Full AI Suggestions")
    st.info(result)
