from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from . import models


async def get_user_by_username(db: AsyncSession, username: str) -> models.User:
    result = await db.execute(
        select(models.User).where(models.User.username == username)
    )
    return result.scalars().first()


async def create_user(db: AsyncSession, user: models.UserCreate):
    db_user = models.User(username=user.username, hashed_password=user.hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)


async def get_posts(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[models.Post]:
    query = (
        select(models.Post)
        .order_by(models.Post.created.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


async def get_post_by_id(db: AsyncSession, id: int) -> models.Post:
    query = select(models.Post).where(models.Post.id == id)
    result = await db.execute(query)
    return result.scalars().first()


async def create_post(db: AsyncSession, create_data: models.PostCreate, user_id: int):
    post = models.Post(**create_data.dict(), author_id=user_id)
    db.add(post)
    await db.commit()
    await db.refresh(post)


async def update_post(db: AsyncSession, update_data: models.PostUpdate):
    post = await get_post_by_id(db, update_data.id)
    post.title = update_data.title
    post.body = update_data.body
    await db.commit()
    await db.refresh(post)


async def delete_post(db: AsyncSession, post_id: int):
    post = await get_post_by_id(db, post_id)
    await db.delete(post)
    await db.commit()
