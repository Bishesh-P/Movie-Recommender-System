import pickle
import requests
import streamlit as st

# ---------- Page config ----------
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# ---------- Load data ----------
@st.cache_resource
def load_data():
    movies = pickle.load(open("movie_list.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    return movies, similarity

movies, similarity = load_data()

TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

# ---------- Poster fetch ----------
@st.cache_data
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except requests.exceptions.RequestException:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster"

# ---------- Recommend logic ----------
def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_titles = []
    recommended_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].id
        recommended_titles.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_titles, recommended_posters

# ---------- UI ----------
st.title("🎬 Movie Recommender System")
st.markdown("Pick a movie you like, and I'll suggest 5 similar ones.")

selected_movie = st.selectbox(
    "Search or select a movie",
    movies["title"].values
)

if st.button("Recommend", type="primary"):
    with st.spinner("Finding similar movies..."):
        names, posters = recommend(selected_movie)

    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            st.image(poster, use_container_width=True)
            st.markdown(f"**{name}**")