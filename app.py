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
                random_user_id = random.randint(1, 10)
                # Check if the user has already seen and updated suggestions
                user_data = db.get(email)
                suggestions_seen = user_data.get('suggestions_seen', False)
                
                if not suggestions_seen:
                    recommendations = get_movie_recommendations(random_user_id, 20)
                    if user_data:
                        liked_movies = user_data.get('liked_movies', [])
                        for i in recommendations:
                            liked_movies.append(i)

                        # Update the liked movies in the user's data
                        user_data['liked_movies'] = liked_movies
                        user_data['suggestions_seen'] = True

                        # Put the updated user data back into the database
                        db.put(user_data)
                # let User see app
                st.sidebar.subheader(f'Welcome {username}')
                Authenticator.logout('Log Out', 'sidebar')


                # Movie selection component
                st.title('Movie Recommendation System')
                st.write('Welcome to the Movie Recommendation System. Click get new recommendations to see your movie suggestions')
                selected_movie = st.selectbox('Search Movies', movie_titles)
                st.subheader('These are your suggestions:')
                if user_data:
                    liked_movies = user_data.get('liked_movies', [])
                    if liked_movies:
                        liked_movies_text = '\n'.join(liked_movies)
                        st.text_area('', liked_movies_text, height=200)

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



                    # Get recommendations based on the remaining slots
                    recommendations = get_movie_recommendations(random_user_id, 3)
                    if user_data:
                        liked_movies = user_data.get('liked_movies', [])
                        for i in recommendations:
                            liked_movies.append(i)

                        # Update the liked movies in the user's data
                        user_data['liked_movies'] = liked_movies
                        # Put the updated user data back into the database
                        db.put(user_data)

                    # Pick 20 random movies from liked_movies (if there are at least 20 liked movies)
                    if len(liked_movies) >= 20:
                        random_liked_movies = random.sample(liked_movies, 20)
                    else:
                        random_liked_movies = liked_movies

                    # Combine liked movies and recommendations
                    updated_recommendations = random_liked_movies
                    
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
                sign_up()

except:
    st.success('Your network is a little slow, refresh page to continue')
