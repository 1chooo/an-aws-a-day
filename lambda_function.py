# -*- coding: utf-8 -*-

import json
import os
import time
from datetime import datetime

import boto3
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (ApiClient, AudioMessage, Configuration,
                                  ImageMessage, MessagingApi, MessagingApiBlob,
                                  ReplyMessageRequest,
                                  ShowLoadingAnimationRequest, TextMessage,
                                  VideoMessage)
from linebot.v3.webhooks import (AudioMessageContent, FileMessageContent,
                                 ImageMessageContent, MessageEvent,
                                 StickerMessageContent, TextMessageContent,
                                 VideoMessageContent)

CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(channel_secret=CHANNEL_SECRET)

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

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    with ApiClient(configuration) as api_client:
        start_time = time.time()
        line_bot_api = MessagingApi(api_client)
        line_bot_api.show_loading_animation(
            ShowLoadingAnimationRequest(
                chat_id=event.source.user_id,
            )
        )
        reply_messages = []

        if event.message.text == "我想知道 AWS 創辦故事":
            reply_messages = get_aws_starting_story()
        elif event.message.text == "我想知道 AWS 提供的業務":
            reply_messages = get_aws_business_story()
        elif event.message.text == "我想知道 AWS 的16項領導力準則":
            reply_messages = get_aws_leadership_story()
        elif event.message.text == "我想知道 AWS 未來的發展方向":
            reply_messages = get_aws_future_story()
        elif event.message.text == "我想了解 AWS LINE BOT 開發團隊":
            reply_messages = get_aws_line_bot_development_story()
        elif event.message.text == "我想了解如何成為 AWS Educate 校園大使":
            reply_messages = get_aws_ambassador_story()
        else:
            reply_messages = [
                "DAMMMM 蟹 Bro, M3 換一句試試吧！",
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                f"Time elapsed: {time.time() - start_time} seconds."
            ]

            reply_messages = [TextMessage(text=message) for message in reply_messages]

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
                messages=[
                    TextMessage(text="$", emojis=[{"index": 0, "productId": "5ac21c46040ab15980c9b442", "emojiId": "138"}])
                ]
            )
        )

@handler.add(MessageEvent, message=(ImageMessageContent,
                                    VideoMessageContent,
                                    AudioMessageContent))
def handle_content_message(event: MessageEvent):
    """
    The timeout for Lambda Functions here is only 3 seconds, 
    which is insufficient for uploading files to S3. 
    Please increase the timeout to 10 seconds or possibly more.
    """
    start_time = time.time()
    if isinstance(event.message, ImageMessageContent):
        ext = "jpg"
    elif isinstance(event.message, VideoMessageContent):
        ext = "mp4"
    elif isinstance(event.message, AudioMessageContent):
        ext = "m4a"
    else:
        return

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.show_loading_animation(
            ShowLoadingAnimationRequest(
                chat_id=event.source.user_id,
            )
        )

        line_bot_blob_api = MessagingApiBlob(api_client)

        store_img_to_s3(event, ext, line_bot_blob_api)

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text="Save content."),
                    TextMessage(text=f"Time elapsed: {time.time() - start_time} seconds.")
                ]
            )
        )

@staticmethod
def lambda_handler(event, *args, **kwargs):
    try: 
        body = event["body"]
        signature = event["headers"]["x-line-signature"]

        # Here we don"t need to parse the body because it"s already a string
        # body = json.loads(body)
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

@staticmethod
def get_source_id(event: MessageEvent) -> str:
    if event.source.type == "user":
        source_id = event.source.user_id
    elif event.source.type == "group":
        source_id = event.source.group_id
    elif event.source.type == "room":
        source_id = event.source.room_id
    return source_id

@staticmethod
def store_img_to_s3(
        event: MessageEvent, ext: str, 
        line_bot_blob_api: MessagingApiBlob) -> None:
    source_id = get_source_id(event)
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")

    # Save the content to /tmp folder or lambda will not have permission to access it
    user_uploaded_image_file_name = f"/tmp/{source_id}-{current_time}.{ext}"
    s3_goal_file_path = f"{ext}/{source_id}-{current_time}.{ext}"

    message_content = line_bot_blob_api.get_message_content(message_id=event.message.id)
    with open(user_uploaded_image_file_name, "wb") as tf:
        tf.write(message_content)

    s3_client.upload_file(user_uploaded_image_file_name, aws_bucket_name, s3_goal_file_path)
    os.remove(user_uploaded_image_file_name)

