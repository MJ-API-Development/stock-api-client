from pydantic import BaseModel
from src.databases.models.schemas.apikeys import ApiKeysBaseModel


class AccountModel(BaseModel):
    uuid: str
    first_name: str
    second_name: str
    surname: str
    email: str
    cell: str
    is_admin: bool = False
    is_deleted: bool = False


class AccountCreate(AccountModel):
    uuid: str | None
    password: str


class CompleteAccountResponseModel(AccountModel):

    apikeys: ApiKeysBaseModel


class AccountResponseSchema(BaseModel):
    status : bool
    payload : CompleteAccountResponseModel
    message : str

