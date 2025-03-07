import streamlit as st
import pandas as pd
import pickle
import requests
import time

# Load optimized dataset
df = pd.read_csv("optimized_netflix_titles.csv")  # Use your reduced dataset file
movie_titles = sorted(df['title'].dropna().unique())

# Load similarity matrix
with open("optimized_netflix_rec.pkl", "rb") as f:  # Ensure this matches the reduced dataset
    cosine_sim = pickle.load(f)


# Function to get movie recommendations
def get_recommendations(title, df, cosine_sim):
    if title not in df['title'].values:
        return pd.DataFrame()  # Return empty DataFrame if title not found

    idx_list = df[df['title'] == title].index.tolist()
    if not idx_list:
        return pd.DataFrame()  # No index found, return empty DataFrame

    idx = idx_list[0]  # Get the first valid index

    # Ensure idx is within range of cosine_sim
    if idx >= len(cosine_sim):
        return pd.DataFrame()

    # Get similarity scores
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:6]

    # Filter out-of-range indices
    movie_indices = [i[0] for i in sim_scores if i[0] < len(df)]

    return df.iloc[movie_indices] if movie_indices else pd.DataFrame()


# Function to fetch movie posters from TMDB API
def get_movie_poster(title):
    api_key = "ca967cd4b94896a1d94026d518f56827"  # Replace with your TMDb API key
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={title}"

    try:
        time.sleep(0.5)  # Prevents API rate limiting
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raises error if response is bad

        data = response.json()
        if data.get("results"):
            poster_path = data["results"][0].get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"

    except requests.exceptions.RequestException as e:
        print(f"Error fetching poster for {title}: {e}")

    return None


# Streamlit UI
st.title("Netflix Recommendations")

selected_movie = st.selectbox("Pick your Poison:", movie_titles)

if st.button("Get Recommendations"):
    recommendations = get_recommendations(selected_movie, df, cosine_sim)

    if recommendations.empty:
        st.write("No recommendations found.")
    else:
        st.write("Recommended Poison:")
        cols = st.columns(5)  # Display posters in 5 columns

        for i, (index, row) in enumerate(recommendations.iterrows()):
            poster_url = get_movie_poster(row['title'])
            if poster_url:
                cols[i].image(poster_url, caption=row['title'], use_container_width=True)
            else:
                cols[i].write(row['title'])
