from pydantic import BaseModel, validator
from src.databases.models.schemas.apikeys import ApiKeysBaseModel

from pydantic import BaseModel, root_validator


class AccountModel(BaseModel):
    uuid: str
    first_name: str | None
    second_name: str | None
    surname: str | None
    email: str
    cell: str | None
    is_admin: bool = False
    is_deleted: bool = False

    class Config:
        title = "Account Base Model"

    @classmethod
    @root_validator(pre=True)
    def split_name(cls, values):
        name = values.get('name', None)
        if name is not None:
            parts = name.strip().split(' ')
            if len(parts) == 1:
                values['first_name'] = parts[0]
                values['second_name'] = ''
                values['surname'] = ''
            elif len(parts) == 2:
                values['first_name'] = parts[0]
                values['second_name'] = ''
                values['surname'] = parts[1]
            elif len(parts) == 3:
                values['first_name'] = parts[0]
                values['second_name'] = parts[1]
                values['surname'] = parts[2]
            else:
                raise ValueError('Invalid name format')
        return values


class AccountCreate(AccountModel):
    uuid: str | None
    password: str

    class Config:
        title = "Create Account Model"


class CompleteAccountResponseModel(AccountModel):
    apikeys: ApiKeysBaseModel

    class Config:
        title = "Account Response Model"


class AccountResponseSchema(BaseModel):
    status: bool
    payload: CompleteAccountResponseModel
    message: str

    class Config:
        title = "Account Response Model"