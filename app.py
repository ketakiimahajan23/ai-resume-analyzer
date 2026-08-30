import os
import tempfile

import streamlit as st
from dotenv import load_dotenv

from extract_resume import extract_resume_text
from analyze_resume import analyze_resume


load_dotenv()


st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="centered"
)


st.title("📄 AI Resume Analyzer")

st.write(
    "Upload your resume and paste a job description. "
    "Gemini will score how well you match and give specific feedback."
)


uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"]
)

job_description = st.text_area(
    "Paste the job description here",
    height=250
)

analyze_clicked = st.button(
    "Analyze Resume",
    type="primary"
)


if analyze_clicked:

    if uploaded_file is None:
        st.error("Please upload a resume file first.")

    elif not job_description.strip():
        st.error("Please paste a job description first.")

    else:

        file_extension = os.path.splitext(uploaded_file.name)[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_extension
        ) as tmp_file:

            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        try:

            with st.spinner("Reading your resume..."):
                resume_text = extract_resume_text(tmp_path)

            with st.spinner(
                "Analyzing with Gemini... this may take a few seconds"
            ):
                result = analyze_resume(
                    resume_text,
                    job_description
                )

            if result is None:
                st.error(
                    "Something went wrong parsing the AI's response. "
                    "Please try again."
                )

            else:

                st.divider()

                score = result.get("match_score", 0)

                st.subheader(f"Match Score: {score}/100")

                st.progress(
                    min(max(score, 0), 100) / 100
                )

                st.write(
                    result.get("summary", "")
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.markdown("### ✅ Strengths")

                    for item in result.get("strengths", []):
                        st.markdown(f"- {item}")

                with col2:

                    st.markdown("### ⚠️ Gaps")

                    for item in result.get("gaps", []):
                        st.markdown(f"- {item}")

                st.markdown("### 💡 Suggestions")

                for item in result.get("suggestions", []):
                    st.markdown(f"- {item}")

        finally:
            os.remove(tmp_path)