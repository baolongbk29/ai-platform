from datetime import datetime
from pydantic import BaseModel
import uuid


class Message(BaseModel):
    id = str(uuid.uuid4())
    msg: str
    timestamp = str(datetime.now())