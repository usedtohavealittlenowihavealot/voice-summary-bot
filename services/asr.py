from faster_whisper import WhisperModel
from config import WHISPER_SIZE, WHISPER_DEVICE, WHISPER_TYPE, logger

class ASRService:
    def __init__(self):
        logger.info('loading ASR model...')
        self.model = WhisperModel(WHISPER_SIZE, device=WHISPER_DEVICE, compute_type=WHISPER_TYPE)
        logger.info('ready')

    def transcribe(self, audio_path: str) -> str:
        segments, _ = self.model.transcribe(audio_path, beam_size=5, language='ru')
        return ' '.join([s.text for s in segments])