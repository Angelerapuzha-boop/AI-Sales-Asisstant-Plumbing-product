from groq import Groq
from config import settings

_client = Groq(api_key=settings.GROQ_API_KEY)


def chat(messages: list[dict], system: str = "", temperature: float = 0.7, max_tokens: int = 2048) -> str:
    """Send messages to Groq Llama-3 and return text response."""
    payload = []
    if system:
        payload.append({"role": "system", "content": system})
    payload.extend(messages)

    response = _client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=payload,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def generate_sales_email(
    company_name: str,
    contact_name: str,
    industry: str,
    notes: str,
    sender_name: str = "Sales Team",
) -> dict:
    """Generate a personalised sales email using Groq Llama-3."""
    prompt = f"""Generate a professional, personalised B2B sales email.

Company: {company_name}
Contact: {contact_name}
Industry: {industry}
Context / notes: {notes}

Return ONLY valid JSON in this exact format:
{{
  "subject": "compelling subject line",
  "body": "full email body with greeting, value prop, CTA, and sign-off"
}}"""

    raw = chat([{"role": "user", "content": prompt}], temperature=0.8)

    # Parse JSON safely
    import json, re
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    return {"subject": "Following up from ProPlumb Supply", "body": raw}


def score_lead(company: dict) -> float:
    """Use Groq to score a lead from 0-100."""
    prompt = f"""Score this sales lead from 0 to 100. Consider company size, industry demand, engagement signals.

Company data:
{company}

Respond with ONLY a JSON object: {{"score": <number 0-100>, "reason": "<brief reason>"}}"""

    raw = chat([{"role": "user", "content": prompt}], temperature=0.3, max_tokens=200)

    import json, re
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        data = json.loads(match.group())
        return float(data.get("score", 50))
    return 50.0


def generate_call_script(company_name: str, contact_name: str, industry: str, notes: str) -> str:
    """Generate a Bland AI call script using Groq."""
    prompt = f"""Write a natural, professional AI phone call script for a sales representative calling {contact_name} at {company_name} ({industry} industry).

Context: {notes}

The script should:
- Start with a friendly introduction
- State the purpose clearly
- Ask qualifying questions
- Handle objections
- End with a clear next step (schedule meeting, send info, etc.)

Keep it under 300 words. Write it as instructions for an AI voice agent."""

    return chat([{"role": "user", "content": prompt}], temperature=0.7)


def generate_daily_report(stats: dict) -> str:
    """Generate a daily sales report summary."""
    prompt = f"""Write a concise daily sales report summary for our team.

Today's stats:
{stats}

Keep it under 150 words. Use bullet points. Be encouraging and action-oriented."""

    return chat([{"role": "user", "content": prompt}], temperature=0.6, max_tokens=300)
