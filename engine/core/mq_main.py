from redis import Redis
from engine.core import config


redis = Redis(
    host=config.REDIS['host'], 
    port=config.REDIS['port'], 
    password=config.REDIS['pass'],
    db= config.REDIS['db']
)