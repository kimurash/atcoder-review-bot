import os
from random import choice

from dotenv import find_dotenv
from dotenv import load_dotenv
# FastAPI
from fastapi import (
    APIRouter,
    Header, 
    Request
)
from starlette.exceptions import HTTPException
# LINE Bot SDK
from linebot import (
    LineBotApi,
    WebhookHandler
)
from linebot.models import (
    # イベント
    MessageEvent,
    # メッセージ
    TextMessage,
    StickerMessage,
    # テンプレートメッセージ
    ButtonsTemplate,
    # メッセージ送信
    TextSendMessage,
    StickerSendMessage,
    TemplateSendMessage,
    # クイックリプライ
    QuickReply,
    QuickReplyButton,
    # アクション
    MessageAction,
    URIAction
)
from linebot.v3.exceptions import InvalidSignatureError

# パッケージ内では暗黙的相対インポートが行われない
from api.routers.config import *
from api.routers.task_selector import TaskSelector


load_dotenv(find_dotenv())

line_bot_api = LineBotApi(os.getenv('LINE_ACCESS_TOKEN'))
# LINE Platformからのリクエストを処理するためのハンドラ
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

router = APIRouter()
task_selector = TaskSelector()

@router.post(
    '/api/callback',
    summary='LINE Message APIからのコールバック',
    description='ユーザーからメッセージを受信した際にMessage APIからここにリクエストが送られる',
)
async def callback(request: Request, x_line_signature=Header(None)):
    body = await request.body()

    try:
		# リクエストがLINE Platformからのものか検証する
        handler.handle(body.decode('utf-8'), x_line_signature)

    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail='InvalidSignatureError')
    
    return 'OK'

# メッセージイベントかつテキストメッセージを受け取ったとき
@handler.add(MessageEvent, message=TextMessage)
def handle_txt_msg(event: MessageEvent):
    recv_msg = event.message.text
    match recv_msg:
        case '復習':
            recommend_task()
            ask_result()
        case '解けた！':
            send_stamp(AC_STAMP)
        case 'あともう一歩':
            send_stamp(ALMOST_AC_STAMP)
        case '解けなかった':
            send_stamp(CANNOT_AC_STAMP)
        case _: # 生死確認のオウム返し
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=event.message.text)
            )

# メッセージイベントかつスタンプメッセージを受け取ったとき
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_msg(event: MessageEvent):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            # XXX:LINEスタンプでないとき
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id
        )
    )

def recommend_task():
    # Notionから問題を取得
    prime_task = task_selector.get_prime_task()

    if prime_task is None:
        # テキストメッセージを送信する
        line_bot_api.push_message(
            os.environ.get('LINE_USER_ID'),
            TextSendMessage(text='復習すべき問題はありません')
        )
        return

    btn_template = make_btn_template(prime_task)
    line_bot_api.push_message(
        os.environ.get('LINE_USER_ID'),
        btn_template
    )

def make_btn_template(prime_task: dict):
    props = prime_task['properties']
    title = props['Name']['title'][0]['plain_text']
    url = props['URL']['url']

    priority = task_selector.get_priority(prime_task)

    btn_template = TemplateSendMessage(
        alt_text=title,
        template=ButtonsTemplate(
            title=title,
            text=f'優先度: {priority}',
            image_size='cover',
            thumbnail_image_url='https://img.atcoder.jp/assets/atcoder.png',
            actions=[
                URIAction(
                    uri=url,
                    label='問題へのリンク'
                )
            ]
        )
    )
    
    return btn_template

def ask_result():
    quick_reply_msg = make_quick_reply()
    line_bot_api.push_message(
        os.getenv('LINE_USER_ID'),
        quick_reply_msg
    )

def make_quick_reply():
    items = [
        QuickReplyButton(
            action=MessageAction(
                label=AC,
                text=AC
            )
        ),
        QuickReplyButton(
            action=MessageAction(
                label=ALMOST_AC,
                text=ALMOST_AC
            )
        ),
        QuickReplyButton(
            action=MessageAction(
                label=CANNOT_AC,
                text=CANNOT_AC
            )
        )
    ]

    quick_reply_msg = TextSendMessage(
        text='解けた？',
        quick_reply=QuickReply(items=items)
    )

    return quick_reply_msg

def send_stamp(stamp_list: list[dict]):
    random_stamp = choice(stamp_list)
    line_bot_api.push_message(
        os.getenv('LINE_USER_ID'),
        StickerSendMessage(
            package_id=random_stamp['package_id'],
            sticker_id=random_stamp['sticker_id']
        )
    )
    
