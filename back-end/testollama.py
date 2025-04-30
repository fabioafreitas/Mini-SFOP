from ollama import Client

client = Client(host='http://localhost:11434')

response = client.chat(
    model='gemma3:1b',
    messages=[
        {'role': 'user', 'content': 'what is 1+1+1+1+1+1?'}
    ],
    stream=False  # ensures we get full response at once
)

print(response['message']['content'])
