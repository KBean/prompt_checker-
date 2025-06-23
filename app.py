import streamlit as st
from openai import OpenAI

# === Setup your OpenAI key ===
client = OpenAI()

st.set_page_config(page_title="Prompt Checker", page_icon="✅")

st.title("🔍 AI Coach Prompt Checker")

st.markdown("""
Paste your AI prompt below.  
This tool will check for:
- **Role & Goal**
- **Step-by-Step Instructions**
- **Pedagogy**
- **Constraints**
- **Personalization**
""")

prompt_input = st.text_area("✏️ Paste your prompt here:", height=300)

if st.button("Check Prompt"):
    with st.spinner("Analyzing your prompt..."):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a prompt quality checker. "
                        "For any prompt, check if it has these 5 sections: "
                        "1) Role & Goal 2) Step-by-Step Instructions "
                        "3) Pedagogy 4) Constraints 5) Personalization. "
                        "Give a checklist ✅ or ❌ and for each ❌, suggest a fix. "
                        "Then give an overall improvement suggestion."
                    )
                },
                {"role": "user", "content": prompt_input}
            ]
        )
        result = response.choices[0].message.content
        st.markdown("### ✅ **Result:**")
        st.markdown(result)
