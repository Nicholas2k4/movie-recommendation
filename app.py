# app.py
# ------------------------------------------------------------------
import os, json
import pandas as pd
from flask import Flask, render_template, request, jsonify, redirect, url_for
from utils.embed import query_from_plot, query_from_movies

app = Flask(__name__)

# ── load movie metadata once ──────────────────────────────────────
MOVIES_DF = pd.read_csv(os.path.join("data", "movies_cleaned.csv"))[
    ["imdb_id", "title", "genres", "vote_average", "poster_url", "overview"]
]


# ── PAGE ROUTES ───────────────────────────────────────────────────
@app.route("/")
def index():
    return redirect(url_for("page_plot"))


@app.route("/plot")
def page_plot():
    return render_template("plot.html")


@app.route("/movies")
def page_movies():
    return render_template("movies.html")


# ── API: search titles for Select2 ────────────────────────────────
@app.route("/api/search")
def search_movies():
    q = request.args.get("q", "").lower()
    mask = MOVIES_DF["title"].str.contains(q, case=False, na=False)
    result = MOVIES_DF[mask].head(20)
    return jsonify(
        {
            "results": [
                {"id": r.imdb_id, "text": r.title, "poster_url": r.poster_url}
                for r in result.itertuples()
            ]
        }
    )


# ── API: recommend by plot ────────────────────────────────────────
@app.route("/api/recommend/plot", methods=["POST"])
def recommend_plot():
    data = request.get_json()
    recs = query_from_plot(
        plot=data.get("plot", ""),
        k=int(data.get("k", 50)),
        genre=data.get("genre"),
        min_rating=data.get("min_rating"),
    )
    return jsonify(recs)


# ── API: recommend by selected movies ─────────────────────────────
@app.route("/api/recommend/movies", methods=["POST"])
def recommend_movies():
    data = request.get_json()
    ids = data.get("imdb_ids", [])
    seed = MOVIES_DF[MOVIES_DF["imdb_id"].isin(ids)]
    recs = query_from_movies(
        movies_df=seed,
        k=int(data.get("k", 50)),
        genre=data.get("genre"),
        min_rating=data.get("min_rating"),
    )
    return jsonify(recs)


# ── run ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
