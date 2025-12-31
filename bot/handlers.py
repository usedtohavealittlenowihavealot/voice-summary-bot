import os
import html
import asyncio
from aiogram import Router, F, types, Bot
from aiogram.filters import Command
from pydub import AudioSegment
from config import logger

router = Router()

def setup_router(asr_service, llm_service, tts_service):
    router.asr = asr_service
    router.llm = llm_service
    router.tts = tts_service
    return router


@router.message(Command('start'))
async def start_handler(message: types.Message):
    await message.reply(
        'Привет! Отправь голосовое сообщение или используй команды /суть или /продолжи в ответ на аудио.')

# для теста
@router.message(Command('ping'))
async def ping_handler(message: types.Message):
    await message.reply('pong')


@router.message(F.voice | F.video_note)
async def auto_handle_media(message: types.Message):
    if message.chat.type == 'private':
        await process_summary(message, get_file_id(message), get_ext(message))


@router.message(Command('суть', 'summary'))
async def command_summary(message: types.Message):
    target = message.reply_to_message
    if not target or (not target.voice and not target.video_note):
        return await message.reply('Ответьте на голосовое или видео-сообщение.')
    await process_summary(message, get_file_id(target), get_ext(target))


@router.message(Command('продолжи'))
async def command_continue(message: types.Message):
    target = message.reply_to_message
    if not target or (not target.voice and not target.video_note):
        return await message.reply('Ответьте на голосовое или видео-сообщение.')
    await process_continuation(message, get_file_id(target))


def get_file_id(message):
    return message.voice.file_id if message.voice else message.video_note.file_id


def get_ext(message):
    return '.ogg' if message.voice else '.mp4'


async def process_summary(message: types.Message, file_id: str, ext: str):
    bot: Bot = message.bot
    status = await message.reply('⏳⏳⏳')
    unique_id = f'{message.chat.id}_{message.message_id}'
    paths = {
        'input': f'input_{unique_id}{ext}',
        'wav': f'audio_{unique_id}.wav'
    }

    try:
        await bot.download(file_id, destination=paths['input'])
        await asyncio.to_thread(lambda: AudioSegment.from_file(paths['input']).export(paths['wav'], format='wav'))

        await status.edit_text("🎧🎧🎧")
        text = await asyncio.to_thread(router.asr.transcribe, paths['wav'])

        if not text or len(text.strip()) < 5:
            return await status.edit_text('Не удалось распознать речь')

        await status.edit_text('🧠🧠🧠')
        summary = await asyncio.to_thread(router.llm.summarize, text)

        preview = html.escape(text[:600] + '...' if len(text) > 600 else text)
        response = f'📝 <b>Саммари:</b>\n{html.escape(summary)}\n\n🔎 <b>Исходный текст:</b>\n<i>{preview}</i>'

        await status.delete()
        await message.reply(response, parse_mode='HTML')

    except Exception as e:
        logger.error(f'Summary error: {e}', exc_info=True)
        await status.edit_text('Произошла ошибка.')
    finally:
        cleanup(paths.values())


async def process_continuation(message: types.Message, file_id: str):
    bot: Bot = message.bot
    status = await message.reply('⏳⏳⏳')
    unique_id = f'{message.chat.id}_{message.message_id}'
    paths = {
        'input': f'temp_{unique_id}',
        'orig_wav': f'orig_{unique_id}.wav',
        'gen_wav': f'gen_{unique_id}.wav',
        'out_ogg': f'out_{unique_id}.ogg'
    }

    try:
        await bot.download(file_id, destination=paths['input'])
        await asyncio.to_thread(lambda: AudioSegment.from_file(paths['input']).export(paths['orig_wav'], format='wav'))
        text = await asyncio.to_thread(router.asr.transcribe, paths['orig_wav'])
        if not text: return await status.edit_text('Нет речи для продолжения')
        continuation = await asyncio.to_thread(router.llm.predict_continuation, text)
        if not continuation: return await status.edit_text('Не удалось придумать продолжение')
        await status.edit_text('🎙🎙🎙')
        await asyncio.to_thread(router.tts.generate_audio, continuation, paths['orig_wav'], paths['gen_wav'])
        await status.edit_text('🔧🔧🔧')
        await asyncio.to_thread(lambda: combine_audio(paths['orig_wav'], paths['gen_wav'], paths['out_ogg']))

        await status.delete()
        await message.reply_voice(types.FSInputFile(paths['out_ogg']))

    except Exception as e:
        logger.error(f'Continuation error: {e}', exc_info=True)
        await status.edit_text('Ошибка обработки')
    finally:
        cleanup(paths.values())


def combine_audio(orig_path, gen_path, out_path):
    s1 = AudioSegment.from_wav(orig_path)
    s2 = AudioSegment.from_wav(gen_path)
    s1.append(s2, crossfade=150).export(out_path, format="ogg", codec="libopus")


def cleanup(paths):
    for p in paths:
        if os.path.exists(p): os.remove(p)