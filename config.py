import os
import logging
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError('BOT_TOKEN не найден')

HF_REPO_ID = 'bartowski/Qwen2.5-7B-Instruct-GGUF'
MODEL_FILENAME = 'Qwen2.5-7B-Instruct-Q5_K_M.gguf'
MODEL_PATH = MODEL_FILENAME


LLAMA_GPU_LAYERS = -1
LLAMA_CTX_SIZE = 16384

WHISPER_SIZE = 'small'
WHISPER_DEVICE = 'cpu'
WHISPER_TYPE = 'int8'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('VoiceBot')