import logging
import random
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes, InlineQueryHandler, MessageHandler, filters, CallbackQueryHandler, CommandHandler
import aiohttp
from utils.db import get_db
from uuid import uuid4
import telegram

logger = logging.getLogger(__name__)

# Helper function to get the filters collection (sync since pymongo is used)
def get_filters_collection():
    db = get_db()  # Synchronous call
    return db.get_collection("filters")

# --- Couple Command ---
async def couple_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("This command can only be used in groups! 👥")
        return

    try:
        admins = await context.bot.get_chat_administrators(chat.id)
        members = [admin.user for admin in admins if not admin.user.is_bot]
        if len(members) < 2:
            await context.bot.send_message(
                chat_id=chat.id,
                text="Not enough non-bot members in the group to form a couple! 😅"
            )
            return

        user1, user2 = random.sample(members, 2)
        user1_link = f"tg://user?id={user1.id}"
        user2_link = f"tg://user?id={user2.id}"

        caption = (
            "🙈🎀𝗖❀𝗨𝗣𝗟𝗘 ❀𝗙 𝗧𝗛𝗘 𝗗𝗔𝗬😘🎀\n"
            f"♡\n"
            f"°\n"
            f"°❀💗\n"
            f"[{user1.first_name}]({user1_link}) + [{user2.first_name}]({user2_link}) = 💘\n"
            f"Mᴀʏ Yᴏᴜʀ ʟᴏᴠᴇ ʙʟᴏᴏᴍ🌸🌸\n"
            f"°ᴄ❀ᴜᴘʟᴇ ❣️\n"
            f"♡"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.waifu.pics/sfw/waifu") as response:
                if response.status != 200:
                    await context.bot.send_message(
                        chat_id=chat.id,
                        text="Couldn’t fetch a couple image. Try again later! 😓"
                    )
                    return
                data = await response.json()
                image_url = data["url"]

        await context.bot.send_photo(
            chat_id=chat.id,
            photo=image_url,
            caption=caption,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in couple command: {e}")
        try:
            await context.bot.send_message(
                chat_id=chat.id,
                text="An error occurred while finding a couple. Try again later! 😓"
            )
        except Exception as send_error:
            logger.error(f"Failed to send error message: {send_error}")

# --- Whisper Command ---
async def whisper_inline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query
    if not query:
        results = [
            InlineQueryResultArticle(
                id=str(uuid4()),
                title="Whisper 💬",
                description="Send a secret message to a user",
                input_message_content=InputTextMessageContent(
                    "Click to send a whisper message 💬\nFormat: @botusername <message> @username"
                )
            )
        ]
        await update.inline_query.answer(results)
        return

    bot = context.bot
    bot_username = bot.username.lower()
    pattern = rf"^{re.escape(bot_username)}\s+(.+?)\s+@(\w+)$"
    match = re.match(pattern, query.lower(), re.IGNORECASE)

    if not match:
        return

    message = match.group(1)
    username = match.group(2)

    try:
        chat = update.effective_chat
        if chat.type not in ["group", "supergroup"]:
            return

        members = [m.user async for m in context.bot.get_chat_members(chat.id) if not m.user.is_bot]
        target_user = next((m for m in members if m.username and m.username.lower() == username.lower()), None)

        if not target_user:
            await update.inline_query.answer([])
            return

        whisper_id = str(uuid4())
        context.bot_data[whisper_id] = {
            "sender": update.effective_user.first_name,
            "message": message,
            "target_user_id": target_user.id
        }

        keyboard = [[InlineKeyboardButton("Open Whisper 🔒", callback_data=f"whisper_{whisper_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=target_user.id,
            text=f"💬 You have a whisper from {update.effective_user.first_name}!",
            reply_markup=reply_markup
        )
        await update.inline_query.answer([])
    except Exception as e:
        logger.error(f"Error in whisper command: {e}")
        await update.inline_query.answer([])

async def whisper_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    user = query.from_user

    if not data.startswith("whisper_"):
        return

    whisper_id = data.split("_")[1]
    whisper_data = context.bot_data.get(whisper_id)

    if not whisper_data:
        await query.edit_message_text("This whisper has expired or does not exist.")
        await query.answer()
        return

    if user.id != whisper_data["target_user_id"]:
        await query.answer("This whisper is not for you! 🔒", show_alert=True)
        return

    await query.edit_message_text(
        f"💬 *Whisper from {whisper_data['sender']}:* {whisper_data['message']}",
        parse_mode="Markdown"
    )
    await query.answer()
    del context.bot_data[whisper_id]

# --- Fonts Command ---
FONTS = {
    "𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛": "𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛",
    "ꇙꌦꂵꃳꄲ꒒": "ꇙꌦꂵꃳꄲ꒒",
    "𝘽𝙊𝙇𝘿𝙄𝙏𝘼𝙇𝙄𝘾": "𝘽𝙊𝙇𝘿𝙄𝙏𝘼𝙇𝙄𝘾",
    "₵ʉɽɽɇ₦₵ɏ": "₵ʉɽɽɇ₦₵ɏ",
    "ℙ𝕣𝕖𝕞𝕚𝕦𝕞": "ℙ𝕣𝕖𝕞𝕚𝕦𝕞",
    "ᕼᗩᒪᗩᒪᗩ": "ᕼᗩᒪᗩᒪᗩ",
    "ɹǝʌǝɹsǝ": "ɹǝʌǝɹsǝ",
    "🄱🄾🅇": "🄱🄾🅇",
    "sᴍʟᴄᴀᴘ": "sᴍʟᴄᴀᴘ",
    "𝕰𝖒𝖕𝖎𝖗𝖊": "𝕰𝖒𝖕𝖎𝖗𝖊",
    "𝘐𝘵𝘢𝘭𝘪𝘤": "𝘐𝘵𝘢𝘭𝘪𝘤",
    "Ⱨł₮₥₳₦": "Ⱨł₮₥₳₦",
    "Ⓦⓗⓘⓣⓔ": "Ⓦⓗⓘⓣⓔ",
    "ℜ𝔢𝔤𝔞𝔩": "ℜ𝔢𝔤𝔞𝔩",
    "ＤｕｍＤｕｍ": "ＤｕｍＤｕｍ",
    "[̲̅E][̲̅d][̲̅w][̲̅a][̲̅r][̲̅d]": "[̲̅E][̲̅d][̲̅w][̲̅a][̲̅r][̲̅d]",
    "🅑🅛🅚🅑🅐🅛🅛": "🅑🅛🅚🅑🅐🅛🅛",
    "🅰🆂🅿🅴🅲🆃": "🅰🆂🅿🅴🅲🆃",
    "Ԃιαɳα": "Ԃιαɳα",
    "Çå§†lê": "Çå§†lê",
    "𝗕𝗼𝗹𝗱": "𝗕𝗼𝗹𝗱",
    "¢αяιту": "¢αяιту",
    "ᎷᎽᎿᎻᎾᏝᎾᎶᏽ": "ᎷᎽᎿᎻᎾᏝᎾᎶᏽ",
    "𝐓𝐍𝐘𝐁𝐎𝐋𝐃": "𝐓𝐍𝐘𝐁𝐎𝐋𝐃",
    "̶S̶t̶r̶i̶k̶e̶T̶H̶R̶O̶U̶G̶H": "̶S̶t̶r̶i̶k̶e̶T̶H̶R̶O̶U̶G̶H",
    "▀▄▀▄Greatwall ▄▀▄▀": "▀▄▀▄Greatwall ▄▀▄▀",
    ".•♫•♬•Senorita•♬•♫•.": ".•♫•♬•Senorita•♬•♫•.",
    "◦•●◉✿Text ✿◉●•◦": "◦•●◉✿Text ✿◉●•◦",
    "🇸 🇵 🇪 🇨 🇮 🇦 🇱": "🇸 🇵 🇪 🇨 🇮 🇦 🇱",
    "𝑺𝒆𝒓𝒊𝒇": "𝑺𝒆𝒓𝒊𝒇",
    "𝐒𝐞𝐫𝐢𝐟": "𝐒𝐞𝐫𝐢𝐟",
    "𝑆𝑒𝑟𝑖𝑓": "𝑆𝑒𝑟𝑖𝑓"
}

FONT_MAPPINGS = {
    "𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛": "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝙰𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣",
    "ꇙꌦꂵꃳꄲ꒒": "ꁲꃃꉓ꒯ꏂꊰꁅꀍꀤ꒻ꀘ꒒ꂵꋊꄲꉣꁷꋪꇙꋖ꒤꒦ꅐꇓ꒍ꁲꃃꉓ꒯ꏂꊰꁅꀍꀤ꒻ꀘ꒒ꂵꋊꄲꉣꁷꋪꇙꋖ꒤꒦ꅐꇓ꒍",
    "𝘽𝙊𝙇𝘿𝙄𝙏𝘼𝙇𝙄𝘾": "𝘽𝙊𝙇𝘿𝙄𝙏𝘼𝙇𝙄𝘾𝘽𝙊𝙇𝘿𝙄𝙏𝘼𝙇𝙄𝘾",
    "₵ʉɽɽɇ₦₵ɏ": "₳฿₵ĐɆ₣₲ⱧłJ₭Ⱡ₥₦Ø₱QⱤ₴₮ɄV₩ӾɎⱫₐ₿₵đₑ₣₲ₕᵢⱼ₭ₗₘₙₒₚqᵣ₴ₜᵤᵥ₩Ӿɏⱬ",
    "ℙ𝕣𝕖𝕞𝕚𝕦𝕞": "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫",
    "ᕼᗩᒪᗩᒪᗩ": "ᗩᗷᑕᗪᗴᖴᘜᕼᓮᒍᖽᐸᒪᗰᑎᓍᑭQᖇᔕ丅ᑌᐯᗯ᙭Ƴ乙ᗩᗷᑕᗪᗴᖴᘜᕼᓮᒍᖽᐸᒪᗰᑎᓍᑭQᖇᔕ丅ᑌᐯᗯ᙭Ƴ乙",
    "ɹǝʌǝɹsǝ": "ɐqɔpǝɟɓɥıɾʞlɯuodbɹsʇnʌʍxʎzɐqɔpǝɟɓɥıɾʞlɯuodbɹsʇnʌʍxʎz",
    "🄱🄾🅇": "🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉",
    "sᴍʟᴄᴀᴘ": "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘQʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘQʀsᴛᴜᴠᴡxʏᴢ",
    "𝕰𝖒𝖕𝖎𝖗𝖊": "𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟",
    "𝘐𝘵𝘢𝘭𝘪𝘤": "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻",
    "Ⱨł₮₥₳₦": "Ⱨł₮₥₳₦Ⱨł₮₥₳₦",
    "Ⓦⓗⓘⓣⓔ": "ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ",
    "ℜ𝔢𝔤𝔞𝔩": "ℜ𝔢𝔤𝔞𝔩ℜ𝔢𝔤𝔞𝔩",
    "ＤｕｍＤｕｍ": "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ",
    "[̲̅E][̲̅d][̲̅w][̲̅a][̲̅r][̲̅d]": "[̲̅A][̲̅B][̲̅C][̲̅D][̲̅E][̲̅F][̲̅G][̲̅H][̲̅I][̲̅J][̲̅K][̲̅L][̲̅M][̲̅N][̲̅O][̲̅P][̲̅Q][̲̅R][̲̅S][̲̅T][̲̅U][̲̅V][̲̅W][̲̅X][̲̅Y][̲̅Z][̲̅a][̲̅b][̲̅c][̲̅d][̲̅e][̲̅f][̲̅g][̲̅h][̲̅i][̲̅j][̲̅k][̲̅l][̲̅m][̲̅n][̲̅o][̲̅p][̲̅q][̲̅r][̲̅s][̲̅t][̲̅u][̲̅v][̲̅w][̲̅x][̲̅y][̲̅z]",
    "🅑🅛🅚🅑🅐🅛🅛": "🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅝🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅝🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩",
    "🅰🆂🅿🅴🅲🆃": "🅰🅱🅲🅳🅴🅵🅶🅷🅸🅹🅺🅻🅼🅽🅾🅿🆀🆁🆂🆃🆄🆅🆆🆇🆈🆉🅰🅱🅲🅳🅴🅵🅶🅷🅸🅹🅺🅻🅼🅽🅾🅿🆀🆁🆂🆃🆄🆅🆆🆇🆈🆉",
    "Ԃιαɳα": "αв¢∂єƒgнιנкℓмησρqяѕтυνωχуzαв¢∂єƒgнιנкℓмησρqяѕтυνωχуz",
    "Çå§†lê": "Çå§†lêÇå§†lê",
    "𝗕𝗼𝗹𝗱": "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇",
    "¢αяιту": "αв¢∂єƒgнιנкℓмησρqяѕтυνωχуzαв¢∂єƒgнιנкℓмησρqяѕтυνωχуz",
    "ᎷᎽᎿᎻᎾᏝᎾᎶᏽ": "ᎪᎳᏟᎠᎬᎱᎶᎻᎨᎫᏦᏞᎷᏁᎾᏢᏄᎡᏕᎿᏬᏙᏔᎲᎩᏃᎪᎳᏟᎠᎬᎱᎶᎻᎨᎫᏦᏞᎷᏁᎾᏢᏄᎡᏕᎿᏬᏙᏔᎲᎩᏃ",
    "𝐓𝐍𝐘𝐁𝐎𝐋𝐃": "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳",
    "̶S̶t̶r̶i̶k̶e̶T̶H̶R̶O̶U̶G̶H": "̶A̶B̶C̶D̶E̶F̶G̶H̶I̶J̶K̶L̶M̶N̶O̶P̶Q̶R̶S̶T̶U̶V̶W̶X̶Y̶Z̶a̶b̶c̶d̶e̶f̶g̶h̶i̶j̶k̶l̶m̶n̶o̶p̶q̶r̶s̶t̶u̶v̶w̶x̶y̶z",
    "▀▄▀▄Greatwall ▄▀▄▀": "▀▄▀▄A▄▀▄▀B▄▀▄▀C▄▀▄▀D▄▀▄▀E▄▀▄▀F▄▀▄▀G▄▀▄▀H▄▀▄▀I▄▀▄▀J▄▀▄▀K▄▀▄▀L▄▀▄▀M▄▀▄▀N▄▀▄▀O▄▀▄▀P▄▀▄▀Q▄▀▄▀R▄▀▄▀S▄▀▄▀T▄▀▄▀U▄▀▄▀V▄▀▄▀W▄▀▄▀X▄▀▄▀Y▄▀▄▀Z▄▀▄▀a▄▀▄▀b▄▀▄▀c▄▀▄▀d▄▀▄▀e▄▀▄▀f▄▀▄▀g▄▀▄▀h▄▀▄▀i▄▀▄▀j▄▀▄▀k▄▀▄▀l▄▀▄▀m▄▀▄▀n▄▀▄▀o▄▀▄▀p▄▀▄▀q▄▀▄▀r▄▀▄▀s▄▀▄▀t▄▀▄▀u▄▀▄▀v▄▀▄▀w▄▀▄▀x▄▀▄▀y▄▀▄▀z",
    ".•♫•♬•Senorita•♬•♫•.": ".•♫•♬•A•♬•♫•.•♫•♬•B•♬•♫•.•♫•♬•C•♬•♫•.•♫•♬•D•♬•♫•.•♫•♬•E•♬•♫•.•♫•♬•F•♬•♫•.•♫•♬•G•♬•♫•.•♫•♬•H•♬•♫•.•♫•♬•I•♬•♫•.•♫•♬•J•♬•♫•.•♫•♬•K•♬•♫•.•♫•♬•L•♬•♫•.•♫•♬•M•♬•♫•.•♫•♬•N•♬•♫•.•♫•♬•O•♬•♫•.•♫•♬•P•♬•♫•.•♫•♬•Q•♬•♫•.•♫•♬•R•♬•♫•.•♫•♬•S•♬•♫•.•♫•♬•T•♬•♫•.•♫•♬•U•♬•♫•.•♫•♬•V•♬•♫•.•♫•♬•W•♬•♫•.•♫•♬•X•♬•♫•.•♫•♬•Y•♬•♫•.•♫•♬•Z•♬•♫•.•♫•♬•a•♬•♫•.•♫•♬•b•♬•♫•.•♫•♬•c•♬•♫•.•♫•♬•d•♬•♫•.•♫•♬•e•♬•♫•.•♫•♬•f•♬•♫•.•♫•♬•g•♬•♫•.•♫•♬•h•♬•♫•.•♫•♬•i•♬•♫•.•♫•♬•j•♬•♫•.•♫•♬•k•♬•♫•.•♫•♬•l•♬•♫•.•♫•♬•m•♬•♫•.•♫•♬•n•♬•♫•.•♫•♬•o•♬•♫•.•♫•♬•p•♬•♫•.•♫•♬•q•♬•♫•.•♫•♬•r•♬•♫•.•♫•♬•s•♬•♫•.•♫•♬•t•♬•♫•.•♫•♬•u•♬•♫•.•♫•♬•v•♬•♫•.•♫•♬•w•♬•♫•.•♫•♬•x•♬•♫•.•♫•♬•y•♬•♫•.•♫•♬•z•♬•♫•.",
    "◦•●◉✿Text ✿◉●•◦": "◦•●◉✿A✿◉●•◦◦•●◉✿B✿◉●•◦◦•●◉✿C✿◉●•◦◦•●◉✿D✿◉●•◦◦•●◉✿E✿◉●•◦◦•●◉✿F✿◉●•◦◦•●◉✿G✿◉●•◦◦•●◉✿H✿◉●•◦◦•●◉✿I✿◉●•◦◦•●◉✿J✿◉●•◦◦•●◉✿K✿◉●•◦◦•●◉✿L✿◉●•◦◦•●◉✿M✿◉●•◦◦•●◉✿N✿◉●•◦◦•●◉✿O✿◉●•◦◦•●◉✿P✿◉●•◦◦•●◉✿Q✿◉●•◦◦•●◉✿R✿◉●•◦◦•●◉✿S✿◉●•◦◦•●◉✿T✿◉●•◦◦•●◉✿U✿◉●•◦◦•●◉✿V✿◉●•◦◦•●◉✿W✿◉●•◦◦•●◉✿X✿◉●•◦◦•●◉✿Y✿◉●•◦◦•●◉✿Z✿◉●•◦◦•●◉✿a✿◉●•◦◦•●◉✿b✿◉●•◦◦•●◉✿c✿◉●•◦◦•●◉✿d✿◉●•◦◦•●◉✿e✿◉●•◦◦•●◉✿f✿◉●•◦◦•●◉✿g✿◉●•◦◦•●◉✿h✿◉●•◦◦•●◉✿i✿◉●•◦◦•●◉✿j✿◉●•◦◦•●◉✿k✿◉●•◦◦•●◉✿l✿◉●•◦◦•●◉✿m✿◉●•◦◦•●◉✿n✿◉●•◦◦•●◉✿o✿◉●•◦◦•●◉✿p✿◉●•◦◦•●◉✿q✿◉●•◦◦•●◉✿r✿◉●•◦◦•●◉✿s✿◉●•◦◦•●◉✿t✿◉●•◦◦•●◉✿u✿◉●•◦◦•●◉✿v✿◉●•◦◦•●◉✿w✿◉●•◦◦•●◉✿x✿◉●•◦◦•●◉✿y✿◉●•◦◦•●◉✿z✿◉●•◦",
    "🇸 🇵 🇪 🇨 🇮 🇦 🇱": "🇦 🇧 🇨 🇩 🇪 🇫 🇬 🇭 🇮 🇯 🇰 🇱 🇲 🇳 🇴 🇵 🇶 🇷 🇸 🇹 🇺 🇻 🇼 🇽 🇾 🇿 🇦 🇧 🇨 🇩 🇪 🇫 🇬 🇭 🇮 🇯 🇰 🇱 🇲 🇳 🇴 🇵 🇶 🇷 🇸 🇹 🇺 🇻 🇼 🇽 🇾 🇿",
    "𝑺𝒆𝒓𝒊𝒇": "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛",
    "𝐒𝐞𝐫𝐢𝐟": "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳",
    "𝑆𝑒𝑟𝑖𝑓": "𝑆𝑒𝑟𝑖𝑓𝑆𝑒𝑟𝑖𝑓"
}

def transform_text(text, font_key):
    base_alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    font_alpha = FONT_MAPPINGS.get(font_key, base_alpha)
    if len(font_alpha) < 52:  # Handle decorative fonts
        return font_key.replace("Text", text) if "Text" in font_key else text
    mapping = str.maketrans(base_alpha, font_alpha)
    return text.translate(mapping)

async def fonts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not context.args:
        await message.reply_text("Please provide a message to style! E.g., /fonts Hello")
        return
    text = " ".join(context.args)
    context.user_data["font_text"] = text  # Store the text in user_data
    await show_font_page(update, context, text, page=0)  # Start at page 0

async def show_font_page(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, page: int) -> None:
    font_keys = list(FONTS.keys())
    per_page = 12
    total_pages = (len(font_keys) + per_page - 1) // per_page
    page = max(0, min(page, total_pages - 1))  # Clamp page number
    start_idx = page * per_page
    end_idx = min(start_idx + per_page, len(font_keys))

    keyboard = []
    for i in range(start_idx, end_idx, 3):
        row = [
            InlineKeyboardButton(font_keys[j], callback_data=f"font_{font_keys[j]}_{text}")
            for j in range(i, min(i + 3, end_idx))
        ]
        keyboard.append(row)

    # Navigation buttons
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("◀ Back", callback_data=f"font_page_{page-1}_{text}"))
    else:
        nav_row.append(InlineKeyboardButton("◀", callback_data="noop"))
    nav_row.append(InlineKeyboardButton("❌ Close", callback_data="font_close"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("Forward ▶", callback_data=f"font_page_{page+1}_{text}"))
    else:
        nav_row.append(InlineKeyboardButton("▶", callback_data="noop"))
    keyboard.append(nav_row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    msg_text = f"🖋️ Select a font to style: *{text}*\nPage {page + 1}/{total_pages}"
    if update.callback_query:
        await update.callback_query.edit_message_text(msg_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(msg_text, reply_markup=reply_markup, parse_mode="Markdown")

async def font_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data

    if data == "font_close":
        await query.message.delete()
        await query.answer()
        return

    if data.startswith("font_page_"):
        parts = data.split("_", 3)
        page = int(parts[2])
        text = parts[3]
        await show_font_page(update, context, text, page)
        await query.answer()
        return

    if not data.startswith("font_"):
        await query.answer()
        return

    parts = data.split("_", 2)
    font_type = parts[1]
    original_text = parts[2] if len(parts) > 2 else context.user_data.get("font_text", "No text provided")

    # Check if this font was already applied
    last_font = context.user_data.get("last_font_applied", None)
    if last_font == font_type:
        await query.answer("This font is already applied! Copy it or pick another.", show_alert=True)
        return

    converted_text = transform_text(original_text, font_type)

    keyboard = [
        [InlineKeyboardButton("📋 Tap to Copy", switch_inline_query=converted_text)],
        [InlineKeyboardButton("⬅️ Back", callback_data=f"font_page_0_{original_text}"),
         InlineKeyboardButton("❌ Close", callback_data="font_close")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    new_text = f"Converted text:\n`{converted_text}`\n\nTap  TAP ON ABOVE TEXT TO COPY OR FOR SENDING IT TO ANYONE THEN 'Tap to Copy' to copy to your clipboard!"
    
    try:
        await query.edit_message_text(
            text=new_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        context.user_data["last_font_applied"] = font_type
    except telegram.error.BadRequest as e:
        if "Message is not modified" in str(e):
            await query.answer("No change detected! Pick a different font.", show_alert=True)
        else:
            logger.error(f"Unexpected BadRequest error: {e}")
            await query.answer("Something went wrong. Try again!", show_alert=True)
    await query.answer()

# Optional: Keep /paste if you want it, but it's less needed now
async def paste_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    clipboard_text = context.user_data.get("clipboard", None)
    if clipboard_text:
        await update.message.reply_text(
            f"Here’s your copied text:\n`{clipboard_text}`",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("Nothing in the clipboard! Use /fonts and copy some text first.")

# --- Filter Command ---
async def filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.message

    if chat.type not in ["group", "supergroup"]:
        await message.reply_text("This command can only be used in groups! 👥")
        return

    if not message.reply_to_message:
        await message.reply_text("Please reply to a message to set it as the filter response!")
        return

    if not context.args:
        await message.reply_text("Please provide a trigger word! E.g., /filter yoo")
        return

    trigger = context.args[0].lower()
    reply_message = message.reply_to_message

    if reply_message.text:
        response = reply_message.text
    elif reply_message.caption:
        response = reply_message.caption
    elif reply_message.sticker:
        response = f"Sticker: {reply_message.sticker.file_id}"
    elif reply_message.animation:
        response = f"GIF: {reply_message.animation.file_id}"
    else:
        response = "Media message"

    filters_collection = get_filters_collection()
    filters_collection.update_one(
        {"chat_id": chat.id, "trigger": trigger},
        {"$set": {"response": response}},
        upsert=True
    )

    await message.reply_text(f"Filter set! Whenever someone says '{trigger}', I’ll respond with the replied message.")

# --- Stop Command for Filters ---
async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    chat = update.effective_chat
    if not context.args:
        try:
            await message.reply_text("Please provide a filter trigger to stop (e.g., /stop hello)!")
        except telegram.error.BadRequest:
            await context.bot.send_message(chat_id=chat.id, text="Please provide a filter trigger to stop (e.g., /stop hello)!")
        return
    
    trigger = context.args[0].lower()
    db = get_db()
    filters_collection = db.get_collection('filters')
    
    result = filters_collection.delete_one({'chat_id': str(chat.id), 'trigger': trigger})
    if result.deleted_count > 0:
        try:
            await message.reply_text(f"Filter for '{trigger}' has been removed.")
        except telegram.error.BadRequest:
            await context.bot.send_message(chat_id=chat.id, text=f"Filter for '{trigger}' has been removed.")
    else:
        try:
            await message.reply_text(f"No filter found for '{trigger}' in this chat.")
        except telegram.error.BadRequest:
            await context.bot.send_message(chat_id=chat.id, text=f"No filter found for '{trigger}' in this chat.")

# --- Filter List Command ---
async def filterlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.message

    if chat.type not in ["group", "supergroup"]:
        await message.reply_text("This command can only be used in groups! 👥")
        return

    filters_collection = get_filters_collection()
    filters = list(filters_collection.find({"chat_id": chat.id}))

    if not filters:
        await message.reply_text("No filters are set in this group.")
        return

    filter_list = "📌 Active Filters:\n\n"
    for i, filter_doc in enumerate(filters, 1):
        filter_list += f"{i}. Trigger: `{filter_doc['trigger']}`\n   Response: {filter_doc['response']}\n\n"

    await message.reply_text(filter_list, parse_mode="Markdown")

# --- Handle Filters ---
async def handle_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.message
    if chat is None or message is None:
        logger.info("No chat or message, skipping.")
        return

    if chat.type not in ["group", "supergroup"]:
        logger.info(f"Chat {chat.id} is not a group, skipping.")
        return

    content = ""
    if message.text:
        content = message.text.lower()
    elif message.caption:
        content = message.caption.lower()
    elif message.sticker and message.sticker.emoji:
        content = message.sticker.emoji.lower()
    elif message.animation:
        content = "gif"

    if not content:
        logger.info("No relevant content, skipping.")
        return

    filters_collection = get_filters_collection()
    filters = list(filters_collection.find({"chat_id": chat.id}))
    logger.info(f"Found {len(filters)} filters for chat {chat.id}: {[f['trigger'] for f in filters]}")

    for filter_doc in filters:
        trigger = filter_doc["trigger"]
        logger.info(f"Checking trigger '{trigger}' against content '{content}'")
        if trigger in content:
            response = filter_doc["response"]
            logger.info(f"Trigger '{trigger}' matched, responding with: {response}")
            if "Sticker:" in response:
                await message.reply_sticker(response.split("Sticker: ")[1])
            elif "GIF:" in response:
                await message.reply_animation(response.split("GIF: ")[1])
            else:
                await message.reply_text(response)
    # No unnecessary replies if no filters match