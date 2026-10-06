from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories import user_repository


def create_user(
    db: Session,
    user_data: UserCreate
):

    user = User(
        name=user_data.name,
        email=user_data.email
    )

    return user_repository.create_user(db, user)


def get_user(
    db: Session,
    user_id: int
):

    return user_repository.get_user(db, user_id)


def update_user(
    db: Session,
    user_id: int,
    user_data: UserUpdate
):

    user = user_repository.get_user(db, user_id)

    if user is None:
        return None

    user.name = user_data.name
    user.email = user_data.email

    return user_repository.update_user(db, user)


def delete_user(
    db: Session,
    user_id: int
):

    user = user_repository.get_user(db, user_id)

    if user is None:
        return None

    return user_repository.delete_user(db, user)