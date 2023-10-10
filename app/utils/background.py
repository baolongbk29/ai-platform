import os
import datetime
import json
from fastapi import UploadFile
from app.models.engine import MlResult
from app.core.config import configs
from app.utils import helpers
from app.core.mq_main import redis, celery_execute


def image_upload_background(file: UploadFile, 
                           task_id: str, 
                           time: datetime,
                           data: MlResult):
    file_name = task_id + configs.ML_IMAGE_TYPE
    dir_path = configs.ML_STORAGE_UPLOAD_PATH + helpers.str_yyyy_mm_dd(time)    
    helpers.create_path(dir_path)
    file_path = os.path.join(dir_path, file_name)
    file_bytes = file.file.read()
    try:
        helpers.upload_file_bytes(file_bytes, file_path)
        # data.status['upload_id'] = task_id
        data.time['end_upload'] = str(helpers.now_utc().timestamp())
        data.status['upload_status'] = "SUCCESS"
        data.upload_result = {"path": file_path, "file_type": configs.ML_IMAGE_TYPE} 
        data_dump = json.dumps(data.__dict__)
        redis.set(task_id, data_dump)
        # print(config.ML_QUERY_NAME, config.ML_OBJECT_DETECTION_TASK)
        celery_execute.send_task(
            name="{}.{}".format(configs.ML_QUERY_NAME, configs.ML_OBJECT_DETECTION_TASK),
            kwargs={
                'task_id': task_id,
                'data': data_dump,
            },
            queue= configs.ML_QUERY_NAME
        )
    except Exception as e:
        data.status['upload_status'] = "FAILED"
        data.status['general_status'] = "FAILED"
        data.error = str(e)
        redis.set(task_id, json.dumps(data.__dict__))