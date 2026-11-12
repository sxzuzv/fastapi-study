from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import posts, auth, users
  
app = FastAPI()

app.include_router(posts.router)
app.include_router(auth.router)
app.include_router(users.router)

app.mount('/media', StaticFiles(directory='media'), name='media')
app.mount('/static', StaticFiles(directory='static'), name='static')

@app.get('/')
def home():
  return {'hi': 'hello'}