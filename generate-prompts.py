from groq import Groq
from config import groq_key
from tqdm.auto import tqdm
import json

model = "llama-3.1-70b-versatile"

client = Groq(
    api_key=groq_key,
)

def gpt(x,system=None):
    if system:
        messages = [
            {
                "role" : "system",
                "content" : system
            }
        ]
    else:
        messages = []
    messages.append(
            {
                "role": "user",
                "content": x,
            })
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model,
    )

    return chat_completion.choices[0].message.content

with open('angel.txt',encoding='utf-8') as f:
    l = [x.strip() for x in f.readlines()]

system = """
You are virtual artist that draws pictures using Stable Diffusion XL in personalized style. You are provided with a request what to draw below in triple backquotes. Please return JSON containing the Stable Diffusion prompt to create a picture (prompt), and short title of the drawing (title).
{}
"""

result = []

for x in tqdm(l):
    res = gpt(system.format(x))
    if '{' in res and '}' in res:
        res = res[res.find('{'):]
        res = res[:res.find('}')+1]
        j = json.loads(res)
        result.append(j)
    else:
        print(f"Error processing prompt {x}")

with open('prompts.json','w',encoding='utf-8') as f:
    json.dump(result,f)
