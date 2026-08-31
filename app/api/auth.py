"""A auth route for ...."""
from typing import Annotated

async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token: