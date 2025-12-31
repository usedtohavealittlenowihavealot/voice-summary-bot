import re
import difflib
from llama_cpp import Llama
from config import LLAMA_GPU_LAYERS, LLAMA_CTX_SIZE, logger

class LLMService:
    def __init__(self, model_path: str):
        logger.info(f'loading llm from {model_path}...')
        self.llm = Llama(model_path=model_path, n_ctx=LLAMA_CTX_SIZE, n_gpu_layers=LLAMA_GPU_LAYERS, verbose=False)
        logger.info('llm ready')

    def summarize(self, text: str) -> str:
        if len(text.split()) < 20:
            return 'Текст слишком короткий для пересказа'

        sys_msg = (
            'Ты — гениальный редактор. Твоя суперсила — превращать длинную, сбивчивую устную речь '
            'в лаконичный, плотный и понятный текст. Убирай воду, повторы, слова-паразиты. '
            'Сохраняй логику и факты. Стиль: инфостиль. Описывай контекст и эмоции.'
        )

        prompt = (
            f'<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{sys_msg}<|eot_id|>'
            f'<|start_header_id|>user<|end_header_id|>\n\nТекст: {text}<|eot_id|>'
            f'<|start_header_id|>assistant<|end_header_id|>\n\n'
        )

        output = self.llm(prompt,max_tokens=600,stop=['<|eot_id|>'], echo=False, temperature=0.1, top_p=0.95, repeat_penalty=1.2)
        return re.sub(r'<\|.*?\|>', '', output['choices'][0]['text']).strip()

    def predict_continuation(self, text: str) -> str:
        sys_msg = (
            'Ты — гениальный импровизатор. Твоя задача — услышать КОНЕЦ фразы и мгновенно продолжить ее. '
            'Не повторяй слова из конца фразы. Начинай сразу с новой мысли. Будь краток.'
        )
        context_text = text[-250:]

        prompt = (
            f'<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{sys_msg}<|eot_id|>'
            f'<|start_header_id|>user<|end_header_id|>\n\nКонец фразы: ...{context_text}»\nПродолжение:<|eot_id|>'
            f'<|start_header_id|>assistant<|end_header_id|>\n\n'
        )

        output = self.llm(prompt, max_tokens=100, stop=['<|eot_id|>', '\n', '«'], echo=False, temperature=0.6, top_p=0.9, repeat_penalty=1.15)

        generated = re.sub(r'<\|.*?\|>', '', output['choices'][0]['text']).strip()
        return self._clean_overlap(context_text, generated)

    def _clean_overlap(self, context: str, generated: str) -> str:
        s = difflib.SequenceMatcher(None, context, generated)
        match = s.find_longest_match(0, len(context), 0, len(generated))
        if (match.a + match.size == len(context)) and (match.b == 0) and (match.size > 3):
            return generated[match.size:].lstrip()
        return generated