###This file is generated by AI from prompts/src/main.py. DO NOT MODIFY THIS FILE MANUALLY###

import requests

discord_webhook = "https://discord.com/api/webhooks/1234567890/ABCDEFGHIJKLMN"


def send_discord(message: str) -> None:
    payload = {"content": message}
    response = requests.post(discord_webhook, json=payload)
    response.raise_for_status()
