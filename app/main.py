from fastapi import FastAPI

from app.core.exception_handlers import register_exception_handlers
from app.router import authentication

app = FastAPI(
    title="Google Integration API",
    description="This API integrates with Google services.",
    version="1.0.0",
)

register_exception_handlers(app)

app.include_router(authentication.router)
