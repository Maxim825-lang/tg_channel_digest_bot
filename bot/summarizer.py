import logging
import os
from collections import defaultdict

logger = logging.getLogger(__name__)

KEYWORDS = {
    "важно", "срочно", "запуск", "релиз", "закон", "рынок", "цена",
    "санкции", "обновление", "утечка", "сделка", "авария", "решение",
    "суд", "правительство", "компания", "рост", "падение",
}


async def summarize_messages(messages: list[dict]) -> str:
    """
    Генерирует текстовую выжимку из списка сообщений.
    Если задан OPENAI_API_KEY — использует OpenAI.
    Иначе — локальная extractive summary.
    """
    if not messages:
        return "За последние 24 часа важных сообщений не найдено."

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key:
        return await _openai_summary(messages, api_key)
    return _local_summary(messages)


async def _openai_summary(messages: list[dict], api_key: str) -> str:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Формируем контекст
    lines = []
    for m in messages:
        channel = m.get("channel", "?")
        text = m.get("text", "").strip()
        link = m.get("link", "")
        lines.append(f"[{channel}] {text}" + (f" ({link})" if link else ""))
    context = "\n\n".join(lines[:50])  # не больше 50 сообщений в промпт

    prompt = (
        "Ты помощник, который составляет краткий дайджест новостей из Telegram-каналов.\n"
        "Опирайся ТОЛЬКО на переданные сообщения. Не придумывай факты.\n"
        "Если данных мало — так и напиши.\n\n"
        "Составь выжимку на русском языке в формате:\n"
        "📰 Главное за день\n"
        "1. ...\n2. ...\n3. ...\n\n"
        "📌 По каналам\n"
        "...\n\n"
        "🔗 Источники\n"
        "- канал: ссылка (если есть)\n\n"
        f"Сообщения:\n{context}"
    )

    try:
        import openai
        client = openai.AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except ImportError:
        logger.warning("openai package not installed, falling back to local summary")
        return _local_summary(messages)
    except Exception as e:
        logger.error("OpenAI error: %s", e)
        return _local_summary(messages) + f"\n\n⚠️ OpenAI недоступен: {e}"


def _local_summary(messages: list[dict]) -> str:
    """Extractive summary без внешних API."""
    by_channel: dict[str, list[dict]] = defaultdict(list)
    for m in messages:
        channel = m.get("channel", "?")
        by_channel[channel].append(m)

    parts = ["📰 <b>Главное за день</b>\n"]

    # Топ сообщений
    top_msgs = sorted(messages, key=_score, reverse=True)[:10]
    for i, m in enumerate(top_msgs, 1):
        text = _truncate(m.get("text", ""), 200)
        parts.append(f"{i}. {text}")

    parts.append("\n📌 <b>По каналам</b>")
    for channel, msgs in by_channel.items():
        parts.append(f"\n<b>{channel}</b> — {len(msgs)} сообщ.")
        for m in msgs[:3]:
            text = _truncate(m.get("text", ""), 150)
            link = m.get("link", "")
            suffix = f' <a href="{link}">→</a>' if link else ""
            parts.append(f"• {text}{suffix}")

    parts.append("\n🔗 <b>Источники</b>")
    seen = set()
    for m in messages:
        channel = m.get("channel", "?")
        link = m.get("link", "")
        if channel not in seen:
            seen.add(channel)
            if link:
                base_link = "/".join(link.split("/")[:-1])
                parts.append(f"- {channel}: {base_link}")
            else:
                parts.append(f"- {channel}")

    return "\n".join(parts)


def _score(m: dict) -> float:
    text = m.get("text", "")
    views = m.get("views", 0) or 0
    kw_hits = sum(1 for kw in KEYWORDS if kw in text.lower())
    length_score = min(len(text) / 300, 1.0)
    return kw_hits * 2 + length_score + views / 10000


def _truncate(text: str, max_len: int) -> str:
    text = text.strip().replace("\n", " ")
    return text[:max_len] + "…" if len(text) > max_len else text
