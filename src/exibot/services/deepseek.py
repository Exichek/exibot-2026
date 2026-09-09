"""Сервис для работы с DeepSeek API."""

from openai import AsyncOpenAI


class DeepSeekService:
    """Выполнять текстовые запросы к DeepSeek."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
    ) -> None:
        """Инициализировать клиент DeepSeek."""
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self._model = model

    async def chat(
        self,
        system_prompt: str,
        user_message: str,
    ) -> str:
        """Получить обычный текстовый ответ модели."""
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
        )

        return (response.choices[0].message.content or "").strip()

    async def classify(
        self,
        system_prompt: str,
        user_message: str,
    ) -> str:
        """Получить короткий ответ модели для классификации текста."""
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            max_tokens=5,
            temperature=0,
        )

        return (response.choices[0].message.content or "").strip().lower()

    async def close(self) -> None:
        """Закрыть HTTP-клиент DeepSeek."""
        await self._client.close()
