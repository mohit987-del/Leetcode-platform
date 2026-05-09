from django.conf import settings

import requests


def run_submission(payload):
    response = requests.post(
        f"{settings.JUDGE_RUNNER_URL}/internal/judge/submissions/",
        json=payload,
        headers={"Authorization": f"Bearer {settings.JUDGE_RUNNER_TOKEN}"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
