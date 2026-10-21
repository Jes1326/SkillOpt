import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://your-endpoint.openai.azure.com/"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
)

response = client.chat.completions.create(
    model=os.getenv("TARGET_MODEL", "gpt-4o"),
    messages=[
        {"role": "user", "content": "Say hello"}
    ]
)

print(response.choices[0].message.content)
print(response.choices[0].message.content)