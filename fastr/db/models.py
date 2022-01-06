from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship


class UserBase(SQLModel):
    username: str


class UserCreate(UserBase):
    hashed_password: str


class UserLoggedIn(UserBase):
    id: int


class User(UserBase, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, sa_column_kwargs=dict(unique=True))
    hashed_password: str

    posts: List["Post"] = Relationship(back_populates="author")


class PostBase(SQLModel):
    title: str
    body: str


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    id: int


class Post(PostBase, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="user.id")
    created: datetime.datetime = Field(default_factory=datetime.datetime.now)

    author: User = Relationship(
        back_populates="posts", sa_relationship_kwargs=dict(lazy="joined")
    )
