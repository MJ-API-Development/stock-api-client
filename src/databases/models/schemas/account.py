from pydantic import BaseModel


class AccountBase(BaseModel):
    uuid: str
    first_name: str
    second_name: str
    surname: str
    email: str
    cell: str
    password_hash: str
    is_admin: bool
    is_deleted: bool


class AccountCreate(AccountBase):
    pass


class Account(AccountBase):
    class Config:
        orm_mode = True
