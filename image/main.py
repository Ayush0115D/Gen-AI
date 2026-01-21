from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
          max_tokens=120, 
    messages=[
        {
            "role": "user",
            "content": [
                { "type": "text", "text": "Generate a caption for this image in about 50 words" },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://images.pexels.com/photos/879109/pexels-photo-879109.jpeg"
                    }
                }
            ]
        }
    ],
)

print("Response:", response.choices[0].message.content)
#we can also pass a local file as base64 image,for this we have to convert image to base64string
