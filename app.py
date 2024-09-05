import streamlit as st
import pickle
import requests
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


# fetch fun to fetch the poster from tmdb
def fetch_poster(movie_id):
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    try:
        response = session.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=304a703e9457bc856d8ce58d74f9b057',
            timeout=10)
        response.raise_for_status()
        data = response.json()
        return "https://image.tmdb.org/t/p/w500/" + data.get('poster_path', '')
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {e}")
        return None

#main function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        poster_url = fetch_poster(movie_id)
        if poster_url:
            recommended_movies_posters.append(poster_url)
        time.sleep(0.5)

    return recommended_movies, recommended_movies_posters


movies = pickle.load(open('movies.pkl', 'rb'))
movies_list = movies['title'].values
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title('Movie Recommender System')
selected_movie_name = st.selectbox(
    "Select a movie to get recommendations:",
    movies_list
)

#making button
if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)

    num_recommendations = len(names)

    if num_recommendations > 0:
        cols = st.columns(num_recommendations)
        for i in range(num_recommendations):
            with cols[i]:
                st.text(names[i])
                if i < len(posters):
                    st.image(posters[i])
                else:
                    st.text("Poster not available")
    else:
        st.warning("No recommendations found.")
