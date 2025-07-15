import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient
from sklearn.linear_model import LinearRegression
import os

# ----------------------------------
# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["Spotify_Lyrics"]
collection = db["Lyrics_data"]
# ----------------------------------

# Load sentiment documents
docs = list(collection.find({
    "sentiment_vader": {"$exists": True},
    "sentiment_textblob": {"$exists": True},
    "year": {"$exists": True}
}))

df = pd.DataFrame(docs)

st.title("🎧 Spotify Lyrics Sentiment Analysis (2019–2024)")

# Sidebar Filters
st.sidebar.header("🔍 Filter Options")
years = list(range(2019, 2025))
selected_years = st.sidebar.multiselect("Select years", years, default=years)

df = df[df["year"].isin(selected_years)]

# Song-level view
st.subheader("📄 Song-level Sentiment Scores")
if df.empty:
    st.warning("No data available for selected years.")
else:
    st.dataframe(df[["year", "title", "sentiment_vader", "sentiment_textblob"]].sort_values(by="year"))

    # Plot
    st.subheader("📊 Sentiment Distribution by Year")
    fig, ax = plt.subplots()
    ax.scatter(df["year"], df["sentiment_vader"], label="VADER", color="blue", alpha=0.6)
    ax.scatter(df["year"], df["sentiment_textblob"], label="TextBlob", color="orange", alpha=0.6)
    ax.set_xlabel("Year")
    ax.set_ylabel("Sentiment Score")
    ax.set_title("Sentiment Scores Per Song")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

# Yearly avg + regression prediction
if not df.empty:
    yearly_sentiment = df.groupby("year")[["sentiment_vader", "sentiment_textblob"]].mean().reset_index()
    
    # Regression
    X = yearly_sentiment["year"].values.reshape(-1, 1)
    y = yearly_sentiment["sentiment_vader"].values
    model = LinearRegression().fit(X, y)
    pred_2025 = model.predict(np.array([[2025]]))[0]

    st.subheader("📈 Yearly Avg Sentiment & 2025 Prediction")
    st.dataframe(yearly_sentiment)

    fig2, ax2 = plt.subplots()
    ax2.plot(yearly_sentiment["year"], yearly_sentiment["sentiment_vader"], marker="o", label="VADER Avg")
    ax2.scatter(2025, pred_2025, color="red", label=f"2025 Prediction: {pred_2025:.3f}")
    ax2.set_title("🎯 Average Yearly Sentiment Trend")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Sentiment Score")
    ax2.legend()
    ax2.grid(True)
    st.pyplot(fig2)

