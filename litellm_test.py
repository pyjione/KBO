import litellm

response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Hello! Which LLM are you using?"}
    ],
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

print(response['choices'][0]['message']['content'])