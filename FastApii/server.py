from fastapi import FastAPI

app=FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "World"}
@app.get("/contact-us")
def contact_us():
    return {"email": "Contact us at ayushd@gmail.com"}