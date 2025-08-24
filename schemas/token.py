from schemas.base import BaseSchema

# Token schemas
class Token(BaseSchema):
    access_token: str
    token_type: str
