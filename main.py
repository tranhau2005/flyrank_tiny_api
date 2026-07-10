from fastapi import FastAPI 
app=FastAPI()

@app.get("/")
def main():
    return {"status":"Welcome to FastAPI"}
@app.get("/healthcheck")
def healthcheck():
    return {"healthcheck":"oke"}