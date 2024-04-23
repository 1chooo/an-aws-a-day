import json
import os
from datetime import datetime
import time

import boto3
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (ApiClient, AudioMessage, Configuration,
                                  ImageMessage, MessagingApi, MessagingApiBlob,
                                  ReplyMessageRequest,
                                  ShowLoadingAnimationRequest, TextMessage)
from linebot.v3.webhooks import (AudioMessageContent, ImageMessageContent,
                                 MessageEvent, StickerMessageContent,
                                 TextMessageContent, VideoMessageContent)

CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(channel_secret=CHANNEL_SECRET)

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.show_loading_animation(
            ShowLoadingAnimationRequest(
                chat_id=event.source.user_id,
            )
        )
        reply_messages = []

        if event.message.text == "我想知道 AWS 的16項領導力準則":
            reply_messages = [
                TextMessage(
                    text=f"AWS ☁️ 的 16 項領導力準則是文化核心價值觀的體現，著重於滿足客戶需求並超越期望，以及追求卓越而非滿足現狀。"
                ),
                ImageMessage(
                    original_content_url = "https://line-workshop-test.s3.amazonaws.com/aws_leadership.jpg",
                    preview_image_url = "https://line-workshop-test.s3.amazonaws.com/aws_leadership.jpg",
                ),
                TextMessage(
                    text=f"同時，這些準則強調了團隊合作、創新、效率和對變革的開放態度，成為公司文化中的重要支柱。"
                ),
                TextMessage(
                    text=f"透過這些準則，AWS ☁️ 激勵著員工發揮最佳表現，持續挑戰自我，並不斷追求個人與團隊的成長。"
                ),
                TextMessage(
                    text=f"這些準則不僅是指導方針，更是推動公司進步和持續發展的動力所在。"
                ),
            ]
                

        else:
            reply_messages = [
                TextMessage(text=event.message.text),
            ]

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=reply_messages,
            )
        )

@handler.add(MessageEvent, message=StickerMessageContent)
def handle_sticker_message(event: MessageEvent):
    if event.source.type != "user":
        return
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.show_loading_animation(
            ShowLoadingAnimationRequest(
                chat_id=event.source.user_id,
            )
        )

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="$", emojis=[{"index": 0, "productId": "5ac21c46040ab15980c9b442", "emojiId": "138"}])]
            )
        )

@handler.add(MessageEvent, message=(ImageMessageContent,
                                    VideoMessageContent,
                                    AudioMessageContent))
def handle_content_message(event):
    """
    這裏 Lambda Functions 的 timeout only 3 sec, not enough to upload file to S3
    Change the timeout to 10 sec
    """
    start_time = time.time()
    if isinstance(event.message, ImageMessageContent):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessageContent):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessageContent):
        ext = 'm4a'
    else:
        return

    
    if event.source.type == 'user':
        source_id = event.source.user_id
    elif event.source.type == 'group':
        source_id = event.source.group_id
    elif event.source.type == 'room':
        source_id = event.source.room_id
    
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
    # Save the content to /tmp folder or lambda will not have permission to access it
    user_uploaded_image_file_name = f"/tmp/{source_id}-{current_time}.{ext}"
    s3_goal_file_path = f"{ext}/{source_id}-{current_time}.{ext}"
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        # 要加在 ReplyMessageRequest 裡面，不然會出現錯誤
        line_bot_api.show_loading_animation(
            ShowLoadingAnimationRequest(
                chat_id=event.source.user_id,
            )
        )
        line_bot_blob_api = MessagingApiBlob(api_client)
        message_content = line_bot_blob_api.get_message_content(message_id=event.message.id)
        with open(user_uploaded_image_file_name, 'wb') as tf:
            tf.write(message_content)

        print("File has been saved to /tmp folder.")
        s3_client.upload_file(user_uploaded_image_file_name, aws_bucket_name, s3_goal_file_path)
        os.remove(user_uploaded_image_file_name)
        print("File has been uploaded to S3.")

        end_time = time.time()

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text="Save content."),
                    TextMessage(text=f"File name: {user_uploaded_image_file_name}"),
                    TextMessage(text=f"Time elapsed: {end_time - start_time} seconds.")
                ]
            )
        )

aws_access_key_id = os.environ["AWS_CLIENT_ACCESS_KEY_ID"]
aws_secret_access_key = os.environ["AWS_CLIENT_SECRET_ACCESS_KEY"]
aws_bucket_arn = os.environ["AWS_CLIENT_BUCKET_ARN"]
aws_region_name = os.environ["AWS_CLIENT_REGION_NAME"]
aws_bucket_name = os.environ["AWS_CLIENT_BUCKET_NAME"]

s3_client = boto3.client(
    "s3",
    aws_access_key_id = aws_access_key_id,
    aws_secret_access_key = aws_secret_access_key,
    region_name=aws_region_name
)


def lambda_handler(event, context):
    try: 
        body = event["body"]
        signature = event["headers"]["x-line-signature"]

        store_user_log(body)

        handler.handle(body, signature)

        return {
            "statusCode": 201,
            "body": json.dumps("Hello from Lambda!")
        }
    except InvalidSignatureError:
        return {
            "statusCode": 400,
            body: "Invalid signature"
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(str(e))
        }
    
def store_user_log(body: str) -> None:
    # Here we don"t need to parse the body because it"s already a string
    # body = json.loads(body)
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")

    s3_goal_file_path = f"logs/{current_time}.log"
    lambda_tmp_file_file = "/tmp/events.log"

    with open(lambda_tmp_file_file, "a", encoding="utf-8") as f:
        f.write(f"{body}\n")
    s3_client.upload_file(lambda_tmp_file_file, aws_bucket_name, s3_goal_file_path)
    os.remove(lambda_tmp_file_file)
