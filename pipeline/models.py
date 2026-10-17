"""Pydantic models for what the pipeline reads (sources, stat and dataset specs) and writes (stats, datasets)."""
import re
from typing import Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Origin = Literal['government', 'court', 'team_or_league', 'independent']
Unit = Literal['usd_m', 'usd', 'pct', 'count', 'number', 'year']
SLUG = r'^[a-z0-9][a-z0-9-]*$'
DOC_DATE = r'^(\d{4}(-\d{2}(-\d{2})?)?|n\.d\.)$'
LABEL = r'^[abc](/[abc])*( ; [abc](/[abc])*)*$'


class Source(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: str = Field(pattern=SLUG)
    url: str = Field(pattern=r'^https?://')
    title: str = Field(min_length=3)
    title_from: Literal['ledger description', 'page title', 'url', 'curated']
    publisher: str = Field(min_length=2)
    origin: Origin
    date: str = Field(pattern=DOC_DATE)
    checked: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    review: Optional[str] = None


class Evidence(BaseModel):
    """Where a hand-entered stat value can be found in the data, so the build can confirm it."""
    model_config = ConfigDict(extra='forbid')
    file: str
    where: dict[str, str]
    column: str
    contains: str


class StatSpec(BaseModel):
    model_config = ConfigDict(extra='forbid')
    key: str = Field(pattern=r'^[a-z][a-z0-9_]*$')
    title: str
    unit: Unit
    basis: str = ''
    digits: Optional[int] = None
    label: Optional[str] = None
    label_sql: Optional[str] = None
    sql: Optional[str] = None
    value: Optional[float] = None
    evidence: Optional[Evidence] = None
    sources: list[str] = []
    sources_sql: Optional[str] = None
    check: Optional[str] = None  # SQL that must return true, for claims the copy makes about this number
    note: str = ''

    @model_validator(mode='after')
    def one_way(self):
        if (self.sql is None) == (self.value is None):
            raise ValueError(f'{self.key}: give exactly one of sql or value')
        if self.value is not None and self.evidence is None:
            raise ValueError(f'{self.key}: a hand-entered value needs evidence in the data')
        if not self.sources and not self.sources_sql:
            raise ValueError(f'{self.key}: no sources')
        if (self.label is None) == (self.label_sql is None):
            raise ValueError(f'{self.key}: give exactly one of label or label_sql')
        return self


class Stat(BaseModel):
    """A number the copy can use, with everything the fact-check ledger shows about it."""
    model_config = ConfigDict(extra='forbid')
    key: str
    title: str
    value: float
    unit: Unit
    basis: str
    digits: Optional[int]
    label: str = Field(pattern=LABEL)
    sources: list[str] = Field(min_length=1)
    display: dict[str, str]
    note: str
    method: str

    @field_validator('value')
    @classmethod
    def finite(cls, v):
        if v != v or v in (float('inf'), float('-inf')):
            raise ValueError('not a finite number')
        return v


class DatasetSpec(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: str = Field(pattern=SLUG)
    title: str
    sql: str
    sources: list[str] = []
    sources_sql: Optional[str] = None
    row_sources: Optional[str] = None  # name of a column holding each row's source ids
    require_row_sources: bool = False  # every row must cite at least one source of its own
    note: str = ''

    @model_validator(mode='after')
    def has_sources(self):
        if not self.sources and not self.sources_sql and not self.row_sources:
            raise ValueError(f'{self.id}: no sources')
        return self


class Dataset(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: str
    title: str
    sources: list[str] = Field(min_length=1)  # every source behind the rows
    base_sources: list[str] = Field(min_length=1)  # the dataset's own sources, without each row's
    columns: list[str]
    rows: list[dict[str, Union[str, int, float, bool, None, list]]]
    note: str
    method: str


def label_ok(label):
    return bool(re.fullmatch(LABEL, label))
