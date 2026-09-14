from pydantic import BaseModel


class SearchResult(BaseModel):
    type: str
    label: str
    description: str
    url: str
