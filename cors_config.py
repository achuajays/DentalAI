from fastapi.middleware.cors import CORSMiddleware


def add_cors(app):
    """
    Add CORS middleware to a FastAPI application.

    Args:
        app: The FastAPI application instance to configure.

    Returns:
        None: Modifies the app in-place by adding CORS middleware.
    """
    # Define allowed origins
    # Use ["*"] for development to allow all origins; restrict in production
    origins = [
        "*"
    ]

    # Add CORS middleware to the app
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # List of allowed origins
        allow_credentials=True,  # Allow cookies and authentication headers
        allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
        allow_headers=["*"],  # Allow all headers
    )


if __name__ == "__main__":
    from fastapi import FastAPI

    # Standalone example for testing
    app = FastAPI(title="CORS Test API")

    # Apply CORS
    add_cors(app)


    @app.get("/test")
    async def test_endpoint():
        return {"message": "CORS is enabled!"}


    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7000)