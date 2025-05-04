"""
Service layer for user-related operations.

Handles user creation, retrieval, email confirmation, and avatar URL updates.
Integrates with Gravatar to generate default avatars.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas import UserCreate

class UserService:
    """
    Provides user-related business logic and service methods.

    Delegates data persistence to the UserRepository and integrates external services like Gravatar.
    """
    def __init__(self, db: AsyncSession):
        """
        Initialize the UserService with a database session.

        Args:
            db (AsyncSession): SQLAlchemy asynchronous session.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Create a new user and generate a Gravatar avatar if available.

        Args:
            body (UserCreate): The data for the new user.

        Returns:
            User: The created user object.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Retrieve a user by their ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            User | None: The user object or None if not found.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Retrieve a user by their username.

        Args:
            username (str): The username to search.

        Returns:
            User | None: The user object or None if not found.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Retrieve a user by their email address.

        Args:
            email (str): The email address to search.

        Returns:
            User | None: The user object or None if not found.
        """
        return await self.repository.get_user_by_email(email)
    
    async def confirmed_email(self, email: str):
        """
        Confirm a user's email address.

        Args:
            email (str): The user's email address.

        Returns:
            None
        """
        return await self.repository.confirmed_email(email)
    
    async def update_avatar_url(self, email: str, url: str):
        """
        Update a user's avatar URL.

        Args:
            email (str): The user's email address.
            url (str): The new avatar URL.

        Returns:
            User: The updated user object.
        """
        return await self.repository.update_avatar_url(email, url)
