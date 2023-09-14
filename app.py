import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
from dependancies import sign_up, fetch_users, get_movie_recommendations, update_liked_movies, db
import random
import tensorflow as tf
import numpy as np
from deta import Deta


st.set_page_config(page_title='Streamlit', page_icon='📺', initial_sidebar_state='collapsed')

# Read the CSV file
df = pd.read_csv('movies.csv')

# Extract movie titles with just title and year
movie_titles = []

for title in df['title']:
    if '(' in title and ')' in title:
        parts = title.split(' (', 1)
        movie_title = f"{parts[0]} ({parts[1].rstrip(')')})"
    else:
        movie_title = title
    movie_titles.append(movie_title)

# Create a dictionary to map movie titles to their genres
movie_genre_map = {title: genres.split('|') for title, genres in zip(df['title'], df['genres'])}
model = tf.keras.models.load_model('twoTower.h5')
# Load the MovieLens 100K dataset
ratings_data = pd.read_csv('ratings.csv')
movies_data = pd.read_csv('movies.csv')
# Data preprocessing for ratings dataset
ratings_data['userId'] = ratings_data['userId'].astype('category').cat.codes.values
ratings_data['movieId'] = ratings_data['movieId'].astype('category').cat.codes.values

# Merge ratings dataset with movies dataset on 'movieId'
data = pd.merge(ratings_data, movies_data[['movieId', 'title']], on='movieId', how='left')

# Data preprocessing
data['userId'] = data['userId'].astype('category').cat.codes.values
data['movieId'] = data['movieId'].astype('category').cat.codes.values
data.dropna(subset=['title'], inplace=True)

try:
    users = fetch_users()
    emails = []
    usernames = []
    passwords = []

    for user in users:
        emails.append(user['key'])
        usernames.append(user['username'])
        passwords.append(user['password'])

    credentials = {'usernames': {}}
    for index in range(len(emails)):
        credentials['usernames'][usernames[index]] = {'name': emails[index], 'password': passwords[index]}

    Authenticator = stauth.Authenticate(credentials, cookie_name='Streamlit', key='abcdef', cookie_expiry_days=4)

    email, authentication_status, username = Authenticator.login(':green[Login]', 'main')

    info, info1 = st.columns(2)

    if not authentication_status:
        sign_up()

    if username:
        if username in usernames:
            if authentication_status:
                # let User see app
                st.sidebar.subheader(f'Welcome {username}')
                Authenticator.logout('Log Out', 'sidebar')

                # Movie selection component
                st.title('Movie Recommendation System')
                st.write('Welcome to the Movie Recommendation System. Click get new recommendations to see your movie suggestions')
                selected_movie = st.selectbox('Search Movies', movie_titles)
                random_user_id = random.randint(1, 10)

                # Display selected movie title and year
                if selected_movie:
                    st.subheader('Selected Movie:')
                    st.write(selected_movie)

                    # Display genres for the selected movie
                    selected_movie_genres = movie_genre_map.get(selected_movie)
                    if selected_movie_genres:
                        st.write(", ".join(selected_movie_genres))
                    else:
                        st.warning('Genres information not available for this movie.')

                if st.button("Like"):
                    # Get the user's current liked movies
                    user_data = db.get(email)
                    if user_data:
                        liked_movies = user_data.get('liked_movies', [])
                        liked_movies.append(selected_movie)
                        update_liked_movies(email, liked_movies)
                        st.success(f"You've added '{selected_movie}' to your recommended list!")
                st.write('Like a movie to get better recommendations!')
                if st.button("Get New Recommendations"):
                    st.write(f"Recommended movies for {username}:")

                    # Get liked movies for the user
                    user_data = db.get(email)
                    liked_movies = user_data.get('liked_movies', [])

                    # Calculate the number of recommendations to fetch
                    max_recommendations = 10
                    num_liked_movies = len(liked_movies)
                    remainder = max(max_recommendations - num_liked_movies, 0)

                    # Get recommendations based on the remaining slots
                    recommendations = get_movie_recommendations(random_user_id, n_recommendations=remainder)

                    # Combine liked movies and recommendations
                    updated_recommendations = liked_movies + recommendations
                    
                    for i, movie in enumerate(updated_recommendations, 1):
                        st.write(f'{i}. {movie}')
                
                
            elif not authentication_status:
                with info:
                    st.error('Incorrect Password or username')
            else:
                with info:
                    st.warning('Please feed in your credentials')
        else:
            with info:
                st.warning('Username does not exist, Please Sign up')


except:
    st.success('Refresh Page')