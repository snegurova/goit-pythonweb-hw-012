from fastapi import APIRouter, Depends, Request, UploadFile, File
from slowapi import Limiter
from slowapi.util import get_remote_address

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import User
from src.conf.config import settings
from src.services.auth import get_current_user
from src.services.users import UserService
from src.services.upload_file import UploadFileService

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)

@router.get("/me", response_model=User, description="No more than 10 requests per minute")
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Retrieve the currently authenticated user's information.

    This endpoint is rate-limited to 10 requests per minute.

    Args:
        request (Request): The HTTP request object used to extract the client IP for rate limiting.
        user (User): The currently authenticated user.

    Returns:
        User: The authenticated user's data.
    """
    return user

@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the avatar image URL for the authenticated user.

    The image is uploaded to a cloud service, and the returned URL is stored in the database.

    Args:
        file (UploadFile): The image file to be uploaded.
        user (User): The currently authenticated user.
        db (AsyncSession): The asynchronous database session.

    Returns:
        User: The updated user object with the new avatar URL.
    """
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