@staticmethod
def store_user_log(body: str) -> None:
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")

    s3_goal_file_path = f"logs/{current_time}.log"
    lambda_tmp_file_file = "/tmp/events.log"

    with open(lambda_tmp_file_file, "a", encoding="utf-8") as f:
        f.write(f"{body}\n")
    s3_client.upload_file(lambda_tmp_file_file, aws_bucket_name, s3_goal_file_path)
    os.remove(lambda_tmp_file_file)


AWS_STARTING_STORY: str = "我想知道 AWS 創辦故事"
AWS_BUSINESS: str = "我想知道 AWS 提供的業務"
AWS_LEADERSHIP: str = "我想知道 AWS 的16項領導力準則"
AWS_FUTURE: str = "我想知道 AWS 未來的發展方向"
AWS_LINE_BOT_DEVELOPMENT: str = "我想了解 AWS LINE BOT 開發團隊"
AWS_AMBASSADOR: str = "我想了解如何成為 AWS Educate 校園大使"

reserved_words = [
    AWS_STARTING_STORY,
    AWS_BUSINESS,
    AWS_LEADERSHIP,
    AWS_FUTURE,
    AWS_LINE_BOT_DEVELOPMENT,
    AWS_AMBASSADOR
]

def is_default_story(sended_message: str) -> bool:
    if sended_message in reserved_words:
        return sended_message
    else:
        return False
    
def get_default_story(default_word):
    if default_word == AWS_STARTING_STORY:
        return get_aws_starting_story()
    elif default_word == AWS_BUSINESS:
        return get_aws_business_story()
    elif default_word == AWS_LEADERSHIP:
        return get_aws_leadership_story()
    elif default_word == AWS_FUTURE:
        return get_aws_future_story()
    elif default_word == AWS_LINE_BOT_DEVELOPMENT:
        return get_aws_line_bot_development_story()
    elif default_word == AWS_AMBASSADOR:
        return get_aws_ambassador_story()

def get_aws_starting_story() -> list[TextMessage]:
    return [
        TextMessage(
            text="AWS ☁️ 的創辦故事始於 2003 年，當時亞馬遜公司的 Jeff Bezos 意識到他們在建設強大的內部基礎設施方面取得了不錯的進展！"
        ),
        ImageMessage(
            original_content_url = "https://line-workshop-test.s3.amazonaws.com/jeff_bezos.jpeg",
            preview_image_url = "https://line-workshop-test.s3.amazonaws.com/jeff_bezos.jpeg",
        ),
        TextMessage(
            text="他認識到這個基礎設施可以成為一個強大的雲端運算平台，能夠為其他企業提供服務。於是在 2006 年，AWS ☁️ 正式推出，開始提供雲端服務。"
        ),
        TextMessage(
            text="AWS ☁️ 的成功與其開放性、靈活性和不斷創新的企業文化有關。"
        ),
        TextMessage(
            text="這一切都源於 Jeff Bezos 對技術和未來的敏銳洞察力✨，他能看到潛在的機會並推動公司朝著新的方向發展。"
        ),
    ]

def get_aws_business_story( ) -> list[TextMessage]:
    return [
        TextMessage(
            text="AWS ☁️ 提供多樣化的雲端運算服務，包括計算（如 EC2 與 Lambda）、儲存（如 S3）、資料庫（如 RDS）、機器學習、人工智慧、物聯網、區塊鏈等。"
        ),
        TextMessage(
            text="舉例來說，EC2 提供虛擬伺服器，Lambda 則提供無需管理伺服器的程式碼執行環境。同時，S3 提供無限儲存空間，RDS 提供受管理的資料庫服務。API Gateway 可建立、部署和管理安全的 API，讓您輕鬆構建和監控應用程式介面。"
        ),
        ImageMessage(
            original_content_url = "https://line-workshop-test.s3.amazonaws.com/aws_services.png",
            preview_image_url = "https://line-workshop-test.s3.amazonaws.com/aws_services.png",
        ),
        TextMessage(
            text="AWS ☁️ 致力於為客戶提供完整、可擴展且高度安全的雲端解決方案。"
        ),
        TextMessage(
            text="且 AWS ☁️ 的多樣性和高度可靠性確保您可以找到符合您業務需求的解決方案。"
        ),
    ]

