from pydantic import BaseModel


class GoogleConnectResponse(BaseModel):
    authorization_url: str
