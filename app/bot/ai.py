import os
import json
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")
MODEL_QUICK = os.getenv("OPENAI_MODEL_QUICK", "gpt-4.1-mini")

PERSONA = (
    "You are a direct, honest accountability coach for an 18-year-old student and solo "
    "founder in Mumbai. He's balancing VIIE coursework, running Adgenix (his ad agency), "
    "a 2-year plan to transfer to Rutgers, and personal goals including gym, piano, guitar, "
    "and Youth Exchange Program applications. Be specific and cite real numbers from the "
    "data given. Never use generic motivational language, rule-of-three lists, or "
    "em-dash-heavy rhetorical flourishes. Keep it tight — no filler."
)


async def generate_weekly_summary(data: dict) -> str:
    prompt = (
        f"{PERSONA}\n\nHere is this week's structured data:\n{json.dumps(data, indent=2)}\n\n"
        "Write: (1) 2-3 sentences of honest analysis citing actual numbers, "
        "(2) one specific thing he did well, named specifically, "
        "(3) one specific thing to tighten up next week, with a concrete suggestion. "
        "Under 130 words total."
    )
    resp = await client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
    )
    return resp.choices[0].message.content.strip()


async def generate_monthly_summary(data: dict) -> str:
    prompt = (
        f"{PERSONA}\n\nHere is this month's structured data (habits, mood, wellness, "
        f"finances, reflection, focus/distractions):\n{json.dumps(data, indent=2)}\n\n"
        "Write a monthly review covering: budget performance vs plan, habit consistency "
        "(call out the strongest and weakest habits by name), mood/wellness trend, and "
        "how well he stuck to his stated focus areas vs distractions. End with ONE concrete "
        "adjustment for next month. Under 220 words. No headers, just flowing paragraphs."
    )
    resp = await client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
    )
    return resp.choices[0].message.content.strip()


async def answer_question(question: str, context_data: dict) -> str:
    prompt = (
        f"{PERSONA}\n\nRecent data for context:\n{json.dumps(context_data, indent=2)}\n\n"
        f"He just asked: \"{question}\"\n\nAnswer directly using the data above. "
        "If the data doesn't cover what he's asking, say so plainly instead of guessing. "
        "Under 100 words."
    )
    resp = await client.chat.completions.create(
        model=MODEL_QUICK,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    return resp.choices[0].message.content.strip()
