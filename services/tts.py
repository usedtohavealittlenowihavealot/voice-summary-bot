import torch
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
from config import logger

class TTSService:
    def __init__(self):
        torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, BaseDatasetConfig, XttsArgs])

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        if torch.backends.mps.is_available():
            self.device = 'mps'

        logger.info(f'loading TTS on {self.device}...')
        self.model = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(self.device)
        logger.info('TTS ready.')

    def generate_audio(self, text: str, speaker_wav: str, output_path: str):
        self.model.tts_to_file(text=text, speaker_wav=speaker_wav, language='ru', file_path=output_path, split_sentences=True)