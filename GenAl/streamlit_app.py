import os
import re
from collections import Counter

import pandas as pd
import streamlit as st


def load_sample_report() -> str:
    sample_path = os.path.join("2_health_analysis", "blood_work.txt")
    if not os.path.exists(sample_path):
        return "Sample report not found."

    with open(sample_path, "r", encoding="utf-8") as f:
        return f.read()


def count_text(text: str) -> dict:
    words = re.findall(r"\w+", text.lower())
    char_count = len(text)
    word_count = len(words)
    sentence_count = len(re.findall(r"[.!?]+", text))
    top_words = Counter(words).most_common(8)
    return {
        "characters": char_count,
        "words": word_count,
        "sentences": sentence_count,
        "top_words": top_words,
    }


def highlight_abnormal_lines(report_text: str) -> list[str]:
    abnormalities = []
    normal_ranges = {
        "Total Cholesterol": (0, 200),
        "LDL Cholesterol": (0, 100),
        "HDL Cholesterol": (40, 999),
        "Triglycerides": (0, 150),
        "Hemoglobin": (13.5, 17.5),
        "Hematocrit": (41, 53),
        "WBC": (4.5, 11.0),
        "Platelets": (150, 400),
        "Glucose (Fasting)": (70, 99),
        "HbA1c": (0, 5.7),
        "Creatinine": (0.7, 1.3),
        "eGFR": (60, 999),
        "ALT": (7, 40),
        "AST": (10, 40),
        "Bilirubin Total": (0.2, 1.2),
    }

    for line in report_text.splitlines():
        for key, (low, high) in normal_ranges.items():
            if line.startswith(key):
                values = re.findall(r"[0-9.]+", line)
                if values:
                    try:
                        value = float(values[0])
                        if value < low or value > high:
                            abnormalities.append(line.strip())
                    except ValueError:
                        continue
    return abnormalities


def main() -> None:
    st.set_page_config(page_title="GenAl Streamlit Frontend", layout="wide")
    st.title("GenAl Streamlit Frontend")
    st.write(
        "This app demonstrates a simple Streamlit frontend for text analysis and sample health report review. "
        "Use the controls below to analyze your own text or review the included blood work report."
    )

    mode = st.sidebar.selectbox("Choose view", ["Text Analysis", "Health Report Sample"])

    if mode == "Text Analysis":
        st.header("Text Analysis")
        user_text = st.text_area("Enter text to analyze", height=240)

        if st.button("Analyze text"):
            if not user_text.strip():
                st.warning("Please enter some text to analyze.")
            else:
                stats = count_text(user_text)
                st.metric("Character count", stats["characters"])
                st.metric("Word count", stats["words"])
                st.metric("Sentence count", stats["sentences"])

                st.subheader("Top words")
                st.write(
                    pd.DataFrame(
                        stats["top_words"],
                        columns=["Word", "Count"],
                    )
                )

                st.subheader("Raw input")
                st.code(user_text)

    else:
        st.header("Health Report Sample")
        report_text = load_sample_report()
        st.subheader("Blood Work Report")
        st.code(report_text)

        abnormalities = highlight_abnormal_lines(report_text)
        if abnormalities:
            st.warning("Abnormal values detected in the sample report:")
            for line in abnormalities:
                st.write(f"- {line}")
        else:
            st.success("No abnormal values detected in the sample report by the configured checks.")

        st.markdown(
            "---\n"
            "**Note:** This sample analyzer performs basic number checks. "
            "It is intended as a UI demo rather than medical advice."
        )


if __name__ == "__main__":
    main()
