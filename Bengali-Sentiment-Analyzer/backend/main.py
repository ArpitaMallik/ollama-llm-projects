from fastapi import FastAPI, Form
import requests

app = FastAPI()

def rule_based_override(text, model_sentiment):
    t = text.strip()

    negative_patterns = [
        "না", "নাই", "হয়নি", "করেনি",
        "ভালো না", "ভালো লাগছে না",
        "খারাপ লাগছে", "মেজাজ ভালো না",
        "দুঃখ", "কষ্ট", "হতাশ", "রাগ"
    ]

    positive_patterns = [
        "খুব ভালো", "অনেক ভালো", "খুশি",
        "আনন্দ", "ভালো লাগছে", "সন্তুষ্ট"
    ]

    # If strong negative signal → override
    if any(p in t for p in negative_patterns):
        return "নেতিবাচক"

    # If strong positive signal → override
    if any(p in t for p in positive_patterns):
        return "ইতিবাচক"

    return model_sentiment



@app.post("/analyze/")


def analyze_sentiment(text: str = Form(...)):
    prompt = f"""
তুমি একটি বাংলা sentiment classifier।

কাজ:
একটি বাক্যের sentiment ঠিক করে শুধু এই ৩টির মধ্যে ১টি লেবেল দেবে:
- ইতিবাচক
- নেতিবাচক
- নিরপেক্ষ

নিয়ম:
1. তথ্যভিত্তিক প্রশ্ন, সাধারণ জিজ্ঞাসা, চিকিৎসা/শিক্ষা/তথ্য জানার প্রশ্ন => নিরপেক্ষ
2. শুধু কোনো রোগ, সমস্যা, কষ্ট, ব্যথা, ভয়, হতাশা, রাগ, অভিযোগ, দুঃখের স্পষ্ট আবেগ থাকলে => নেতিবাচক
3. আনন্দ, ভালো লাগা, স্বস্তি, সন্তুষ্টি, প্রশংসা, আশাবাদ থাকলে => ইতিবাচক
4. শুধু বিষয়ের নাম দেখে sentiment দেবে না
5. কোনো ব্যাখ্যা দেবে না
6. শুধু একটি শব্দ লিখবে

উদাহরণ:
বাক্য: আমার মেজাজ ভালো লাগছে না।
উত্তর: নেতিবাচক

বাক্য: সে পরীক্ষায় ভালো করেনি।
উত্তর: নেতিবাচক

বাক্য: আজ আমার খুব ভালো লাগছে।
উত্তর: ইতিবাচক

বাক্য: {text}
উত্তর:
""".strip()

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "sailor2:1b",  
            "prompt": prompt,
            "stream": False
        }
    )

    result = response.json()
    raw_output = result.get("response", "").strip()

    #Normalize output (very important because LLMs can be messy)
    # Normalize output
    if "ইতিবাচক" in raw_output:
        sentiment = "ইতিবাচক"
    elif "নেতিবাচক" in raw_output:
        sentiment = "নেতিবাচক"
    elif "নিরপেক্ষ" in raw_output:
        sentiment = "নিরপেক্ষ"
    else:
        sentiment = "নিরপেক্ষ"

    # 🔥 Apply rule fix
    sentiment = rule_based_override(text, sentiment)

    return {"sentiment": sentiment}