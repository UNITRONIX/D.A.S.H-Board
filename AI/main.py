from ollama import Client

client = Client()
note = 'memoryEN.md'
note_2 = 'speedtest_results.md'

with open(note, 'r', encoding='utf-8') as file:
    content = file.read()
with open(note_2, 'r', encoding='utf-8') as file:
    content_2 = file.read()

my_prompt = f'dash, turn on flashlight {content} {content_2}'

resp_fast = client.chat(
    model='llama3-gradient:latest',
    messages=[
        {"role": "user", "content": my_prompt}
    ],
    think=False
)

print(resp_fast["message"]["content"])
