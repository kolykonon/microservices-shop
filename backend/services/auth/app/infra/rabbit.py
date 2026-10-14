from typing import Annotated

from fastapi import Depends
from starlette.requests import Request

from libs.rabbit import Rabbit


def get_rabbit(request: Request) -> Rabbit:
    return request.app.state.rabbit


RabbitDep = Annotated[Rabbit, Depends(get_rabbit)]
