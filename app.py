import streamlit as st
import pandas as pd
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sentiment Analyzer", layout="wide")

@st.cache_resource
def load_sentiment_tool():
    return SentimentIntensityAnalyzer()

sentiment_tool = load_sentiment_tool()

st.title("Sentiment Analyzer")
st.caption("Understand how your words feel — individually or across entire datasets.")

examples = [
    "I love this product!",
    "This is the worst experience ever.",
    "It's okay, nothing special.",
    "The service was fine but could be better.",
    "I'm so disappointed right now.",
    "Today was a good day."
]

choice = st.sidebar.radio("Try an example:", options=examples)
if "text_input" not in st.session_state:
    st.session_state.text_input = choice
if st.sidebar.button("Use this"):
    st.session_state.text_input = choice

st.subheader("Try It Out With Manual Text")
text_input = st.text_area("Write something here to analyze its sentiment instantly:", value=st.session_state.get("text_input", ""))

def get_feeling(sentence):
    if not isinstance(sentence, str) or not sentence.strip():
        return pd.Series(["Neutral", 0.0, "neutral"])
    sentence = sentence.strip()
    score_1 = sentiment_tool.polarity_scores(sentence)["compound"]
    score_2 = TextBlob(sentence).sentiment.polarity
    score = (score_1 + score_2) / 2
    if score >= 0.6:
        feeling = "Extremely Positive"
        label = "positive"
    elif score >= 0.3:
        feeling = "Very Positive"
        label = "positive"
    elif score >= 0.1:
        feeling = "Slightly Positive"
        label = "positive"
    elif score <= -0.6:
        feeling = "Extremely Negative"
        label = "negative"
    elif score <= -0.3:
        feeling = "Very Negative"
        label = "negative"
    elif score <= -0.1:
        feeling = "Slightly Negative"
        label = "negative"
    else:
        feeling = "Neutral"
        label = "neutral"
    return pd.Series([feeling, score, label])

if text_input:
    feeling, score, tone = get_feeling(text_input)
    st.markdown("###  Sentiment Analysis Result")
    st.write(f"**Mood:** {feeling}")
    st.write(f"**Score:** {score:.3f}")
    st.write(f"**Sentiment Type:** {tone.capitalize()}")

st.subheader("Bulk Analysis With Your Own Dataset")

data_file = st.file_uploader("Upload a CSV or JSON file with text entries", type=["csv", "json"])

if data_file:
    try:
        if data_file.name.endswith('.csv'):
            records = pd.read_csv(data_file)
        else:
            records = pd.read_json(data_file)

        st.success("File uploaded successfully!")
        st.write("Here’s a quick look at your data:", records.head())

        text_column = st.selectbox("Pick the column that has the text to analyze:", records.columns)

        records[text_column] = records[text_column].astype(str).fillna("").apply(str.strip)
        records = records[records[text_column].str.len() > 3]

        if st.button("Run Sentiment Analysis"):
            with st.spinner("Reading emotions..."):
                records[["Mood", "Sentiment_Score", "Sentiment_Class"]] = records[text_column].apply(get_feeling)

                st.success("Done! Here's what we found:")

                st.subheader("Overall Feelings")
                summary = records["Sentiment_Class"].value_counts()
                st.bar_chart(summary)

                st.metric(" Most Common Mood", summary.idxmax().capitalize())
                st.metric("Average Score", f"{records['Sentiment_Score'].mean():.3f}")

                st.subheader(" A Sample of the Results")
                st.dataframe(records[[text_column, "Mood", "Sentiment_Score", "Sentiment_Class"]].head(10))

                st.subheader("Save Your Results")
                download = records.to_csv(index=False).encode("utf-8")
                st.download_button("Download as CSV", download, "sentiment_results.csv", "text/csv")

    except Exception as e:
        st.error(f"Something went wrong while processing your file: {e}")
