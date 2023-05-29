import threading
from queue import Queue
from collections import defaultdict

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    filters,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
)
from telegram.constants import ChatAction

import myToken
import json_manager
import scrap

user_data = {}


async def call_help(update, context):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="""
다음은 명령어 목록입니다.
/help : 도움말

/today : 오늘 요약

/selectkeyword <키워드> : 뉴스 검색 키워드 선택
/selectlocate <지역> : 날씨 안내 지역 선택

/selectsports : 스포츠 뉴스 종목 선택

/eclass <아이디> <비밀번호> : eClass 로그인 정보 입력""",
    )


async def introduce(update, context):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="""
안녕하세요! 저는 하루 요약 봇입니다.

명령어를 통해 eClass 로그인 정보,
날씨 지역, 뉴스 검색 키워드, 스포츠 종목을
선택하실 수 있습니다.

/help 로 명령어 목록을 확인해 보세요!""",
    )

    if update.message.chat_id not in user_data:
        user_data[str(update.message.chat_id)] = {
            "login_info": {
                "id": "x",
                "pw": "",
            },
            "sports": "축구",
            "location": "서울",
            "keyword": "넥슨",
        }
    json_manager.save_user_data("user_data.json", user_data)


async def echo(update, context):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=update.message.text,
    )


async def call_selectsports(update, context):
    task_buttons = [
        [
            InlineKeyboardButton("야구", callback_data=1),
            InlineKeyboardButton("해외야구", callback_data=2),
        ],
        [
            InlineKeyboardButton("축구", callback_data=3),
            InlineKeyboardButton("해외축구", callback_data=4),
        ],
        [
            InlineKeyboardButton("농구", callback_data=5),
            InlineKeyboardButton("배구", callback_data=6),
        ],
        [
            InlineKeyboardButton("골프", callback_data=7),
            InlineKeyboardButton("일반", callback_data=8),
        ],
        [InlineKeyboardButton("취소", callback_data=9)],
    ]

    reply_markup = InlineKeyboardMarkup(task_buttons)

    target_sports = ""
    chat_id = update.message.chat_id
    for user in user_data:
        if int(user) == chat_id:
            target_sports = user_data[user]["sports"]
            break

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f"현재 선택 종목은 {target_sports}입니다.\r\n종목을 선택해주세요.",
        reply_markup=reply_markup,
    )


async def button_callback(update, context):
    query = update.callback_query
    data = query.data

    if data == "9":
        await context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text="취소되었습니다.",
        )
        return

    sports_text = ""
    sports = ""
    if data == "1":
        sports_text = "야구"
        sports = "kbaseball"
    elif data == "2":
        sports_text = "해외야구"
        sports = "wbaseball"
    elif data == "3":
        sports_text = "축구"
        sports = "kfootball"
    elif data == "4":
        sports_text = "해외축구"
        sports = "wfootball"
    elif data == "5":
        sports_text = "농구"
        sports = "basketball"
    elif data == "6":
        sports_text = "배구"
        sports = "volleyball"
    elif data == "7":
        sports_text = "골프"
        sports = "golf"
    elif data == "8":
        sports_text = "일반"
        sports = "general"

    user_data[str(query.message.chat_id)]["sports"] = sports
    json_manager.save_user_data("user_data.json", user_data)
    await context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=f"스포츠 뉴스 종목이 {sports_text}로 변경되었습니다.",
    )


async def call_selectkeyword(update, context):
    user_data[str(update.message.chat_id)]["keyword"] = context.args[0]
    json_manager.save_user_data("user_data.json", user_data)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"키워드가 {context.args[0]}로 변경되었습니다.",
    )


async def call_selectlocate(update, context):
    user_data[str(update.message.chat_id)]["location"] = context.args[0]
    json_manager.save_user_data("user_data.json", user_data)

    result = Queue()
    thread = threading.Thread(
        target=scrap.location_check, args=[result, context.args[0]]
    )
    thread.start()
    thread.join()

    if result.get():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"지역이 {context.args[0]}으로 변경되었습니다.",
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="지역을 찾을 수 없습니다.",
        )


