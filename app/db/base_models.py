from app.db.base import Base  # noqa F401

from app.models.language import Language  # noqa F401
from app.models.movie import Movie  # noqa F401
from app.models.actor import Actor  # noqa F401
from app.models.movie_actor import MovieActor  # noqa F401
from app.models.director import Director  # noqa F401
from app.models.movie_director import MovieDirector  # noqa F401
from app.models.genre import Genre  # noqa F401
from app.models.movie_genre import MovieGenre  # noqa F401
from app.models.media_asset import MediaAsset  # noqa F401
from app.models.user import User  # noqa F401
from app.models.rating import Rating  # noqa F401
from app.models.review import Review  # noqa F401
from app.models.favorite import Favorite  # noqa F401
from app.models.refresh_token import RefreshToken  # noqa F401
