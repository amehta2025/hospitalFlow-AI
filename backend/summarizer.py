from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_summary(metrics: dict, alerts: list, prediction: dict) -> str:
    alert_text = "\n".join([f"- [{a['level'].upper()}] {a['message']}" for a in alerts])
    top_factors = "\n".join([
        f"- {f['factor']}: {f['current_value']} (importance: {f['importance']})"
        for f in prediction.get("top_factors", [])
    ])

    prompt = f"""
You are an AI assistant helping hospital operations managers understand real-time clinical workflow data.

Current hospital metrics (last 10 minutes):
- ED average wait: {metrics.get('ed_avg_wait_minutes')} min
- ICU average wait: {metrics.get('icu_avg_wait_minutes')} min
- Lab turnaround: {metrics.get('lab_avg_wait_minutes')} min
- Discharge average wait: {metrics.get('discharge_avg_wait_minutes')} min
- Transport average wait: {metrics.get('transport_avg_wait_minutes')} min
- High severity events: {metrics.get('recent_high_severity_pct')}% of recent events

Active alerts:
{alert_text}

ML risk prediction: {prediction.get('prediction')} (score: {prediction.get('risk_score')})
Top contributing factors:
{top_factors}

Write a 3-4 sentence plain-English summary for an operations manager. Explain what is currently happening in the hospital, what is driving the risk, and what actions should be considered. Be direct and specific. Do not use bullet points.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.4,
    )

    return response.choices[0].message.content.strip()