from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, sa_column_kwargs=dict(unique=True))
    hashed_password: str

    posts: List["Post"] = Relationship(back_populates="author")


class Post(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="user.id")
    created: datetime = Field(default=datetime.now())
    title: str
    body: str

    author: User = Relationship(
        back_populates="posts", sa_relationship_kwargs=dict(lazy="joined")
    )
