from ai_coder.ai_decorators import ai_code
from ai_coder.llm_client import call_llm
discord_webhook = "https://discord.com/api/webhooks/1234567890/ABCDEFGHIJKLMN"

class AINews:
    def __init__(self):
        pass
    @ai_code
    def article_summary(self, url: str) -> str:
        f"""Fetch a webpage and call {call_llm} to get the summary of the webpage. 
        The input is the url of the webpage and the output is the summary of the webpage."""
    @ai_code
    def send_discord(self, message: str) -> None:
        f"""
        Implement a Function to send a message to a Discord webhook
        :param message: string, the message to send
        the discord_webhook is {discord_webhook}
        """
    @ai_code
    def split_messages_to_send(self, message, delimiter = "\n") -> None:
        f"""Implement a python function that can split a message and send it to discord.
        :param message: string, the message to send to discord
        :param delimiter: string, the delimiter to split the message
        Rules:c
        1. The message is a long string that has bullet points and delimited by "delimiter".
        2. The message should be split by 2000 characters and send to discord.
        3. The message send to discord should be sub group of the original message, which is split by "delimiter", and has a maximum length of 2000 characters.

        To send to discord you can call {send_discord} function.
        """

if __name__ == "__main__":
   ainews = AINews()
   print(ainews.article_summary("https://techcrunch.com/2024/03/27/amazon-doubles-down-on-anthropic-completing-its-planned-4b-investment/"))