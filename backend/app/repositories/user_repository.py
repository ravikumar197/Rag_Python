from sqlalchemy.orm import Session

from app.models.user import User


def create_user(
    db: Session,
    user: User
):

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user(
    db: Session,
    user_id: int
):

    return db.get(User, user_id)


def update_user(
    db: Session,
    user: User
):

    db.commit()
    db.refresh(user)

    return user


def delete_user(
    db: Session,
    user: User
):

    db.delete(user)
    db.commit()

    return user