from typing import Annotated
from fastapi import Cookie


PocketAccessTokenDep = Annotated[str | None, Cookie(name="access_token")]
