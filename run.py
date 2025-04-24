import uvicorn

if __name__ == "__main__":
    print("Starting University Teaching Specialization Recommendation System...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 