from pydantic import BaseModel, Field, HttpUrl


class GithubValidateRequest(BaseModel):
    repo_url: HttpUrl


class GithubValidateResponse(BaseModel):
    id: str
    repo_url: HttpUrl
    owner: str
    repo: str
    languages: list[str]
    validation: dict
