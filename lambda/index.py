from fastapi import FastAPI, Request
from pydantic import BaseModel
import json
import boto3
import os
import re

app = FastAPI()

# Bedrockの初期化
MODEL_ID = os.environ.get("MODEL_ID", "us.amazon.nova-lite-v1:0")
REGION = "us-east-1"  # 適宜変更
bedrock_client = boto3.client('bedrock-runtime', region_name=REGION)

class ChatRequest(BaseModel):
    message: str
    conversationHistory: list = []

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        print("Received:", request.dict())

        # メッセージ構成
        messages = request.conversationHistory.copy()
        messages.append({"role": "user", "content": request.message})

        bedrock_messages = []
        for msg in messages:
            bedrock_messages.append({
                "role": msg["role"],
                "content": [{"text": msg["content"]}]
            })

        payload = {
            "messages": bedrock_messages,
            "inferenceConfig": {
                "maxTokens": 512,
                "stopSequences": [],
                "temperature": 0.7,
                "topP": 0.9
            }
        }

        response = bedrock_client.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(payload),
            contentType="application/json"
        )
        response_body = json.loads(response['body'].read())
        assistant_response = response_body['output']['message']['content'][0]['text']

        messages.append({
            "role": "assistant",
            "content": assistant_response
        })

        return {
            "success": True,
            "response": assistant_response,
            "conversationHistory": messages
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