def get_aws_leadership_story( ) -> list[TextMessage]:
    return [
        TextMessage(
            text="AWS ☁️ 的 16 項領導力準則是文化核心價值觀的體現，著重於滿足客戶需求並超越期望，以及追求卓越而非滿足現狀。"
        ),
        ImageMessage(
            original_content_url = "https://line-workshop-test.s3.amazonaws.com/aws_leadership.jpg",
            preview_image_url = "https://line-workshop-test.s3.amazonaws.com/aws_leadership.jpg",
        ),
        TextMessage(
            text="同時，這些準則強調了團隊合作、創新、效率和對變革的開放態度，成為公司文化中的重要支柱。"
        ),
        TextMessage(
            text="透過這些準則，AWS ☁️ 激勵著員工發揮最佳表現，持續挑戰自我，並不斷追求個人與團隊的成長。"
        ),
        TextMessage(
            text="這些準則不僅是指導方針，更是推動公司進步和持續發展的動力所在。"
        ),
    ]

def get_aws_future_story( ) -> list[TextMessage]:
    return [
        TextMessage(
            text="AWS ☁️ 將持續引領雲端運算發展，擴展服務和解決方案以滿足客戶需求。"
        ),
        TextMessage(
            text="未來將深入研究人工智慧、機器學習等，提供更智能、靈活的解決方案。"
        ),
        TextMessage(
            text="AWS ☁️ 致力於提升雲端基礎設施性能和安全性，保障客戶資料安全。"
        ),
        TextMessage(
            text="AWS ☁️ 積極推動環保和可持續發展，尋求綠色能源方案與客戶攜手實現可持續目標"
        ),
        ImageMessage(
            original_content_url = "https://line-workshop-test.s3.amazonaws.com/aws_future.jpg",
            preview_image_url = "https://line-workshop-test.s3.amazonaws.com/aws_future.jpg",
        ),
    ]

def get_aws_line_bot_development_story( ) -> list[TextMessage]:
    return [
        TextMessage(
            text="嗨！👋 \n我們是第五屆 AWS Educate 校園大使"
        ),
        TextMessage(
            text="我是你的 AWS 小幫手，將帶你探索 Amazon Web Services 的無限可能。"
        ),
        TextMessage(
            text="將陪你一同踏上雲端運算的冒險之旅。AWS 提供豐富多元的雲端服務，從運算到儲存，應有盡有。"
        ),
        TextMessage(
            text="我會與你分享 AWS 的最新動態、技術見解，以及 AWS Educate 獨家的學習體驗，讓我們一同迎接科技的挑戰吧！🌟💡"
        ),
        ImageMessage(
            original_content_url = "https://1225-line-workshop-demo-g0.s3.amazonaws.com/aws_educate.png",
            preview_image_url = "https://1225-line-workshop-demo-g0.s3.amazonaws.com/aws_educate.png",
        ),
    ]

def get_aws_ambassador_story() -> list[TextMessage]:
    return [
        TextMessage(
            text="成為AWS Educate校園大使是一個很讚的機會👍 "
        ),
        TextMessage(
            text="你可以積極參與AWS Educate舉辦的大小活動，確保你充分了解AWS雲端運算和相關技術。\n也可以先透過以下連結註冊體驗 AWS Educate\n👉🏻 https://awseducate.tw/2"
        ),
        TextMessage(
            text="如果你有興趣成為AWS Educate校園大使，建議你可以定期關注AWS Educate的社群與活動內容，以便瞭解校園大使計劃的最新消息。"
        ),
        TextMessage(
            text="期待你能加入 AWS Educate 校園大使，讓我們一起過程中都能有所收穫 🫵🏻"
        ),
        ImageMessage(
            original_content_url = "https://line-workshop-test.s3.amazonaws.com/become_ambassader.jpg",
            preview_image_url = "https://line-workshop-test.s3.amazonaws.com/become_ambassader.jpg",
        ),
    ]

