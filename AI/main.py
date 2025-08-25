from ollama import Client
import pyttsx4

client = Client()
note = 'memoryEN.md'
note_2 = 'speedtest_results.md'

with open(note, 'r', encoding='utf-8') as file:
    content = file.read()
with open(note_2, 'r', encoding='utf-8') as file:
    content_2 = file.read()

my_prompt = f'Dash turn on the flashlight {content} {content_2}'

resp_fast = client.chat(
    model='deepseek-r1:14b',
    messages=[
        {"role": "user", "content": my_prompt}
    ],
    think=False
)

print(resp_fast["message"]["content"])
