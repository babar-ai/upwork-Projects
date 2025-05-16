import streamlit as st
import requests
from recomended import fetch_poster


# Define Streamlit UI
st.title("Movie Recommendation System")

movie_title = st.text_input("Enter a movie title:")

if st.button("Get Recommendations"):
    if movie_title:
        # Call FastAPI backend to get recommendations
        # print(movie_title)
        response = requests.post("http://127.0.0.1:8000/recommend", json={"title": movie_title})

        if response.status_code == 200:
            recommendations = response.json()["recommendations"]
            

        if recommendations:
            st.subheader("Top Recommendations 🎬")

            # Optional: Arrange posters nicely using columns
            cols = st.columns(3)  # Create 3 columns

            for idx, move in enumerate(recommendations):
                movie_title = move['title']
                poster_url = move['poster_url']

                if poster_url:
                    poster_url = poster_url.replace('w500//', 'w500/')  # Fix if needed
                    with cols[idx % 3]:  # Cycle through the 3 columns
                        st.image(poster_url, width=150)
                        st.caption(movie_title)
                else:
                    with cols[idx % 3]:
                        st.image('https://via.placeholder.com/150?text=No+Image', width=150)
                        st.caption(movie_title)
        else:
            st.warning("No recommendations found!")
    else:
        st.error(f"Failed to fetch recommendations. Status code")