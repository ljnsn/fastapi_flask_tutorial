from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from fastr.db.database import get_session
from fastr.db import crud, models


router = APIRouter(tags=["blog"])
templates = Jinja2Templates(directory=str("fastr/templates"))


# https://github.com/tiangolo/fastapi/issues/1039#issuecomment-591661667
class RequiresLoginException(Exception):
    """
    Used in conjunction with login_required to ensure user is logged in before
    accessing certain views.

    Workaround suggested in a GitHub comment here:
    https://github.com/tiangolo/fastapi/issues/1039#issuecomment-591661667
    """

    pass


def login_required(request: Request):
    """Ensure a user is logged in."""
    if not request.session.get("user"):
        raise RequiresLoginException


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: AsyncSession = Depends(get_session)):
    """Show all the posts, most recent first."""
    posts = await crud.get_posts(db)
    return templates.TemplateResponse(
        "blog/index.html", {"request": request, "posts": posts}
    )


@router.get(
    "/create", dependencies=[Depends(login_required)], response_class=HTMLResponse
)
async def create_page(request: Request):
    """Create post page."""
    return templates.TemplateResponse("blog/create.html", {"request": request})


@router.post(
    "/create", dependencies=[Depends(login_required)], response_class=HTMLResponse
)
async def create_post(
    request: Request,
    title: str = Form(...),
    body: str = Form(""),
    db: AsyncSession = Depends(get_session),
):
    """
    Create a new post for the current user.

    Note: title is specified as a required field, so FastAPI's input validation will
    make sure it is populated. No need for an explicit check that it is not None or "".
    """
    post = models.PostCreate(title=title, body=body)
    await crud.create_post(
        db=db, create_data=post, user_id=request.session["user"]["id"]
    )
    return RedirectResponse("/", status_code=302)


@router.get(
    "/{id}/update", dependencies=[Depends(login_required)], response_class=HTMLResponse
)
async def update_page(
    request: Request, id: int, db: AsyncSession = Depends(get_session)
):
    """Update post page."""
    post = await get_and_validate_post(id=id, db=db, request=request)
    return templates.TemplateResponse(
        "blog/update.html", {"request": request, "post": post}
    )


@router.post(
    "/{id}/update", dependencies=[Depends(login_required)], response_class=HTMLResponse
)
async def update_post(
    request: Request,
    id: int,
    title: str = Form(...),
    body: str = Form(""),
    db: AsyncSession = Depends(get_session),
):
    """
    Update an existing post that was created by the logged in user.

    Note: title is specified as a required field, so FastAPI's input validation will
    make sure it is populated. No need for an explicit check that it is not None or "".
    """
    await get_and_validate_post(id=id, db=db, request=request)

    update_data = models.PostUpdate(id=id, title=title, body=body)
    await crud.update_post(db, update_data)
    return RedirectResponse("/", status_code=302)


@router.post(
    "/{id}/delete", dependencies=[Depends(login_required)], response_class=HTMLResponse
)
async def delete_post(
    request: Request,
    id: int,
    db: AsyncSession = Depends(get_session),
):
    """Delete a post that was created by the logged in user."""
    await get_and_validate_post(id=id, db=db, request=request)
    await crud.delete_post(db, post_id=id)
    return RedirectResponse("/", status_code=302)


async def get_and_validate_post(
    id: int,
    db: AsyncSession,
    request: Request,
    check_author: bool = True,
) -> models.Post:
    """
    Retrieve a post by id. Validate that it exists and was created by the logged in
    user.

    Parameters
    ----------
    id
        id of post we were looking for
    db
        database from get_session
    request
        API request
    check_author
        require the current user to be the author

    Returns
    -------
    The post data

    Raises
    ------
    404
        if a post with the given id doesn't exist
    403
        if the current user isn't the author
    """
    post = await crud.get_post_by_id(db, id)
    if post is None:
        raise HTTPException(404, f"Post id {id} doesn't exist.")

    user = models.UserLoggedIn(**request.session.get("user", {}))
    if check_author and post.author_id != user.id:
        raise HTTPException(
            403,
            f"Post {id} was not posted by currently logged in user ({user.username}).",
        )

    return post
