import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router

# Create FastAPI app
app = FastAPI(
    title="University Teaching Specialization Recommendation System",
    description="A system to match faculty members with courses they are best qualified to teach, and identify skill gaps",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api", tags=["faculty-course-matching"])

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    return {
        "message": "University Teaching Specialization Recommendation System API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 