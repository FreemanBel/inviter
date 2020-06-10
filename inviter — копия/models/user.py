import datetime
from dataclasses import dataclass


@dataclass
class User:
    user_id: int
    jointime: datetime.datetime
    kicktime: datetime.datetime
    access_demo : int
