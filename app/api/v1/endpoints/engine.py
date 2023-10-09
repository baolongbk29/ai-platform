# -----------------------------------------------------------
# API paragraph and field detection for ancestry document
# (C) 2021 Duy Nguyen, Ho Chi Minh, Viet Nam
# email duynguyenngoc@hotmail.com
# -----------------------------------------------------------

from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException, Depends,status
import uuid
import json
from app.core.mq_main import redis
# from securities import token as token_helper
from app.utils import helpers
from app.core.config import configs
from app.models.engine import MlTimeHandle, MlResult, MlStatusHandle, MlResponse
from app.utils.background import image_upload_background


router = APIRouter(    
    prefix="/engine",
    tags=["engine"],
)


@router.post("/process")
async def ml_process(
    *,
    # current_user = Depends(token_helper.get_current_user),
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks
):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="file_type not support!")
    time = helpers.now_utc()
    task_id = str(uuid.uuid5(uuid.NAMESPACE_OID, configs.ML_QUERY_NAME + "_"+ str(time)))
    time_handle = MlTimeHandle(start_upload=str(time.timestamp())).__dict__
    status_hanlde = MlStatusHandle().__dict__
    data = MlResult(task_id=task_id, time=time_handle, status=status_hanlde)
    redis.set(task_id, json.dumps(data.__dict__))
    background_tasks.add_task(image_upload_background, file, task_id, time, data)
    return MlResponse(status="PENDING", time=time, status_code=status.HTTP_200_OK, task_id=task_id)


@router.get("/status/{task_id}", response_model=MlResult)
def ml_status(
    *,
    task_id: str,
    # current_user = Depends(token_helper.get_current_user),
):
    data = redis.get(task_id)
    if data == None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='task id not found!')
    message = json.loads(data)
    return message