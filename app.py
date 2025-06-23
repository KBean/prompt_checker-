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
When you click **Highlight Prompt**, the input will be replaced with your highlighted version — using categories:
Role & Goal, Steps, Pedagogy, Constraints, Personalization.
""")

# === Custom CSS for fixed width ===
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

# === Session state to store whether user clicked Highlight ===
if "show_highlight" not in st.session_state:
    st.session_state.show_highlight = False

# === Layout ===
left, right = st.columns([2, 1])

with left:
    st.markdown('<div class="prompt-container">', unsafe_allow_html=True)

    if not st.session_state.show_highlight:
        prompt = st.text_area(
            "📋 Paste your prompt here:",
            height=150,
            placeholder="e.g. Please help me write a PPT as a marketing leader",
            key="prompt_input"
        )

        if st.button("✨ Highlight Prompt"):
            with st.spinner("Analyzing..."):
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a prompt highlighter. Break any prompt into phrases or sentences. "
                                "Tag each with: Role & Goal, Steps, Pedagogy, Constraints, Personalization. "
                                "If the prompt is unclear, return: [{\"text\":\"Prompt unclear.\", \"label\":\"Uncategorized\"}]. "
                                "Always return only valid JSON array with double quotes."
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

                if not raw.startswith("[") or not raw.endswith("]"):
                    st.error(f"⚠️ The AI did not return valid JSON. Please refine your prompt.\n\nRaw output:\n\n{raw}")
                    st.stop()

                try:
                    tagged = json.loads(raw)
                except Exception as e:
                    st.error(f"⚠️ Couldn't parse JSON. Raw output:\n\n{raw}\n\nError: {e}")
                    st.stop()

                st.session_state.highlighted = tagged
                st.session_state.show_highlight = True

    else:
        # Show the highlighted version in place of input
        st.markdown('<div class="highlighted-output">', unsafe_allow_html=True)
        html = ""
        for item in st.session_state.highlighted:
            text = item['text']
            label = item['label']
            color = colors.get(label, "#ddd")
            html += f'<span style="background-color:{color}; padding:2px 4px; border-radius:4px; margin:1px; color:white;">{text} </span>'
        st.markdown(html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Optionally allow reset:
        if st.button("🔄 Start Over"):
            st.session_state.show_highlight = False
            st.session_state.prompt_input = ""

    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown("### 📌 Index")
    for label, color in colors.items():
        st.markdown(
            f'<div style="background-color:{color}; color:white; padding:8px; border-radius:4px; margin-bottom:8px;">{label}</div>',
            unsafe_allow_html=True
        )

# === Bottom Explanation Box with pastel and equal size ===
st.markdown("---")
st.subheader("📚 What Each Category Means (with Examples)")

pastel_colors = {
    "Role & Goal": "#f7c4c4",
    "Steps": "#c4d7f7",
    "Pedagogy": "#c4f1f7",
    "Constraints": "#e1c4f7",
    "Personalization": "#f1efc4"
}

box_style = """
    padding: 16px;
    border-radius: 8px;
    color: #000;
    width: 100%;
    height: 250px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow-wrap: break-word;
"""

col1, col2, col3, col4, col5 = st.columns(5)

col1.markdown(
    f"""
    <div style="background-color:{pastel_colors['Role & Goal']}; {box_style}">
    <strong>📂 Role & Goal</strong><br>
    📌 Example: "You are a friendly project coach who helps teams run a premortem."<br><br>
    <em>What it does:</em> Tells AI who it is, how to behave, and the main purpose.
    </div>
    """,
    unsafe_allow_html=True
)

col2.markdown(
    f"""
    <div style="background-color:{pastel_colors['Steps']}; {box_style}">
    <strong>📝 Step by Step</strong><br>
    📌 Example: "First, ask about their project. Next, guide them through risk points."<br><br>
    <em>What it does:</em> Guides AI through the task step-by-step.
    </div>
    """,
    unsafe_allow_html=True
)

col3.markdown(
    f"""
    <div style="background-color:{pastel_colors['Pedagogy']}; {box_style}">
    <strong>🎓 Pedagogy</strong><br>
    📌 Example: "Encourage reflection. Use simple explanations."<br><br>
    <em>What it does:</em> Gives teaching style or learning guidance.
    </div>
    """,
    unsafe_allow_html=True
)

col4.markdown(
    f"""
    <div style="background-color:{pastel_colors['Constraints']}; {box_style}">
    <strong>🚫 Constraints</strong><br>
    📌 Example: "Don't share project secrets. Avoid negativity."<br><br>
    <em>What it does:</em> Defines limits and what to avoid.
    </div>
    """,
    unsafe_allow_html=True
)

col5.markdown(
    f"""
    <div style="background-color:{pastel_colors['Personalization']}; {box_style}">
    <strong>🎁 Personalization</strong><br>
    📌 Example: "Summarize their plan and wish them good luck."<br><br>
    <em>What it does:</em> Tells AI how to wrap up with a personal touch.
    </div>
    """,
    unsafe_allow_html=True
)

