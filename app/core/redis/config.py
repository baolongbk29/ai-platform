import os
from dotenv import load_dotenv
import aioredis
from rejson import Client


from app.core.config import configs 


class Redis:
    def __init__(self):
        """initialize  connection"""
        self.REDIS = configs.REDIS
        self.REDIS_HOST = self.REDIS["host"]
        self.REDIS_PORT = self.REDIS["port"]
        self.connection_url = "redis://:{password}@{hostname}:{port}".format(
                hostname=self.REDIS["host"],
                password=self.REDIS["pass"],
                port=self.REDIS["port"],
        )
        self.REDIS_BACKEND_CHAT = configs.REDIS_BACKEND_CHAT
    async def create_connection(self):
        self.connection = aioredis.from_url(self.REDIS_BACKEND_CHAT,db=self.REDIS['db_chat'])
        return self.connection

    def create_rejson_connection(self):
        self.redisJson = Client(
            host=self.REDIS["host"],
            port=self.REDIS["port"],
            decode_responses=True,
            # username=self.REDIS_USER,
            password=self.REDIS["pass"],
        )
        return self.redisJson