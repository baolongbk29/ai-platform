from fastapi import (
    APIRouter,
    UploadFile,
    File,
    BackgroundTasks,
    HTTPException,
    Depends,
    status,
)
import uuid
import json
from app.core.mq_main import redis
from app.utils import helpers
from app.core.config import configs
from app.models.engine import MlTimeHandle, MlResult, MlStatusHandle, MlResponse
from app.utils.background import image_upload_background
from app.core.dependency import get_current_active_user_token

router = APIRouter(
    prefix="/engine",
    tags=["Engine"],
)


@router.post(
    "/process",
)
async def engine_process(
    *,
    # current_user = Depends(token_helper.get_current_user),
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks,
    user_token: str = Depends(get_current_active_user_token),
):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="file_type not support!"
        )
    time = helpers.now_utc()
    task_id = str(
        uuid.uuid5(uuid.NAMESPACE_OID, configs.ML_QUERY_NAME + "_" + str(time))
    )
    time_handle = MlTimeHandle(start_upload=str(time.timestamp())).__dict__
    status_hanlde = MlStatusHandle().__dict__
    data = MlResult(task_id=task_id, time=time_handle, status=status_hanlde)
    redis.set(task_id, json.dumps(data.__dict__))
    background_tasks.add_task(image_upload_background, file, task_id, time, data)
    return MlResponse(
        status="PENDING", time=time, status_code=status.HTTP_200_OK, task_id=task_id
    )


@router.get("/status/{task_id}", response_model=MlResult)
def engine_status(
    *,
    task_id: str,
    user_token: str = Depends(get_current_active_user_token),
):
    data = redis.get(task_id)
    if data == None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="task id not found!"
        )
    message = json.loads(data)
    return message
