from fastapi import FastAPI
from routers import posts, auth
  
app = FastAPI()

app.include_router(posts.router)
app.include_router(auth.router)

@app.get('/')
def home():
  return {'hi': 'hello'}