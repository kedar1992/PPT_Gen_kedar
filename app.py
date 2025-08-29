import streamlit as st
import io
from ppt_builder import build_presentation
from template_style import analyze_template
from llm_providers import simple_heuristic_plan, plan_slides_with_llm

st.set_page_config(page_title="Want Help for creating your own PPT?", layout="wide")
st.title("Want Help for creating your own PPT?")

# UI
st.subheader("Step 1: Please enter text or markdown you have")
input_text = st.text_area("Enter text", height=200, placeholder="Paste your content here...")

st.subheader("Step 2: Upload a 1 Slider PowerPoint template (.pptx or .potx)")
uploaded_template = st.file_uploader("Upload template", type=["pptx", "potx"])

st.subheader("Optional: Use LLM for smarter slides")
provider = st.selectbox("LLM Provider", ["None (heuristic)", "OpenAI", "Anthropic", "Gemini"])
api_key = st.text_input("API Key (required if provider selected)", type="password")
guidance = st.text_input("Guidance (e.g., 'Investor pitch deck')", value="default")
add_notes = st.checkbox("Add speaker notes (LLM only)", value=False)

st.subheader("Step 3: Generate Presentation")
if st.button("Generate Deck"):
    if not input_text.strip():
        st.error("Please enter some text.")
    elif uploaded_template is None:
        st.error("Please upload a template file.")
    else:
        # Analyze template
        style_info = analyze_template(uploaded_template)

        # Plan slides
        if provider == "None (heuristic)":
            plan = simple_heuristic_plan(input_text, guidance, max_slides=8)
        else:
            if not api_key:
                st.error("Please enter your API key for the selected provider.")
                st.stop()
            plan = plan_slides_with_llm(provider, api_key, input_text, guidance, add_notes, model=None, max_slides=8)

        # Build presentation
        out_pptx = build_presentation(uploaded_template, plan, style_info)

        st.success(f"Presentation generated with {len(plan['slides'])} slides!")
        st.download_button(
            label="Download .pptx",
            data=out_pptx.getvalue(),
            file_name="generated_deck.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
