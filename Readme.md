# Movie Recommendation System (MR App)

## Description

The Movie Recommendation System (MR App) is a Streamlit-based application that provides personalized movie recommendations to users based on their preferences and interactions. This system uses machine learning to suggest movies tailored to individual users' tastes.

### Page Configuration

The application is titled "MR App" with a movie icon (📺) as the page icon. The initial sidebar is set to "collapsed" to provide a cleaner interface.

### Movie Selection

 Users can select movies from the dropdown menu labeled "Search Movies." This dropdown contains a list of movie titles.

### Suggestions

The selected movie's title, year, and genres (if available) are displayed once a movie is selected. Users can also see personalized movie suggestions under the "These are your suggestions:" section.

### Like Button

Users can click the "Like" button to add the selected movie to their recommended list.

### Get New Recommendations

Clicking the "Get New Recommendations" button generates new movie recommendations based on user interactions and previously liked movies.

### User Authentication

Users can log in with their credentials using the green "Login" button.
If not logged in or incorrect credentials are entered, users can sign up by providing a valid email, username, and password.
Sidebar: Once logged in, the sidebar displays a welcome message with the user's username and a "Log Out" button to sign out.

## How the App Works

### Data Loading

The app reads movie data from a CSV file (movies.csv) and preprocesses it. It also loads a machine learning model (twoTower.h5) for movie recommendations and the MovieLens 100K dataset for user ratings.

### User Authentication

The app uses streamlit-authenticator for user authentication. Users can log in with their credentials or sign up if they are new users.

### Movie Recommendations

Recommendations are based on user interactions and liked movies. The app recommends movies for the logged-in user and displays them.

### Data Storage

User data, including liked movies and suggestions seen, is stored in a database. The app retrieves and updates this data for each user.

### UI Updates

The app dynamically updates the user interface to display movie details, recommendations, and liked movies based on user interactions.

### Handling Errors

In case of slow network connectivity, the app provides a message instructing users to refresh the page to continue.

## Demo

You can check out a live demo of the MR App at [Demo Link](https://movie-recommendergit-ishwtvbe3vmi4z3jrpkfrl.streamlit.app/).

## Installation

To run the MR App on your local machine, follow these steps:

1. Navigate to the project directory.
2. Install the required dependencies using pip.
'''
pip install -r requirements.txt
'''

## Configuration

**Deta Credentials**

The Deta Base and Key credentials are required for user authentication and data storage. You can obtain these credentials by signing up for a Deta account and creating a new Base. Update the `DETA_KEY` variable in the `dependancies.py` file with your Deta Base key.

## Usage

To run the MR App, execute the following command in your terminal:

```bash
streamlit run app.py
You can then access the application at http://localhost:8501.
```

This will start the Streamlit application locally.
