from pydantic import BaseModel


class BaseTemplate(BaseModel):
    id: str
    name: str
    createdAt: str
    createdBy: str
    description: str


class VersionContent(BaseModel):
    tag: str
    template: str
    engine: str
    mjml: str
    createdAt: str
    comment: str
    active: bool
    id: str


class FullTemplate(BaseTemplate):
    version: VersionContent
