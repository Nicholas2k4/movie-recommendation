from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain_qdrant import QdrantVectorStore
from tqdm import tqdm
from collections import defaultdict
from operator import itemgetter
import pandas as pd
from operator import itemgetter
from typing import List, Union, Optional


def get_embedding():
    return HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")


def get_qdrant_client():
    return QdrantClient(
        url="https://5cabd8ea-7bcb-4d91-a725-f78349da9599.us-east4-0.gcp.cloud.qdrant.io:6333",
        api_key="EYc-fiqd65kJZt8AdSROtvEjgSpUV6jBotVkBAaj1-HInyC1FuaCiQ",
    )


def add_plots_to_qdrant(df):
    qdrant_client = get_qdrant_client()
    embeddings = get_embedding()

    qdrant_client.create_collection(
        collection_name="movies",
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    )
    vector_store = QdrantVectorStore(
        client=qdrant_client, collection_name="movies", embedding=embeddings
    )

    batch_size = 16
    for i in tqdm(range(0, len(df), batch_size), desc="Embedding and adding plots"):
        batch_df = df[i : i + batch_size]
        texts = batch_df["overview"].tolist()
        metadatas = batch_df[
            ["imdb_id", "title", "genres", "vote_average", "poster_url"]
        ].to_dict(orient="records")
        vector_store.add_texts(texts=texts, metadatas=metadatas)


def embed_plot(plot):
    embeddings = get_embedding()
    vec = embeddings.embed_query(plot)
    dim = len(vec)
    return vec, dim


def query_from_plot(
    plot: str,
    k: int = 10,
    genre: Optional[Union[str, List[str]]] = None,
    min_rating: Optional[float] = None,
):
    print(f"fn query_from_plot called = {plot}")
    qdrant_client = get_qdrant_client()
    embeddings = get_embedding()
    collection = "movies"

    query_vec = embeddings.embed_query(plot)

    total_points = qdrant_client.count(collection, exact=True).count
    res = qdrant_client.search(
        collection_name=collection,
        query_vector=query_vec,
        limit=total_points,
        with_payload=True,
        with_vectors=False,
    )

    results = []
    for pt in res:
        meta = pt.payload.get("metadata", {})
        genres = meta.get("genres") or []
        rating = meta.get("vote_average", 0.0)

        # ---------- filtering ----------
        if genre:
            want = set(genre) if isinstance(genre, (list, tuple, set)) else {genre}
            if not want.intersection(genres):
                continue
        if min_rating is not None and rating < min_rating:
            continue
        # --------------------------------------

        results.append(
            {
                "imdb_id": meta.get("imdb_id"),
                "title": meta.get("title"),
                "overview": pt.payload.get("page_content", ""),
                "genres": genres,
                "vote_average": rating,
                "poster_url": meta.get("poster_url"),
                "score": round(pt.score, 5),  
            }
        )

    # ── ambil top-k 
    top_k = sorted(results, key=itemgetter("score"), reverse=True)[:k]
    
    print(f"fn results = {top_k}")
    
    return top_k


def query_from_movies(
    movies_df,
    k: int = 10,
    genre: Optional[Union[str, List[str]]] = None,
    min_rating: Optional[float] = None,
):
    print(f"fn query_from_movies called = {movies_df}")

    qdrant_client = get_qdrant_client()
    embeddings = get_embedding()
    collection_name = "movies"

    total_points = qdrant_client.count(collection_name, exact=True).count
    seed_ids = set(str(x) for x in movies_df["imdb_id"])

    agg_score, agg_meta = defaultdict(float), {}

    for _, row in movies_df.iterrows():
        query_vec = embeddings.embed_query(row["overview"])

        res = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_vec,
            limit=total_points,
            with_payload=True,
            with_vectors=False,
        )

        for pt in res:
            meta = pt.payload.get("metadata", {})
            imdb_id = meta.get("imdb_id")
            genres = meta.get("genres") or []
            rating = meta.get("vote_average", 0.0)

            if imdb_id is None or imdb_id in seed_ids:
                continue

            # ---------- filtering ----------
            if genre:
                want = set(genre) if isinstance(genre, (list, tuple, set)) else {genre}
                if not want.intersection(genres):
                    continue
            if min_rating is not None and rating < min_rating:
                continue
            # --------------------------------------

            agg_score[imdb_id] += pt.score
            if imdb_id not in agg_meta:
                agg_meta[imdb_id] = {
                    "imdb_id": imdb_id,
                    "title": meta.get("title"),
                    "overview": pt.payload.get("page_content", ""),
                    "genres": genres,
                    "vote_average": rating,
                    "poster_url": meta.get("poster_url"),
                }

    ranked = sorted(agg_score.items(), key=itemgetter(1), reverse=True)[:k]
    movies = [{**agg_meta[iid], "score": round(score, 5)} for iid, score in ranked]
    
    print(f"fn results = {movies}")
    
    return movies


# print(embed_plot("test"))


# res = query_from_plot(
#     "survival on isolated island", k=10, genre="Animation", min_rating=7.0
# )
# for r in res:
#     print("=" * 80)
#     print(r["title"], r["imdb_id"], r["score"])  
#     genres = r["genres"]
#     for genre in genres:
#         print(genre, end=", ")
#     print()
#     print(r, "\n")


# df = pd.read_csv("data/movies_cleaned.csv")
# df = pd.read_csv("data/movies_cleaned.csv")
# df = df[df["title"].isin(["Iron Man 3", "Avengers: Age of Ultron"])]
# print(df)

# res = query_from_movies(df, k=30, min_rating=7)
# for r in res:
#     print("=" * 80)
#     print(r["title"], r["imdb_id"], r["score"])  
#     genres = r["genres"]
#     for genre in genres:
#         print(genre, end=", ")
#     print()
#     print(r, "\n")
