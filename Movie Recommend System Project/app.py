from fastapi import FastAPI
from pydantic import BaseModel
from recomended import improved_recommend

app = FastAPI()

class MovieRequest(BaseModel):
    title: str


@app.get("/")
def Home():
    return {"message": "Welcome to Movie Recommendation System"}

@app.post("/recommend")
def recommend_movie(request: MovieRequest):
    result = improved_recommend(request.title)
    recommendations = [{"title": title, "poster_url": poster} for title, poster in result]
    return {"recommendations": recommendations}


