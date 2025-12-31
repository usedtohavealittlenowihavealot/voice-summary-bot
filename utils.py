import os
from huggingface_hub import hf_hub_download
from config import logger


def ensure_model_exists(repo_id: str, filename: str) -> str:
    if os.path.exists(filename):
        logger.info(f' Файл модели найден локально: {filename}')
        return filename

    logger.info(f' Файл {filename} не найден. Загрузка с HuggingFace ({repo_id})...')
    try:
        model_path = hf_hub_download(repo_id=repo_id, filename=filename, local_dir='.', local_dir_use_symlinks=False)
        logger.info('Загрузка завершена')
        return model_path
    except Exception as e:
        logger.error(f'Ошибка загрузки модели: {e}')
        raise FileNotFoundError(f'Не удалось найти или скачать {filename}')