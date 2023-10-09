import json
import logging
import cv2
from celery import Celery, Task
from engine.core.init_broker import is_broker_running
from engine.core.init_redis import is_backend_running

from engine.core import config
from engine.core.mq_main import redis

from engine.core.yolov8 import YOLOv8
from engine.core import config
from utils import helpers


if not is_backend_running(): exit()
if not is_broker_running(): exit()


app = Celery(config.QUERY_NAME, broker=config.BROKER, backend=config.REDIS_BACKEND)
app.config_from_object('settings.celery_config')


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
            self.model = YOLOv8(config.MODEL_PATH, conf_thres=config.SCORE_THRESHOLD, iou_thres=config.IOU_THRESHOLD)
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
        detection_boxes,detection_scores, detection_classes = self.model(image)
        det_new = []
        class_name_color = (0,255,0)
        box_color = (0,255,0)
        for j in range(len(detection_boxes)):
            box = detection_boxes[j]
            ymin, xmin, ymax, xmax = int(box[0]*height), int(box[1]*width), int(box[2]*height), int(box[3]*width)
            obj = {}
            obj['confidence_level'] = str(detection_scores[j])
            obj['box'] = ",".join([str(xmin), str(ymin), str(xmax), str(ymax)])
            # obj['class_name'] = category_index[detection_classes[j]]['name']
            det_new.append(obj)
            image_draw = cv2.rectangle(image_draw, (xmin, ymin), (xmax, ymax), box_color, 1)
            cv2.putText(image_draw, str(detection_classes[j]), (xmin+5, ymin+20), cv2.FONT_HERSHEY_SIMPLEX, 0.9, class_name_color, 2)
        # data['detection_draw_url'] = "http://{}:{}/api/v1/show-image/?path_image=".format(config.BE_HOST, config.BE_PORT) \
        #     + celery_config.ML_STORAGE_OBJECT_DETECTION_PATH + string_time + '/' + str(task_id) + celery_config.ML_IMAGE_TYPE
        # create_path(celery_config.ML_STORAGE_OBJECT_DETECTION_PATH + string_time)
        cv2.imwrite(config.ML_STORAGE_OBJECT_DETECTION_PATH + string_time + '/' + str(task_id) + config.ML_IMAGE_TYPE, image_draw)
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
        