import streamlit as st
import streamlit_authenticator as stauth
import datetime
import re
from deta import Deta
import tensorflow as tf
import numpy as np
import pandas as pd


DETA_KEY = 'a0vjrdeprjf_K1vvdkyUAcgKGW9gFETU9SALWjuaryjt'
deta = Deta(DETA_KEY)

db = deta.Base('streamlitauth')


def insert_user(email, username, password):
    """
    Inserts Users into the DB
    :param email:
    :param username:
    :param password:
    :return User Upon successful Creation:
    """
    date_joined = str(datetime.datetime.now())

    return db.put({'key': email, 'username': username, 'password': password, 'date_joined': date_joined})

def update_liked_movies(email, liked_movies):
    """
    Updates the liked movies for a user in the DB, preventing duplicates
    :param email: User's email
    :param liked_movies: A list of liked movie titles to add
    """
    user_data = db.get(email)
    if user_data:
        existing_liked_movies = set(user_data.get('liked_movies', []))
        new_liked_movies = list(set(liked_movies) - existing_liked_movies)
        if new_liked_movies:
            user_data['liked_movies'] = list(existing_liked_movies.union(new_liked_movies))
            db.put(user_data)



def fetch_users():
    """
    Fetch Users
    :return Dictionary of Users:
    """
    users = db.fetch()
    return users.items


def get_user_emails():
    """
    Fetch User Emails
    :return List of user emails:
    """
    users = db.fetch()
    emails = []
    for user in users.items:
        emails.append(user['key'])
    return emails


def get_usernames():
    """
    Fetch Usernames
    :return List of user usernames:
    """
    users = db.fetch()
    usernames = []
    for user in users.items:
        usernames.append(user['key'])
    return usernames


def validate_email(email):
    """
    Check Email Validity
    :param email:
    :return True if email is valid else False:
    """
    pattern = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"  # tesQQ12@gmail.com

    if re.match(pattern, email):
        return True
    return False


def validate_username(username):
    """
    Checks Validity of userName
    :param username:
    :return True if username is valid else False:
    """

    pattern = "^[a-zA-Z0-9]*$"
    if re.match(pattern, username):
        return True
    return False


def sign_up():
    with st.form(key='signup', clear_on_submit=True):
        st.subheader(':green[Sign Up]')
        email = st.text_input(':blue[Email]', placeholder='Enter Your Email')
        username = st.text_input(
            ':blue[Username]', placeholder='Enter Your Username')
        password1 = st.text_input(
            ':blue[Password]', placeholder='Enter Your Password', type='password')
        password2 = st.text_input(
            ':blue[Confirm Password]', placeholder='Confirm Your Password', type='password')

        if email:
            if validate_email(email):
                if email not in get_user_emails():
                    if validate_username(username):
                        if username not in get_usernames():
                            if len(username) >= 2:
                                if len(password1) >= 6:
                                    if password1 == password2:
                                        # Add User to DB
                                        hashed_password = stauth.Hasher(
                                            [password2]).generate()
                                        insert_user(email, username,
                                                    hashed_password[0])
                                        st.success(
                                            'Account created successfully!!')
                                        st.balloons()
                                    else:
                                        st.warning('Passwords Do Not Match')
                                else:
                                    st.warning('Password is too Short')
                            else:
                                st.warning('Username Too short')
                        else:
                            st.warning('Username Already Exists')

                    else:
                        st.warning('Invalid Username')
                else:
                    st.warning('Email Already exists!!')
            else:
                st.warning('Invalid Email')

        btn1, bt2, btn3, btn4, btn5 = st.columns(5)

        with btn3:
            st.form_submit_button('Sign Up')

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

# Function to get movie recommendations for a user
def get_movie_recommendations(user_id, n_recommendations=10):
    # Get movie embeddings for the given user
    user_embedding = model.get_layer('user_embedding')(np.array([user_id]))
    user_embedding = np.squeeze(user_embedding.numpy())

    # Calculate the similarity between user and all movies
    movie_embeddings = model.get_layer('movie_embedding').get_weights()[0]
    similarity_scores = np.dot(movie_embeddings, user_embedding)

    # Get movie ids with highest similarity scores (recommendations)
    movie_ids = np.argsort(similarity_scores)[::-1][:n_recommendations]

    # Get the movie titles based on movie ids
    recommended_movies = []
    for movie_id in movie_ids:
        movie_data = data[data['movieId'] == movie_id]
        if not movie_data.empty and not pd.isna(movie_data['title'].iloc[0]):
            recommended_movies.append(movie_data['title'].iloc[0])

    return recommended_movies
