import os
import json
import logging
import cv2
from celery import Celery, Task
from engine.core.init_broker import is_broker_running
from engine.core.init_redis import is_backend_running

from engine.core import config
from engine.core.mq_main import redis

from engine.core.yolov8 import YOLOv8, utils
from engine.core import config
from engine.utils import helpers


if not is_backend_running(): exit()
if not is_broker_running(): exit()


app = Celery(config.QUERY_NAME, broker=config.BROKER, backend=config.REDIS_BACKEND)
app.config_from_object('engine.core.config')


class PredictTask(Task):
    """
    Abstraction of Celery's Task class to support loading ML model.
    """
    abstract = True

    def __init__(self):
        super().__init__()
        self.model = None

    def __call__(self, *args, **kwargs):
        """
        Load model on first call (i.e. first task processed)
        Avoids the need to load model on each task request
        """
        if not self.model:
            logging.info('Loading Model...')
            self.model = YOLOv8.YOLOv8(config.MODEL_PATH, conf_thres=config.SCORE_THRESHOLD, iou_thres=config.IOU_THRESHOLD)
            logging.info('Model loaded')
        return self.run(*args, **kwargs)
    
@app.task(bind=True, 
          base=PredictTask,
          name="{query}.{task_name}".format(
              query=config.QUERY_NAME, 
              task_name=config.ML_OBJECT_DETECTION_TASK_NAME))
def object_detection_task(self, task_id: str, data: bytes):
    """_summary_: object_detection by efi d2 model

    Args:
        task_id (str): _description_
        data (bytes): _description_

    Returns:
        _type_: _description_
    """
    data = json.loads(data) # load session data
    time = helpers.now_utc()
    data['time']['start_detection'] = str(helpers.now_utc().timestamp())
    string_time = helpers.str_yyyy_mm_dd(time)
    try:
        image = helpers.read_image_from_path_to_numpy(data['upload_result']['path'])
        image_draw = image.copy()
        height, width = image.shape[0:2]
        # Detect Objects
        detection_boxes, detection_scores, detection_classes = self.model(image)
        # Draw detections
        combined_img = self.model.draw_detections(image)
        det_new = []
        for j in range(len(detection_boxes)):
            box = detection_boxes[j]
            ymin, xmin, ymax, xmax = int(box[0]*height), int(box[1]*width), int(box[2]*height), int(box[3]*width)
            obj = {}
            obj['confidence_level'] = str(detection_scores[j])
            obj['box'] = ",".join([str(xmin), str(ymin), str(xmax), str(ymax)])
            obj['class_name'] = utils.class_names[detection_classes[j]]
            det_new.append(obj)
        data['detection_draw_url'] = config.ML_STORAGE_RESULTS_PATH + string_time + '/' + str(task_id) + config.ML_IMAGE_TYPE
        helpers.create_path(os.path.join(config.ML_STORAGE_RESULTS_PATH + string_time))
        cv2.imwrite(config.ML_STORAGE_RESULTS_PATH + string_time + '/' + str(task_id) + config.ML_IMAGE_TYPE, cv2.cvtColor(combined_img, cv2.COLOR_RGB2BGR))
        data['time']['end_detection'] = str(helpers.now_utc().timestamp())
        data['status']['detection_status'] = "SUCCESS"
        if len(det_new) > 0:
            data['detection_result'] = det_new
        data['status']['general_status'] = "SUCCESS"
        data_dump = json.dumps(data)
        redis.set(task_id, data_dump) 
    except Exception as e:
        data['time']['end_detection'] = str(helpers.now_utc().timestamp())
        data['status']['detection_status'] = "FAILED"
        data['status']['general_status'] = "FAILED"
        data['error'] = str(e)
        data_dump = json.dumps(data)
        redis.set(task_id, data_dump)
        