import requests
import streamlit as st
import pickle
import pandas as pd
import os
from dotenv import load_dotenv
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# ---------------- Setup ---------------- #

# Load API key securely from .env file
load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

# Configure a requests session with retry logic
session = requests.Session()
retry_strategy = Retry(
    total=3,                # retry up to 3 times
    backoff_factor=1,       # wait 1s, then 2s, then 4s...
    status_forcelist=[500, 502, 503, 504],  # retry on these HTTP errors
    allowed_methods=["GET"] # only retry GET requests
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)  # enforce secure HTTPS only

# ---------------- Functions ---------------- #

def fetch_poster(movie_id):
    """Fetch movie poster from TMDb API using movie_id"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    try:
        response = session.get(url, timeout=5)  # use session with retry + timeout
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Poster+Available"
    except requests.exceptions.RequestException as e:
        st.warning(f"Poster fetch failed for movie_id {movie_id}: {e}")
        return "https://via.placeholder.com/500x750?text=Poster+Unavailable"

def recommend(movie_name):
    """Recommend top 5 similar movies with posters"""
    recommended_movies = []
    recommended_posters = []

    # find the movie index
    movie_index_df = movie[movie['title'] == movie_name]

    if movie_index_df.empty:
        st.write("Movie not found. Check spelling.")
        return [], []

    movie_index = movie_index_df.index[0]

    # calculate distances
    distances = similarity[movie_index]

    # get top 5 similar movies
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    # collect recommended movie titles and posters
    for i in movies_list:
        movie_id = movie.iloc[i[0]].movie_id   # ensure your dataset has 'movie_id'
        recommended_movies.append(movie.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters

# ---------------- Streamlit UI ---------------- #

# load data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movie = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title("🎬Movie Recommender System🥰")

selected_movie_name = st.selectbox(
    "Select the movie name for the recommendation:",
    movie['title'].values
)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)

    if names:
        st.write("Recommended Movies:")
        cols = st.columns(5)  # display 5 recommendations side by side
        for idx, col in enumerate(cols):
            with col:
                st.text(names[idx])
                st.image(posters[idx])

st.write("\n\n\n\n\n")
st.write("\n\n\n\n\n")
st.write("\n\n\n\n\n")

# Align your name to the right
st.markdown("<p style='text-align:right ;color:black; font-weight:bold;'> 🎥— Prabhat Kumar</p>", unsafe_allow_html=True)
