import streamlit as st
import os
from openai import OpenAI
import json

# === Setup ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Color codes ===
colors = {
    "Role & Goal": "#C70039",
    "Steps": "#0B3C5D",
    "Pedagogy": "#0099CC",
    "Constraints": "#800080",
    "Personalization": "#8B8000"
}

pastel_colors = {
    "Role & Goal": "#f7c4c4",
    "Steps": "#c4d7f7",
    "Pedagogy": "#c4f1f7",
    "Constraints": "#e1c4f7",
    "Personalization": "#f1efc4"
}

# === Page config ===
st.set_page_config(page_title="AI Coach Inline Highlighter", page_icon="✅", layout="wide")
st.title("🔍 AI Coach Prompt Highlighter — Clean & Smart")

st.markdown("""
**Paste your raw prompt below.**  
When you click **Highlight Prompt**, the input will be replaced with a color-coded version, with recommendations for missing pieces.
""")

# === Custom CSS ===
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

# === Session states ===
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
                                "If the prompt is unclear or missing parts, still return a valid JSON array: "
                                "[{\"text\":\"Prompt unclear.\", \"label\":\"Uncategorized\"}]. "
                                "Always return only valid JSON with double quotes, no extra text."
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
        # === Show highlighted prompt ===
        st.markdown('<div class="highlighted-output">', unsafe_allow_html=True)
        html = ""
        for item in st.session_state.highlighted:
            text = item['text']
            label = item['label']
            color = colors.get(label, "#ddd")
            html += f'<span style="background-color:{color}; padding:2px 4px; border-radius:4px; margin:1px; color:white;">{text} </span>'
        st.markdown(html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # === Smart recommendations ===
        expected_labels = ["Role & Goal", "Steps", "Pedagogy", "Constraints", "Personalization"]
        found_labels = set(item['label'] for item in st.session_state.highlighted)
        missing_labels = [label for label in expected_labels if label not in found_labels]

        example_suggestions = {
            "Role & Goal": "Add a clear role, e.g. 'You are my trusted advisor for this project.'",
            "Steps": "Add step-by-step tasks, e.g. 'First, ask about my goals, then provide a plan.'",
            "Pedagogy": "Add a learning style, e.g. 'Explain in simple terms with examples.'",
            "Constraints": "Add limits, e.g. 'Do not use jargon or recommend paid tools.'",
            "Personalization": "Add a personal wrap-up, e.g. 'End with a summary tailored to my situation.'"
        }

        if missing_labels:
            st.markdown("### 🧩 **Recommendations to Improve This Prompt**")
            for label in missing_labels:
                color = colors.get(label, "#ccc")
                suggestion = example_suggestions.get(label, "Add more detail.")
                st.markdown(
                    f"""
                    <div style="border-left: 8px solid {color}; background-color: #f9f9f9; padding: 8px; margin-bottom: 8px; border-radius: 6px;">
                    <strong style="color:{color};">{label}</strong>: {suggestion}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.success("✅ All categories are well covered!")

        # === Reset button ===
        if st.button("🔄 Start Over"):
            st.session_state.show_highlight = False
            st.session_state.prompt_input = ""

    st.markdown('</div>', unsafe_allow_html=True)

# === Right: Color Index ===
with right:
    st.markdown("### 📌 Index")
    for label, color in colors.items():
        st.markdown(
            f'<div style="background-color:{color}; color:white; padding:8px; border-radius:4px; margin-bottom:8px;">{label}</div>',
            unsafe_allow_html=True
        )

# === Bottom Explanation Cards ===
st.markdown("---")
st.subheader("📚 What Each Category Means (with Examples)")

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
