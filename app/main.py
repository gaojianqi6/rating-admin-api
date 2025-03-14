from fastapi import FastAPI
from app.api.v1.endpoints import auth, users

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"ratingAdminAPIVersion": "0.0.1"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)