from pydantic import BaseModel
from typing import Union

class CommonException(BaseModel):
    ExceptionText: Union[str, None]
    ExceptionType: Union[str, None]
    Success: bool
