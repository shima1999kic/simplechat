# lambda/index.py
import json
import os
import re
import urllib.request

# FastAPI の推論エンドポイント（Colabで公開されたURLに変更）
FASTAPI_URL = os.environ.get("FASTAPI_URL", "https://3f9d-34-169-213-164.ngrok-free.app/generate")

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        # Cognito認証ユーザーのログ（任意）
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")

        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])

        print("User message:", message)
        print("Conversation history:", conversation_history)

        # FastAPI 用のリクエスト構築
        request_payload = {
            "message": message,
            "conversationHistory": conversation_history
        }
        headers = {"Content-Type": "application/json"}
        data = json.dumps(request_payload).encode("utf-8")

        # FastAPI にリクエスト送信
        req = urllib.request.Request(FASTAPI_URL, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req) as res:
            result = json.loads(res.read().decode("utf-8"))

        assistant_response = result.get("response", "")
        updated_history = result.get("conversationHistory", conversation_history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": assistant_response}
        ])

        # レスポンス返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": updated_history
            })
        }

    except Exception as error:
        print("Error:", str(error))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
