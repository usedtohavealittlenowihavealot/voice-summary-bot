# Voice Summary & Clone Bot

Телеграм-бот для обработки голосовых сообщений. Умеет переводить голос в текст, выделять суть (саммари) и генерировать продолжение речи, клонируя голос говорящего.

## Возможности

*   **ASR (Speech-to-Text):** Транскрибация голосовых и видеосообщений (Faster-Whisper).
*   **LLM :** Генерация кратких выжимок (Summary) и семантическое продолжение мысли (Qwen 2.5).
*   **Voice Cloning (TTS):** Синтез продолжения речи голосом оригинала (Coqui XTTS v2).

## Требования

*   Python 3.10+
*   FFmpeg (установленный в системе)
*   ~8 GB RAM (для работы моделей на CPU)
*   GPU (желательно)

## Установка

1.  **Клонировать репозиторий**
    ```bash
    git clone https://github.com/usedtohavealittlenowihavealot/voice-summary-bot.git
    cd voice-summary-bot
    ```

2.  **Установить FFmpeg:**
    *   macOS: `brew install ffmpeg`  
    *   Ubuntu: `sudo apt install ffmpeg`
    *   Windows: скачать и добавить в PATH


3.  **Создать виртуальное окружение и установить зависимости:**
    ```bash
    python -m venv venv
    source venv/bin/activate 
    pip install -r requirements.txt
    ```

4.  **Настройка:**
    Создайть файл `.env` и указать токен вашего бота:
    ```ini
    BOT_TOKEN=YOUR_TOKEN
    ```

## Запуск

```bash
python main.py