import streamlit as st
import os
from openai import OpenAI

# === Custom CSS ===
st.markdown("""
    <style>
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
    }

    .checker-box {
        border-left: 8px solid #333;
        background-color: #f9f9f9;
        padding: 1em;
        margin-bottom: 1em;
        border-radius: 8px;
    }

    .role { border-left-color: #C70039; }
    .steps { border-left-color: #0B3C5D; }
    .pedagogy { border-left-color: #0099CC; }
    .constraints { border-left-color: #800080; }
    .personalization { border-left-color: #8B8000; }
    </style>
""", unsafe_allow_html=True)

# === OpenAI Setup ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="AI Coach Prompt Checker", page_icon="✅", layout="wide")

st.title("🎓 AI Coach Prompt Checker — Visual & Interactive")

st.markdown("""
**Paste your prompt below.**  
This tool analyzes it, shows which parts belong to **Role & Goal, Steps, Pedagogy, Constraints, Personalization**,  
and asks you clarifying questions if anything’s missing — just like a real coach.
""")

# === User Input ===
prompt = st.text_area("📋 Paste your prompt here:", height=300)

# === Session storage for clarifications ===
if "clarifications" not in st.session_state:
    st.session_state.clarifications = {}
if "parsed" not in st.session_state:
    st.session_state.parsed = {}

# === Analyze Button ===
if st.button("🔍 Analyze Prompt"):
    with st.spinner("Analyzing and parsing..."):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a prompt analyzer. Given a prompt, break it into 5 parts: "
                        "Role & Goal, Steps, Pedagogy, Constraints, Personalization. "
                        "If any part is missing or unclear, mark it as MISSING and generate a clarifying question."
                        "Return your answer in JSON format: "
                        "{ 'Role & Goal': '...', 'Steps': '...', 'Pedagogy': '...', "
                        "'Constraints': '...', 'Personalization': '...', 'Questions': { 'Role & Goal': '', ... } }"
                    )
                },
                {"role": "user", "content": prompt}
            ]
        )
        result = response.choices[0].message.content

    # --- Try to parse as JSON ---
    import json
    try:
        parsed = json.loads(result)
        st.session_state.parsed = parsed
    except:
        st.error("⚠️ Could not parse AI response as JSON. Check prompt format.")
        st.stop()

# === Display Parsed Parts ===
if st.session_state.parsed:
    parsed = st.session_state.parsed
    colors = {
        "Role & Goal": "role",
        "Steps": "steps",
        "Pedagogy": "pedagogy",
        "Constraints": "constraints",
        "Personalization": "personalization"
    }

    st.subheader("✅ **Highlighted Prompt Parts**")

    for section, css_class in colors.items():
        content = parsed.get(section, "")
        st.markdown(
            f'<div class="checker-box {css_class}">'
            f'<strong>{section}</strong><br>{content if content else "❌ MISSING!"}'
            f'</div>',
            unsafe_allow_html=True
        )

    # === Clarifying Questions ===
    st.subheader("❓ Clarify Missing Parts")
    for section, css_class in colors.items():
        content = parsed.get(section, "")
        question = parsed.get("Questions", {}).get(section, "")
        if "MISSING" in content.upper() and question:
            answer = st.text_input(f"{section}: {question}", key=section)
            st.session_state.clarifications[section] = answer

    # === Button to update prompt ===
    if any(st.session_state.clarifications.values()):
        if st.button("✅ Generate Improved Prompt"):
            clar_text = "\n".join([f"{k}: {v}" for k, v in st.session_state.clarifications.items() if v])
            new_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a prompt improver. "
                            "Rewrite the prompt using the original plus these clarifications to fill all 5 parts."
                        )
                    },
                    {"role": "user", "content": prompt + "\n\nClarifications:\n" + clar_text}
                ]
            )
            st.subheader("✨ **Improved Prompt:**")
            st.code(new_response.choices[0].message.content)

# === Bottom Explanation Boxes ===
st.markdown("---")
st.subheader("ℹ️ What Each Category Means")

info_boxes = {
    "Role & Goal": "Tells AI who it is, how it should behave, and what it should accomplish.",
    "Steps": "Clear step-by-step instructions for how AI should guide the user.",
    "Pedagogy": "How the AI supports learning, encourages thinking, and clarifies complex parts.",
    "Constraints": "What the AI must avoid doing, or limits on length, tone, or scope.",
    "Personalization": "How the AI summarizes results or tailors output to the user."
}

for section, desc in info_boxes.items():
    css_class = colors[section]
    st.markdown(
        f'<div class="checker-box {css_class}">'
        f'<strong>{section}</strong><br>{desc}'
        f'</div>',
        unsafe_allow_html=True
    )
