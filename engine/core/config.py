import configparser
import datetime
import pytz 
from kombu import Queue

cfg = configparser.ConfigParser()
cfg.read(r'E:\BaoLong\ecommerce-platform\engine\engine_enviroment.ini')


#=========================================================================
#                           TIMING CONFIG
#=========================================================================
u = datetime.datetime.utcnow()
u = u.replace(tzinfo=pytz.timezone("Asia/Ho_Chi_Minh"))

#=========================================================================
#                          PROJECT INFORMATION 
#=========================================================================
PROJECT = cfg['project']
BE_HOST = PROJECT['be_host']
BE_PORT = PROJECT['be_port']

#=========================================================================
#                          REDIS INFORMATION 
#=========================================================================
REDIS = cfg['redis']
REDIS_BACKEND = "redis://:{password}@{hostname}:{port}/{db}".format(
    hostname=REDIS['host'],
    password=REDIS['pass'],
    port=REDIS['port'],
    db=REDIS['db']
)

#=========================================================================
#                          BROKER INFORMATION 
#=========================================================================
RABBITMQ = cfg['rabbitmq']
BROKER = "amqp://{user}:{pw}@{hostname}:{port}/{vhost}".format(
    user=RABBITMQ['user'],
    pw=RABBITMQ['pass'],
    hostname=RABBITMQ['host'],
    port=RABBITMQ['post'],
    vhost=RABBITMQ['vhost']
)

#=========================================================================
#                          CELERY INFORMATION 
#=========================================================================
CELERY = cfg['celery']

# Set worker to ack only when return or failing (unhandled expection)
task_acks_late = True

# Worker only gets one task at a time
worker_prefetch_multiplier = 1

QUERY_NAME = CELERY["query"]

# Create queue for worker
task_queues = [Queue(name=QUERY_NAME)]

# Set Redis key TTL (Time to live)
result_expires = 60 * 60 * 48  # 48 hours in seconds


# #=========================================================================
# #                          ML INFORMATION 
# #=========================================================================
ML_OBJECT_DETECTION_TASK_NAME = CELERY['object_detection_task']
ML_STORAGE_PATH = CELERY['storage_path']
ML_STORAGE_UPLOAD_PATH = CELERY['storage_upload_path']
ML_STORAGE_RESULTS_PATH = CELERY['storage_results_path']
ML_IMAGE_TYPE = CELERY['image_type']



# #=========================================================================
# #                          ENGINE CONFIG YOLOV8
# #=========================================================================
ML = cfg["ml"]
MODEL_PATH = ML['model_path']
LABLE_PATH = ML['label_path']

IOU_THRESHOLD = float(ML['iou_threshold'])
SCORE_THRESHOLD = float(ML['score_threshold'])