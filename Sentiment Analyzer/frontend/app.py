import streamlit as st
import requests

# Page config
st.set_page_config(
    page_title="বাংলা সেন্টিমেন্ট অ্যানালাইজার",
    page_icon="💬",
    layout="centered"
)

# Simple styling
st.markdown("""
    <style>
        .main {
            padding-top: 2rem;
        }
        .stTextArea textarea {
            font-size: 18px;
        }
        .result-box {
            padding: 16px;
            border-radius: 12px;
            background-color: #f5f7fa;
            border: 1px solid #d9e2ec;
            margin-top: 10px;
        }
        .title-text {
            text-align: center;
            font-size: 36px;
            font-weight: 700;
            color: #1f2937;
        }
        .subtitle-text {
            text-align: center;
            font-size: 18px;
            color: #4b5563;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="title-text">💬 বাংলা সেন্টিমেন্ট অ্যানালাইজার</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle-text">আপনার বাংলা বাক্যের অনুভূতি বিশ্লেষণ করুন</div>',
    unsafe_allow_html=True
)

# Input
text_input = st.text_area(
    "আপনার বাক্য লিখুন:",
    placeholder="উদাহরণ: আজকের দিনটা আমার খুব ভালো কেটেছে।",
    height=150
)

# Optional examples
# st.markdown("**উদাহরণ:**")
# col1, col2, col3 = st.columns(3)

# with col1:
#     if st.button("😊 ইতিবাচক উদাহরণ"):
#         st.session_state["example_text"] = "আমি আজ খুব আনন্দিত এবং আত্মবিশ্বাসী অনুভব করছি।"

# with col2:
#     if st.button("😞 নেতিবাচক উদাহরণ"):
#         st.session_state["example_text"] = "আজ সারাদিন আমার খুব খারাপ লেগেছে।"

# with col3:
#     if st.button("😐 নিরপেক্ষ উদাহরণ"):
#         st.session_state["example_text"] = "আমি এখন বাসায় বসে একটি বই পড়ছি।"

# if "example_text" in st.session_state:
#     text_input = st.session_state["example_text"]
#     st.text_area("নির্বাচিত উদাহরণ:", value=text_input, height=100, disabled=True)

# Sentiment label mapping
def format_sentiment(sentiment: str) -> str:
    sentiment = sentiment.lower().strip()

    mapping = {
        "positive": "ইতিবাচক 😊",
        "negative": "নেতিবাচক 😞",
        "neutral": "নিরপেক্ষ 😐",
        "ইতিবাচক": "ইতিবাচক 😊",
        "নেতিবাচক": "নেতিবাচক 😞",
        "নিরপেক্ষ": "নিরপেক্ষ 😐"
    }

    return mapping.get(sentiment, f"{sentiment}")

# Analyze button
if st.button("বিশ্লেষণ করুন"):
    final_text = text_input.strip()

    if not final_text:
        st.warning("অনুগ্রহ করে একটি বাংলা বাক্য লিখুন।")
    else:
        with st.spinner("বিশ্লেষণ করা হচ্ছে..."):
            try:
                response = requests.post(
                    "http://localhost:8000/analyze/",
                    data={"text": final_text},
                    timeout=500
                )

                if response.status_code == 200:
                    sentiment = response.json().get("sentiment", "Error")
                    formatted_sentiment = format_sentiment(sentiment)

                    st.markdown("### বিশ্লেষণের ফলাফল")
                    st.markdown(
                        f'<div class="result-box"><strong>প্রেডিক্টেড সেন্টিমেন্ট:</strong> {formatted_sentiment}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.error("সার্ভার থেকে সঠিক রেসপন্স পাওয়া যায়নি।")

            except requests.exceptions.ConnectionError:
                st.error("ব্যাকএন্ড সার্ভারের সাথে সংযোগ করা যায়নি। নিশ্চিত করুন যে FastAPI সার্ভার চালু আছে।")
            except requests.exceptions.Timeout:
                st.error("রেসপন্স পেতে দেরি হচ্ছে। পরে আবার চেষ্টা করুন।")
            except Exception as e:
                st.error(f"একটি সমস্যা হয়েছে: {e}")