async def call_register(update, context):
    user_data[str(update.message.chat_id)]["login_info"]["id"] = context.args[0]
    user_data[str(update.message.chat_id)]["login_info"]["pw"] = context.args[1]
    json_manager.save_user_data("user_data.json", user_data)

    # eClass 아이디 유효성 확인하는 코드 추가하기

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="eClass 로그인 정보가 등록되었습니다.",
    )


async def call_today(update, context):
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING,
    )

    scrap_result = Queue()

    thread_news = threading.Thread(
        target=scrap.get_news,
        args=[scrap_result, user_data[str(update.message.chat_id)]["keyword"]],
    )
    thread_sports = threading.Thread(
        target=scrap.get_sports_news,
        args=[scrap_result, user_data[str(update.message.chat_id)]["sports"]],
    )
    thread_eClass = threading.Thread(
        target=scrap.get_eClass,
        args=[
            scrap_result,
            user_data[str(update.message.chat_id)]["login_info"]["id"],
            user_data[str(update.message.chat_id)]["login_info"]["pw"],
        ],
    )
    thread_weather = threading.Thread(
        target=scrap.get_weather,
        args=[scrap_result, user_data[str(update.message.chat_id)]["location"]],
    )

    thread_news.start()
    thread_sports.start()
    thread_eClass.start()
    thread_weather.start()

    thread_news.join()
    thread_sports.join()
    thread_eClass.join()
    thread_weather.join()

    result = defaultdict(str)
    for r in scrap_result.queue:
        key, val = r.popitem()
        result[key] = val

    result_text = ""
    result_text += result["weather"]
    # result_text += result["eClass"]
    result_text += result["news"]
    result_text += result["sports"]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=result_text,
    )


INPUT_ID, INPUT_PW = range(2)


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="eClass 아이디를 입력해주세요.",
    )
    return INPUT_ID


async def input_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data[str(update.message.chat_id)]["login_info"]["id"] = update.message.text
    json_manager.save_user_data("user_data.json", user_data)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="eClass 비밀번호를 입력해주세요.",
    )

    return INPUT_PW


async def input_pw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data[str(update.message.chat_id)]["login_info"]["pw"] = update.message.text
    json_manager.save_user_data("user_data.json", user_data)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="eClass 로그인 정보가 등록되었습니다.",
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="취소되었습니다.",
    )
    return ConversationHandler.END


if __name__ == "__main__":
    # 사용자 데이터
    user_data = json_manager.load_user_data("user_data.json")

    # 텔레그램 봇 시작
    application = ApplicationBuilder().token(myToken.token).build()

    start_handler = CommandHandler("start", introduce)
    help_handler = CommandHandler("help", call_help)
    select_keyword_handler = CommandHandler("selectkeyword", call_selectkeyword)
    select_locate_handler = CommandHandler("selectlocate", call_selectlocate)
    register_handler = CommandHandler("eclass", call_register)
    today_handler = CommandHandler("today", call_today)

    # eclassid_handler = CommandHandler("eclassid", call_eclassid)
    # eclasspw_handler = CommandHandler("eclasspw", call_eclasspw)

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(select_keyword_handler)
    application.add_handler(select_locate_handler)
    application.add_handler(register_handler)
    application.add_handler(today_handler)

    select_handler = CommandHandler("selectsports", call_selectsports)
    callback_handler = CallbackQueryHandler(button_callback)

    application.add_handler(select_handler)
    application.add_handler(callback_handler)

    eclass_register_handler = ConversationHandler(
        entry_points=[CommandHandler("test", test)],
        states={
            INPUT_ID: [MessageHandler(filters.TEXT & (~filters.COMMAND), input_id)],
            INPUT_PW: [MessageHandler(filters.TEXT & (~filters.COMMAND), input_pw)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(eclass_register_handler)

    application.run_polling()
