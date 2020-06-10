import datetime
from dataclasses import dataclass


@dataclass
class Payment:
    user_id: int
    creation_date: datetime.datetime
