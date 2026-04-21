from fastapi import APIRouter, status, HTTPException, Request

from app.schemas.v2.vlog import VlogYouTubeUploads
from app.api.dependencies import CurrentUser, DatabaseSession
from app.clients.redis import YouTubeUploadsCache
from app.repositories.v2.vloggers import VloggersRepository
from app.services.v2.vloggers import VloggersService
from app.core.exceptions import (
    VloggerDoesntExistError,
    VloggerUploadsError,
    YoutubeDataNotFoundError,
)

router = APIRouter(prefix="/vloggers", tags=["Vloggers"])


@router.get(
    "/youtube-uploads",
    response_model=VlogYouTubeUploads,
    status_code=status.HTTP_200_OK,
)
async def get_youtube_uploads(current_user: CurrentUser, db: DatabaseSession, request: Request):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    repository = VloggersRepository(db)
    cache = YouTubeUploadsCache(request.app.state.redis)
    service = VloggersService(repository, cache)

    try:
        youtube_uploads = await service.get_youtube_uploads(current_user.id)
    
    except VloggerDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Vlogger not found"
        )
    
    except VloggerUploadsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vlogger does not have uploads ID",
        )
    
    except YoutubeDataNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No Youtube Uploads found"
        )

    return youtube_uploads
