from fastapi import FastAPI
from routers import posts, auth, likes

app = FastAPI()

app.include_router(posts.router)
app.include_router(auth.router)
app.include_router(likes.router)
