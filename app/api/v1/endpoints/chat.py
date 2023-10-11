import os
import uuid
from rejson import Path
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    WebSocket,
    WebSocketDisconnect,
    Request,
)
from app.core.dependency import get_current_user_payload
from app.core.socket.connection import ConnectionManager
from app.core.redis.config import Redis
from app.core.redis.producer import Producer
from app.core.redis.stream import StreamConsumer
from app.core.redis.cache import Cache
from app.core.socket.utils import get_token
from app.models.chat import Chat


router = APIRouter(
    prefix="/chat",
    tags=['Chat']
)
manager = ConnectionManager()
redis = Redis()

@router.post("/token",)
async def token(
    *,
    user: str = Depends(get_current_user_payload),
    ):
    # if name=="":
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Invalib input name"
    #     )

    token = str(uuid.uuid4())

    # Create nee chat session
    json_client = redis.create_rejson_connection()
    
    chat_session = Chat(
        token=token,
        messages=[],
        name=user.nickname
    )

    print(chat_session.dict())

    # Store chat session in redis JSON with the token as key
    json_client.jsonset(str(token), Path.rootPath(), chat_session.dict())

    # Set a timeout for redis data
    redis_client = await redis.create_connection()
    await redis_client.expire(str(token), 3600)

    return chat_session.dict()


@router.get("/refresh_token")
async def refresh_token(request: Request, token: str):
    json_client = redis.create_rejson_connection()
    cache = Cache(json_client)
    data = await cache.get_chat_history(token)

    if data == None:
        raise HTTPException(
            status_code=400, detail="Session expired or does not exist")
    else:
        return data



@router.websocket("/process")
async def websocket_endpoint(websocket: WebSocket, token: str = Depends(get_token)):
    await manager.connect(websocket)
    redis_client = await redis.create_connection()
    producer = Producer(redis_client)
    json_client = redis.create_rejson_connection()
    consumer = StreamConsumer(redis_client)

    try:
        while True:
            data = await websocket.receive_text()
            stream_data = {}
            stream_data[str(token)] = str(data)
            await producer.add_to_stream(stream_data, "message_channel")
            response = await consumer.consume_stream(stream_channel="response_channel", block=0)

            print(response)
            for stream, messages in response:
                for message in messages:
                    response_token = [k.decode('utf-8')
                                      for k, v in message[1].items()][0]

                    if token == response_token:
                        response_message = [v.decode('utf-8')
                                            for k, v in message[1].items()][0]

                        print(message[0].decode('utf-8'))
                        print(token)
                        print(response_token)

                        await manager.send_personal_message(response_message, websocket)

                    await consumer.delete_message(stream_channel="response_channel", message_id=message[0].decode('utf-8'))

    except WebSocketDisconnect:
        manager.disconnect(websocket)