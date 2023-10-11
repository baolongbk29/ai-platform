import configparser

cfg = configparser.ConfigParser()
cfg.read(r"E:\BaoLong\ai-platform\bot\bot_evironment.ini")

# =========================================================================
#                          HUGGINGFACE CONFIG
# =========================================================================
HUGGINGFACE = cfg["huggingface"]
HUGGINFACE_INFERENCE_TOKEN = HUGGINGFACE["inference_token"]
HUGGINFACE_MODEL_URL = HUGGINGFACE["model_url"]

# =========================================================================
#                          REDIS INFORMATION
# =========================================================================
REDIS = cfg["redis"]
REDIS_BACKEND = "redis://:{password}@{hostname}:{port}/{db}".format(
    hostname=REDIS["host"],
    password=REDIS["pass"],
    port=REDIS["port"],
    db=REDIS["db"],
)
REDIS_BACKEND_CHAT = "redis://:{password}@{hostname}:{port}/{db}".format(
    hostname=REDIS["host"],
    password=REDIS["pass"],
    port=REDIS["port"],
    db=REDIS["db_chat"],
)