import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time
import random

# Initialize VADER
analyzer = SentimentIntensityAnalyzer()

# App UI Setup
st.set_page_config(
    page_title="🚀 Sentiment Analyzer",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS with animation styles
st.markdown("""
<style>
    .positive { color: #2ecc71; font-size: 24px; font-weight: bold; }
    .negative { color: #e74c3c; font-size: 24px; font-weight: bold; }
    .neutral { color: #95a5a6; font-size: 24px; font-weight: bold; }
    .header { font-size: 32px !important; color: #3498db; }

    /* Neutral animation */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
        100% { transform: translateY(0px); }
    }
    .neutral-emoji {
        animation: float 3s ease-in-out infinite;
        display: inline-block;
    }

    /* Analyze button styling */
    .stButton>button {
        width: 100%;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'input_text' not in st.session_state:
    st.session_state.input_text = ""
if 'analyze_clicked' not in st.session_state:
    st.session_state.analyze_clicked = False

# Header with animated title
st.markdown('<p class="header">🚀 Sentiment Analyzer <span style="font-size:24px"></span></p>',
            unsafe_allow_html=True)
st.write("Type text and press Enter or click Analyze")


# Sentiment analysis function
def analyze(text):
    sentiment = analyzer.polarity_scores(text)
    compound_score = sentiment['compound']

    if compound_score >= 0.05:
        return "😊 Positive", compound_score, "positive"
    elif compound_score <= -0.05:
        return "😠 Negative", compound_score, "negative"
    else:
        return "😐 Neutral", compound_score, "neutral"


# Custom animation functions
def show_neutral_animation():
    """Floating emojis for neutral sentiment"""
    cols = st.columns(5)
    emojis = ["🌫️", "🌀", "🌪️", "💭", "☁️"]
    for col, emoji in zip(cols, emojis):
        with col:
            st.markdown(f'<div class="neutral-emoji" style="font-size: 30px; text-align: center;">{emoji}</div>',
                        unsafe_allow_html=True)


# Create analysis form
with st.form(key='analysis_form'):
    user_input = st.text_area(
        "**Enter your text here:**",
        height=150,
        key="text_input",
        value=st.session_state.input_text,
        placeholder="Type something like 'I feel okay today'..."
    )

    # Analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.form_submit_button("🔍 Analyze", use_container_width=True)

# Sample texts in sidebar
st.sidebar.markdown("### Try these examples:")
sample_texts = [
    "I'm not feeling great",
    "This is absolutely terrible",
    "It's okay, I guess",
    "I love this! Amazing work!",
    "Meh, not bad but not great either"
]

# Handle example selection
example_clicked = None
for text in sample_texts:
    if st.sidebar.button(text, key=f"btn_{text[:10]}"):
        example_clicked = text

# Update session state if example was clicked
if example_clicked:
    st.session_state.input_text = example_clicked
    st.session_state.analyze_clicked = True
    st.rerun()

# Perform analysis
if analyze_button or st.session_state.analyze_clicked:
    st.session_state.analyze_clicked = False

    if user_input:
        with st.spinner('Analyzing sentiment...'):
            time.sleep(0.8)  # Slightly longer for anticipation
            result, score, sentiment_class = analyze(user_input)

            # Display results
            st.markdown(f"### Sentiment: <span class='{sentiment_class}'>{result}</span>",
                        unsafe_allow_html=True)
            st.write(f"**Sentiment score:** `{score:.3f}` (Range: -1.0 to +1.0)")

            # Progress bar
            normalized_score = (score + 1) / 2
            st.progress(normalized_score)

            # Show appropriate animation
            if sentiment_class == "positive":
                st.balloons()
            elif sentiment_class == "negative":
                st.snow()
            else:
                show_neutral_animation()

            # Additional emoji reaction
            reaction_placeholder = st.empty()
            if sentiment_class == "positive":
                reaction_placeholder.success("✨ Great vibes detected!")
            elif sentiment_class == "negative":
                reaction_placeholder.error("💢 Negative emotions noted")
            else:
                reaction_placeholder.info("🌫️ Neutral mood observed")