import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify, render_template


# Load MovieLens Dataset
try:
    ratings = pd.read_csv(
        "ml-100k/u.data",
        sep="\t",
        names=["user_id", "movie_id", "rating", "timestamp"]
    )
    movies = pd.read_csv(
        "ml-100k/u.item",
        sep="|",
        encoding="latin-1",
        usecols=[0, 1],
        names=["movie_id", "title"]
    )
except FileNotFoundError:
    print("Dataset files not found. Please make sure the 'ml-100k' folder is in the same directory.")
    exit()

# Create User-Movie Matrix
user_movie_matrix = ratings.pivot_table(
    index="user_id",
    columns="movie_id",
    values="rating"
).fillna(0)

# Calculate Movie Similarity
movie_similarity = cosine_similarity(user_movie_matrix.T)
movie_similarity_df = pd.DataFrame(
    movie_similarity,
    index=user_movie_matrix.columns,
    columns=user_movie_matrix.columns
)

print("✅ Data loaded and model prepared successfully!")

# RECOMMENDATION FUNCTION

def recommend(movie_name, top_n=5):
    try:
        
        movie_id = movies[movies["title"] == movie_name].iloc[0]["movie_id"]
    except IndexError:
        return ["Movie not found. Please check the spelling or try another movie from the list."]

    
    scores = movie_similarity_df[movie_id].sort_values(ascending=False)
    
    
    top_movie_ids = scores.iloc[1:top_n+1].index
    
    return movies[movies["movie_id"].isin(top_movie_ids)]["title"].tolist()


app = Flask(__name__)

@app.route("/")
def home():
    
    movie_titles = movies['title'].tolist()
    return render_template("index.html", movie_titles=movie_titles)

@app.route("/recommend", methods=["GET"])
def recommend_api():
    movie = request.args.get("movie")
    try:
        
        top_n = int(request.args.get("top_n", 5))
    except (ValueError, TypeError):
        top_n = 5
        
    if not movie:
        return jsonify({"error": "Movie title not provided"}), 400
        
    recs = recommend(movie, top_n=top_n)
    return jsonify({"recommendations": recs})

if __name__ == "__main__":
    app.run(debug=True)