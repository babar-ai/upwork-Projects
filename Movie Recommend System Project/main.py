# #The crew column typically contains information about the people involved in the production of the movie other than the cast. This includes directors, writers, producers, cinematographers, etc.
# #The cast column typically contains information about the actors and actresses who appear in the movie.

import pandas as pd
import ast 
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def convert_cast(text):
    try:
        cast_list = []
        count = 0
        for i in ast.literal_eval(text):
            if count < 5:  # Top 5 actors
                cast_list.append(i['name'])
                count += 1
        return cast_list
    except:
        return []

def convert_crew(obj):
    try:
        crew_list = []
        for i in ast.literal_eval(obj):
            if i['job'] in ['Director', 'Writer', 'Producer']:
                crew_list.append(i['name'])
        return crew_list
    except:
        return []

def convert_features(text):
    try:
        return [i['name'] for i in ast.literal_eval(text)]
    except:
        return []

# Load and merge datasets
credits = pd.read_csv(r"F:\Machine Learning Hub\Machine Learning Projects\Movie Recommend System Project\TMDB 5000 Movie Dataset\tmdb_5000_credits.csv")
movies = pd.read_csv(r"F:\Machine Learning Hub\Machine Learning Projects\Movie Recommend System Project\TMDB 5000 Movie Dataset\tmdb_5000_movies.csv")

movies = movies.merge(credits, on='title')

# Select relevant features
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]

# Clean the data
movies.dropna(inplace=True)
movies.drop_duplicates(inplace=True)

# Convert each feature
movies['cast'] = movies['cast'].apply(convert_cast)
movies['crew'] = movies['crew'].apply(convert_crew)
movies['genres'] = movies['genres'].apply(convert_features)
movies['keywords'] = movies['keywords'].apply(convert_features)

# Create separate strings for features
movies['cast_string'] = movies['cast'].apply(lambda x: ' '.join([name.lower().replace(' ', '') for name in x])) #terminating spaces bt names and convert into list
movies['crew_string'] = movies['crew'].apply(lambda x: ' '.join([name.lower().replace(' ', '') for name in x]))
movies['genres_string'] = movies['genres'].apply(lambda x: ' '.join([name.lower().replace(' ', '') for name in x]))
movies['keywords_string'] = movies['keywords'].apply(lambda x: ' '.join([name.lower().replace(' ', '') for name in x]))

# Create soup with weighted features (using repetition instead of multiplication)
#Without spaces, words would run together and be treated as one big word
movies['soup'] = (
    movies['overview'].str.lower() + ' ' +
    movies['genres_string'] + ' ' + movies['genres_string'] + ' ' +  # Double weight for genres
    movies['keywords_string'] + ' ' +
    movies['cast_string'] + ' ' + movies['cast_string'] + ' ' +  # Double weight for cast
    movies['crew_string'] + ' ' + movies['crew_string']  # Double weight for crew
)

# Create count matrix and compute cosine similarity
count = CountVectorizer(stop_words='english', max_features=5000)            #max_features parameter specifies the maximum number of unique words (or features) to include in the resulting vocabulary.
count_matrix = count.fit_transform(movies['soup'])
similarity = cosine_similarity(count_matrix, count_matrix)

def improved_recommend(title, similarity=similarity):
    try:
        idx = movies[movies['title'] == title].index[0]
        sim_scores = list(enumerate(similarity[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:6]
        movie_indices = [i[0] for i in sim_scores]
        recommendations = movies['title'].iloc[movie_indices]
        return recommendations
    except:
        return "Movie not found in the database."

# Example usage
print("Recommendations for 'Avatar':")
print(improved_recommend('Spider-Man 3'))




