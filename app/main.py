from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

import app.models
from app.core.config import settings
from app.exceptions.base import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError
from app.routers.actor import admin as actor_admin
from app.routers.actor import admin_movie_actor
from app.routers.actor import public as actor_public
from app.routers.director import admin as director_admin
from app.routers.director import admin_movie_director
from app.routers.director import public as director_public
from app.routers.favorite import public as favorite_public
from app.routers.genre import admin as genre_admin
from app.routers.genre import admin_movie_genre
from app.routers.genre import public as genre_public
from app.routers.language import admin as language_admin
from app.routers.language import public as language_public
from app.routers.media_asset import admin as admin_media_asset
from app.routers.movie import admin as movie_admin
from app.routers.movie import public as movie_public
from app.routers.rating import public as rating_public
from app.routers.review import admin as review_admin
from app.routers.review import public as review_public
from app.routers.user import admin as user_admin
from app.routers.user import auth
from app.routers.user import public as user_public

is_production = settings.ENVIRONMENT.lower() == "production"
app = FastAPI(
    title="Movie API",
    version="1.0.0",
    description="Movie REST API",
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json",
)
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=bool(settings.CORS_ORIGINS),
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(user_public.router)
app.include_router(user_admin.router)
app.include_router(language_public.router)
app.include_router(language_admin.router)
app.include_router(movie_public.router)
app.include_router(movie_admin.router)
app.include_router(genre_public.router)
app.include_router(genre_admin.router)
app.include_router(director_admin.router)
app.include_router(director_public.router)
app.include_router(actor_admin.router)
app.include_router(actor_public.router)
app.include_router(admin_movie_genre.router)
app.include_router(admin_movie_director.router)
app.include_router(admin_movie_actor.router)
app.include_router(admin_media_asset.router)
app.include_router(rating_public.router)
app.include_router(favorite_public.router)
app.include_router(review_public.router)
app.include_router(review_admin.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@app.exception_handler(NotFoundError)
def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(ForbiddenError)
def forbidden_handler(request: Request, exc: ForbiddenError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(UnauthorizedError)
def unauthorized_handler(request: Request, exc: UnauthorizedError):
    return JSONResponse(status_code=401, content={"detail": str(exc)})
