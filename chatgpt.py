import sopel
import openai
import requests
import textwrap
import apikeys

openai.api_key = OPENAI_API_KEY

@sopel.module.commands('chatgpt')
def openai_chat(bot, trigger):
    text = trigger.group(2)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": text,
            }
        ],
    )
    response = completion['choices'][0]['message']['content']

    response = response.encode("utf-8")
    response = textwrap.fill(response, 400)
    response = requests.post("https://dumpinen.com", data=response)
    chatgpt_output = response.text


    bot.say(f'chatgpt: {chatgpt_output}')