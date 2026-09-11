import os
import html
import json
import time
import logging
import asyncio
from pathlib import Path

import requests

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.constants import ChatType

from telegram.error import (
    Forbidden,
    BadRequest,
    RetryAfter,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# =========================================================
# LOG
# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# =========================================================
# CONFIG
# =========================================================

# Ưu tiên lấy từ biến môi trường BOT_TOKEN, nếu không có sẽ dùng Token cấu hình trực tiếp
TOKEN = os.getenv("BOT_TOKEN", "8745510750:AAHL7q-_s7PpuQBdwgq3mq-vd-M7h7WDGmE")

FF_API = "https://infohh.vercel.app/get"

TIKTOK_API = (
    "https://socialmediainfo-nu.vercel.app/riduan/tiktok"
)

ADMIN_IDS = {
    8758651209,
    8381760044,
}

ADMIN_ZALO = "https://zalo.me/0363400399"
ADMIN_TELEGRAM = "https://t.me/baoarariul"
WEB_SHOP = "https://shopbaoara.lovable.app"

BOX_BUFF_LIKE = "https://t.me/bao_ara_buff_like"
KENH_THAM_GIA = "https://t.me/bao_ara_riu"

USERS_FILE = Path("users.json")

users = {}

# admin_id -> group_id
pending_group_broadcast = {}


# =========================================================
# USERS
# =========================================================

def load_users():
    if not USERS_FILE.exists():
        return {}

    try:
        data = json.loads(
            USERS_FILE.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(data, dict):
            return data

    except Exception as e:
        logger.warning(
            "Không đọc được users.json: %s",
            e
        )

    return {}


users = load_users()


def save_users():
    try:
        temp_file = USERS_FILE.with_suffix(".tmp")

        temp_file.write_text(
            json.dumps(
                users,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        temp_file.replace(USERS_FILE)

    except Exception as e:
        logger.error(
            "Không lưu được users.json: %s",
            e
        )


async def remember_user(update: Update):
    user = update.effective_user
    chat = update.effective_chat

    if not user or not chat:
        return

    if chat.type != ChatType.PRIVATE:
        return

    uid = str(user.id)

    users[uid] = {
        "id": user.id,
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "username": user.username or "",
        "last_seen": int(time.time()),
        "active": True,
    }

    save_users()


def is_admin(user_id):
    return user_id in ADMIN_IDS


# =========================================================
# PRICE
# =========================================================

LIKE_PRICE = """
┌── 📊 BẢNG GIÁ BUFF LIKE ───
│
├─ 🎮 GÓI 100 LIKES / NGÀY
│  • 1k Likes  ➔ 29K
│  • 2k Likes  ➔ 49K
│  • 3k Likes  ➔ 59K
│  • 5k Likes  ➔ 99K
│  • 10k Likes ➔ 179K
│  • 20k Likes ➔ 349K
│  • 30k Likes ➔ 528K
│  • 40k Likes ➔ 698K
│  • 50k Likes ➔ 877K
│
├─ 🎮 GÓI 200 LIKES / NGÀY
│  • 1k Likes  ➔ 49K
│  • 2k Likes  ➔ 79K
│  • 3k Likes  ➔ 99K
│  • 5k Likes  ➔ 159K
│  • 10k Likes ➔ 249K
│  • 20k Likes ➔ 419K
│  • 30k Likes ➔ 668K
│  • 40k Likes ➔ 838K
│  • 50k Likes ➔ 1.087K
│
├─ 🎮 GÓI 220 LIKES / NGÀY
│  • 1k Likes  ➔ 55K
│  • 2k Likes  ➔ 89K
│  • 3k Likes  ➔ 115K
│  • 5k Likes  ➔ 179K
│  • 10k Likes ➔ 285K
│  • 20k Likes ➔ 479K
│  • 30k Likes ➔ 769K
│  • 40k Likes ➔ 969K
│  • 50k Likes ➔ 1.257K
│
├─ 🎮 GÓI 500 LIKES / NGÀY
│  • 1k Likes  ➔ 59K
│  • 2k Likes  ➔ 99K
│  • 3k Likes  ➔ 139K
│  • 5k Likes  ➔ 199K
│  • 10k Likes ➔ 319K
│  • 20k Likes ➔ 519K
│  • 30k Likes ➔ 838K
│  • 40k Likes ➔ 1.038K
│  • 50k Likes ➔ 1.357K
│
└─ 🎮 GÓI 1000 LIKES / NGÀY
   • 1k Likes  ➔ 99K
   • 2k Likes  ➔ 179K
   • 3k Likes  ➔ 239K
   • 5k Likes  ➔ 379K
   • 10k Likes ➔ 719K
   • 20k Likes ➔ 1.400K
   • 30k Likes ➔ 2.119K
   • 40k Likes ➔ 2.800K
   • 50k Likes ➔ 3.519K

──────────────────────
🎯 Càng ủng hộ nhiều = Ưu đãi càng lớn!
"""


BOT_PRICE = """
┌── 🎮 BOT GAME FREE FIRE ───
├── 👑 1 Ngày   ➔ 29K
├── 👑 3 Ngày   ➔ 79K
├── 👑 7 Ngày   ➔ 149K
├── 👑 15 Ngày  ➔ 249K
└── 👑 30 Ngày  ➔ 479K

✨─────────────────────✨

┌── ⚙️ CHỨC NĂNG NỔI BẬT ───
├── ⚡ BUFF LIKE 100-200 Like/Ngày
├── 🔫 MÚA HÀNH ĐỘNG S7
├── 📱 LẬP TEAM 5
├── 🎵 NGHE NHẠC 24/7
└── 🚀 CÙNG NHIỀU TÍNH NĂNG KHÁC...
"""


GENPLAY = """
┌── 📱 BẢNG GIÁ CODE GENPLAY ───

├─ ⚡ CODE GENPLAY 835
│
│ • 1 Ngày   ➔ 20K
│ • 7 Ngày   ➔ 45K
│ • 15 Ngày  ➔ 90K
│ • 30 Ngày  ➔ 150K
│ • 90 Ngày  ➔ 390K
│ • 180 Ngày ➔ 650K
│ • 360 Ngày ➔ 1M3
│
└─ ⚡ CODE GENPLAY 845
│
│ • 1 Ngày   ➔ 26K
│ • 7 Ngày   ➔ 70K
│ • 15 Ngày  ➔ 150K
│ • 30 Ngày  ➔ 300K
│ • 90 Ngày  ➔ 470K
│ • 180 Ngày ➔ 950K
│ • 360 Ngày ➔ 1M850

──────────────────────
🎯 Tối ưu hiệu năng Game!
"""


QUAN_DOAN = """
┌── 🤖 DỊCH VỤ BOT QUÂN ĐOÀN ───

👋 Xin chào, mình là BẢO ARA!

🎮 Chuyên cung cấp dịch vụ Bot
tăng điểm bang hội Free Fire.

├─ 📊 SERVER VN
│
├─ 💰 Tiền mặt: 170K / tuần
├─ 🎫 Thẻ: 200K Garena
├─ 👥 Cài đặt: 4 tài khoản
└─ 📈 Khoảng 400K - 500K điểm/tuần

├─ ⏱️ TRIỂN KHAI
│
└─ Bot được thêm sau 04:00 sáng
   Thứ Hai hàng tuần.

──────────────────────
📞 Liên hệ Admin để đăng ký.
"""


CHECK_MXT = """
🛡️ BẢNG GIÁ CHECKMXT.COM
──────────────────────

🔹 1. Check MXT & LK

• Theo lần: 49.000đ
• Vĩnh viễn: 299.000đ

🔹 2. Gỡ & Gắn MXT

• Theo lần: 299.000đ
• Vĩnh viễn: 699.000đ

🔹 3. Chặn Mã Xác Thực

• Theo lần: 199.000đ
• Vĩnh viễn: 749.000đ

🔹 4. Dò Mã Bảo Mật

• Vĩnh viễn: 399.000đ

🔹 5. Ban 7 Ngày

• Theo lần: 79.000đ
• Vĩnh viễn: 699.000đ

──────────────────────
🤝 HỖ TRỢ 24/7
"""


# =========================================================
# KEYBOARD
# =========================================================

def main_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📊 Giá Likes",
                callback_data="likes_price"
            ),
            InlineKeyboardButton(
                "🎮 Thuê Bot",
                callback_data="bot_price"
            ),
        ],
        [
            InlineKeyboardButton(
                "📱 Giá GenPlay",
                callback_data="genplay"
            ),
            InlineKeyboardButton(
                "🤖 Bot Quân Đoàn",
                callback_data="quan_doan"
            ),
        ],
        [
            InlineKeyboardButton(
                "🎯 Check Acc FF",
                callback_data="check_ff"
            ),
            InlineKeyboardButton(
                "🛡️ CheckMXT",
                callback_data="check_mxt"
            ),
        ],
        [
            InlineKeyboardButton(
                "💬 Zalo Admin",
                url=ADMIN_ZALO
            ),
            InlineKeyboardButton(
                "📞 Telegram",
                url=ADMIN_TELEGRAM
            ),
        ],
        [
            InlineKeyboardButton(
                "🌐 Web Shop",
                url=WEB_SHOP
            ),
        ],
    ])


def back_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔙 Quay lại",
                callback_data="back"
            )
        ]
    ])


# =========================================================
# START
# =========================================================

START_TEXT = """
<b>┌─────────────────────────────────────┐
│       🧸 SHOP BẢO ARA 🧸
├─────────────────────────────────────┤
│ 🎮 Dịch vụ Free Fire
│ ⚡ Buff Like
│ 📱 GenPlay
│ 🤖 Bot Quân Đoàn
│ 🛡️ Check dịch vụ
│
│ 👑 Admin: @baoarariul
│ 💬 Zalo: 0363400399
└─────────────────────────────────────┘</b>

👇 <b>Chọn chức năng bên dưới</b>
"""


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await remember_user(update)

    if not update.message:
        return

    await update.message.reply_text(
        START_TEXT,
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )


# =========================================================
# HELP
# =========================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await remember_user(update)

    text = (
        "<b>HƯỚNG DẪN SHOP BẢO ARA 🧸</b>\n\n"

        "🎮 <code>/ff UID</code>\n"
        "→ Xem thông tin Free Fire\n\n"

        "😶 <code>/tt username</code>\n"
        "→ Xem thông tin TikTok\n\n"

        "👍🏻 <code>/likes</code>\n"
        "→ Thông tin Buff Likes\n\n"

        "🏡 <code>/start</code>\n"
        "→ Mở menu chính\n\n"

        "🔰 <code>/help</code>\n"
        "→ Xem hướng dẫn"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )


# =========================================================
# ADMIN HELP
# =========================================================

async def amin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    if not user or not is_admin(user.id):
        return

    text = """
🔐 <b>HƯỚNG DẪN ADMIN</b>

👑 /amin
→ Mở bảng điều khiển Admin

📢 /tb Nội dung
→ Broadcast đến user đã tương tác

📨 /ara ID_NHÓM
→ Chọn nhóm để gửi tin

❌ /cancel
→ Hủy /ara

👥 /users
→ Xem số user bot đã lưu

⚠️ Chỉ Admin mới dùng được.
"""

    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )


# =========================================================
# LIKES
# =========================================================

async def likes_cmd(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await remember_user(update)

    text = (
        "<b>❤️ BUFF LIKES SHOP BẢO ARA</b>\n\n"
        f"📦 Box Buff Likes:\n"
        f"{BOX_BUFF_LIKE}\n\n"
        f"📢 Kênh tham gia:\n"
        f"{KENH_THAM_GIA}"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )


# =========================================================
# FREE FIRE
# =========================================================

def check_freefire(uid):

    try:

        response = requests.get(
            FF_API,
            params={
                "uid": uid
            },
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=15
        )

        if response.status_code != 200:
            return None, (
                f"Lỗi HTTP {response.status_code}"
            )

        try:
            data = response.json()

        except ValueError:
            return None, (
                "API không trả JSON hợp lệ."
            )

        return data, None

    except requests.Timeout:
        return None, (
            "API Free Fire phản hồi quá lâu."
        )

    except requests.RequestException as e:
        return None, (
            f"Lỗi kết nối API: {e}"
        )

    except Exception as e:
        return None, (
            f"Lỗi API: {e}"
        )


def safe_extract(data):

    if not isinstance(data, dict):
        return {}

    result = {}

    def walk(obj):

        if isinstance(obj, dict):

            for key, value in obj.items():

                key = str(key).lower()

                if isinstance(
                    value,
                    (dict, list)
                ):
                    walk(value)

                else:
                    result[key] = value

        elif isinstance(obj, list):

            for item in obj:
                walk(item)

    walk(data)

    return result


def get_field(
    flat_data,
    keywords,
    default="Không rõ"
):

    for keyword in keywords:

        keyword = keyword.lower()

        for key, value in flat_data.items():

            if keyword in key:

                if value is not None:

                    value = str(value).strip()

                    if value:
                        return value

    return default


async def do_ff_lookup(
    message,
    uid
):

    loading = await message.reply_text(
        "⌛ Đang tra cứu FF "
        f"<code>{html.escape(uid)}</code>...",
        parse_mode="HTML"
    )

    data, error = await asyncio.to_thread(
        check_freefire,
        uid
    )

    try:
        await loading.delete()

    except Exception:
        pass

    if error or not data:

        await message.reply_text(
            "❌ <b>KHÔNG THỂ TRA CỨU</b>\n\n"
            f"{html.escape(error or 'API không có dữ liệu')}",
            parse_mode="HTML"
        )

        return

    flat = safe_extract(data)

    name = get_field(
        flat,
        [
            "nickname",
            "name",
            "player",
            "ten"
        ]
    )

    level = get_field(
        flat,
        [
            "level",
            "lvl",
            "accountlevel"
        ]
    )

    likes = get_field(
        flat,
        [
            "likes",
            "like",
            "accountlikes"
        ]
    )

    exp = get_field(
        flat,
        [
            "exp",
            "experience",
            "account_exp"
        ]
    )

    region = get_field(
        flat,
        [
            "region",
            "server",
            "zone",
            "khuvuc"
        ]
    )

    created = get_field(
        flat,
        [
            "createtime",
            "created",
            "create",
            "ngaytao"
        ]
    )

    last_login = get_field(
        flat,
        [
            "lastlogin",
            "last_login",
            "login"
        ]
    )

    bio = get_field(
        flat,
        [
            "bio",
            "signature",
            "tieusu"
        ],
        "Không có"
    )

    result = f"""
<b>THÔNG TIN TÀI KHOẢN FREE FIRE</b>
━━━━━━━━━━━━━━━━━━━━━

👤 Tên:
<b>{html.escape(name)}</b>

🆔 ID:
<code>{html.escape(uid)}</code>

🧸 Level:
<b>{html.escape(level)}</b>

👍🏻 Like:
<b>{html.escape(likes)}</b>

📈 EXP:
<b>{html.escape(exp)}</b>

🌍 Khu vực:
<b>{html.escape(region)}</b>

📅 Ngày tạo acc:
<b>{html.escape(created)}</b>

🕒 Lần cuối đăng nhập:
<b>{html.escape(last_login)}</b>

📝 Tiểu sử:
<i>{html.escape(bio)}</i>

━━━━━━━━━━━━━━━━━
<b>tele @baoarariul</b>
"""

    await message.reply_text(
        result,
        parse_mode="HTML"
    )


async def ff(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await remember_user(update)

    if not update.message:
        return

    if (
        not context.args
        or not context.args[0].isdigit()
    ):

        await update.message.reply_text(
            "❌ <b>Vui lòng nhập đúng UID!</b>\n\n"
            "Ví dụ:\n"
            "<code>/ff 12345678</code>",
            parse_mode="HTML"
        )

        return

    await do_ff_lookup(
        update.message,
        context.args[0]
    )


# =========================================================
# TIKTOK
# =========================================================

def check_tiktok(username):

    username = username.lstrip("@").strip()

    if not username:
        return None, (
            "Thiếu username TikTok."
        )

    try:

        response = requests.get(
            TIKTOK_API,
            params={
                "username": username
            },
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=20
        )

        if response.status_code != 200:
            return None, (
                f"Lỗi HTTP {response.status_code}"
            )

        try:
            data = response.json()

        except ValueError:
            return None, (
                "API TikTok không trả JSON."
            )

        return data, None

    except requests.Timeout:
        return None, (
            "API TikTok phản hồi quá lâu."
        )

    except requests.RequestException as e:
        return None, (
            f"Lỗi kết nối: {e}"
        )

    except Exception as e:
        return None, str(e)


def find_value(
    obj,
    keys
):

    if isinstance(obj, dict):

        # Tìm không phân biệt hoa thường
        lowered = {
            str(k).lower(): v
            for k, v in obj.items()
        }

        for key in keys:

            value = lowered.get(
                str(key).lower()
            )

            if value is not None and value != "":
                return value

        for value in obj.values():

            result = find_value(
                value,
                keys
            )

            if result is not None:
                return result

    elif isinstance(obj, list):

        for item in obj:

            result = find_value(
                item,
                keys
            )

            if result is not None:
                return result

    return None


async def tt(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await remember_user(update)

    if not update.message:
        return

    if not context.args:

        await update.message.reply_text(
            "❌ Nhập username TikTok.\n\n"
            "Ví dụ:\n"
            "<code>/tt @username</code>",
            parse_mode="HTML"
        )

        return

    username = context.args[0].strip()

    loading = await update.message.reply_text(
        "⌛ Đang lấy thông tin TikTok "
        f"<b>{html.escape(username)}</b>...",
        parse_mode="HTML"
    )

    data, error = await asyncio.to_thread(
        check_tiktok,
        username
    )

    try:
        await loading.delete()

    except Exception:
        pass

    if error or not data:

        await update.message.reply_text(
            "❌ <b>KHÔNG THỂ LẤY THÔNG TIN</b>\n\n"
            f"{html.escape(error or 'Không có dữ liệu')}",
            parse_mode="HTML"
        )

        return

    nickname = find_value(
        data,
        [
            "nickname",
            "nickName",
            "name"
        ]
    ) or "Không rõ"

    user_name = find_value(
        data,
        [
            "username",
            "unique_id",
            "uniqueId"
        ]
    ) or username.lstrip("@")

    user_id = find_value(
        data,
        [
            "user_id",
            "userId",
            "id"
        ]
    ) or "Không rõ"

    followers = find_value(
        data,
        [
            "followers",
            "follower_count",
            "followerCount"
        ]
    ) or "0"

    following = find_value(
        data,
        [
            "following",
            "following_count",
            "followingCount"
        ]
    ) or "0"

    likes = find_value(
        data,
        [
            "likes",
            "heart_count",
            "heartCount"
        ]
    ) or "0"

    videos = find_value(
        data,
        [
            "total_videos",
            "video_count",
            "videoCount"
        ]
    ) or "0"

    bio = find_value(
        data,
        [
            "bio",
            "signature"
        ]
    ) or "Không có"

    avatar = find_value(
        data,
        [
            "avatar",
            "avatar_url",
            "avatarLarger",
            "avatarMedium",
            "avatarThumb",
            "avatar_url_100"
        ]
    )

    result = f"""
<b>THÔNG TIN TÀI KHOẢN TIKTOK</b>
━━━━━━━━━━━━━━━━━━━━

👤 Tên:
<b>{html.escape(str(nickname))}</b>

🗿 Username:
<b>@{html.escape(str(user_name).lstrip('@'))}</b>

🆔 User ID:
<code>{html.escape(str(user_id))}</code>

👥 Followers:
<b>{html.escape(str(followers))}</b>

➕ Following:
<b>{html.escape(str(following))}</b>

❤️ Likes:
<b>{html.escape(str(likes))}</b>

🎬 Video:
<b>{html.escape(str(videos))}</b>

📝 Tiểu sử:
<i>{html.escape(str(bio))}</i>

━━━━━━━━━━━━━━━━━━━━
<b>Shop Bảo Ara 🧸</b>
📞 @baoarariul
"""

    if avatar:

        try:

            await update.message.reply_photo(
                photo=str(avatar),
                caption=result,
                parse_mode="HTML"
            )

            return

        except Exception as e:

            logger.warning(
                "Không gửi được avatar TikTok: %s",
                e
            )

    await update.message.reply_text(
        result,
        parse_mode="HTML"
    )


# =========================================================
# CALLBACK BUTTON
# =========================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if not query:
        return

    try:
        await query.answer()
    except Exception:
        pass

    data = query.data

    if data == "back":

        await query.edit_message_text(
            START_TEXT,
            reply_markup=main_keyboard(),
            parse_mode="HTML"
        )

    elif data == "likes_price":

        await query.edit_message_text(
            LIKE_PRICE,
            reply_markup=back_keyboard()
        )

    elif data == "bot_price":

        await query.edit_message_text(
            BOT_PRICE,
            reply_markup=back_keyboard()
        )

    elif data == "genplay":

        await query.edit_message_text(
            GENPLAY,
            reply_markup=back_keyboard()
        )

    elif data == "quan_doan":

        await query.edit_message_text(
            QUAN_DOAN,
            reply_markup=back_keyboard()
        )

    elif data == "check_mxt":

        await query.edit_message_text(
            CHECK_MXT,
            reply_markup=back_keyboard()
        )

    elif data == "check_ff":

        await query.edit_message_text(
            "🎮 <b>CHECK FREE FIRE</b>\n\n"
            "Gửi UID bằng lệnh:\n"
            "<code>/ff 12345678</code>\n\n"
            "Ví dụ:\n"
            "<code>/ff 8753272865</code>",
            reply_markup=back_keyboard(),
            parse_mode="HTML"
        )


# =========================================================
# ADMIN /TB
# =========================================================

async def tb(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    if not user or not is_admin(user.id):
        return

    if not update.message:
        return

    if not context.args:

        await update.message.reply_text(
            "❌ Dùng:\n"
            "<code>/tb Nội dung cần gửi</code>",
            parse_mode="HTML"
        )

        return

    content = " ".join(context.args)

    broadcast_text = (
        "🧸 <b>THÔNG BÁO TỪ ADMIN</b> 🧸\n\n"
        f"📢 {html.escape(content)}\n\n"
        "━━━━━━━━━━━━━━\n"
        "💌 Shop Bảo Ara"
    )

    sent = 0
    failed = 0

    user_ids = list(users.keys())

    status = await update.message.reply_text(
        f"📢 Bắt đầu gửi đến "
        f"<b>{len(user_ids)}</b> user...",
        parse_mode="HTML"
    )

    for uid in user_ids:

        try:

            await context.bot.send_message(
                chat_id=int(uid),
                text=broadcast_text,
                parse_mode="HTML",
                disable_web_page_preview=True
            )

            sent += 1

            await asyncio.sleep(0.05)

        except RetryAfter as e:

            await asyncio.sleep(
                float(e.retry_after)
            )

            try:

                await context.bot.send_message(
                    chat_id=int(uid),
                    text=broadcast_text,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )

                sent += 1

            except Exception:
                failed += 1

        except (
            Forbidden,
            BadRequest
        ):

            failed += 1

            if uid in users:
                users[uid]["active"] = False

        except Exception as e:

            failed += 1

            logger.warning(
                "TB lỗi %s: %s",
                uid,
                e
            )

    save_users()

    try:
        await status.edit_text(
            "✅ <b>BROADCAST HOÀN TẤT</b>\n\n"
            f"📨 Thành công: <b>{sent}</b>\n"
            f"❌ Thất bại: <b>{failed}</b>",
            parse_mode="HTML"
        )

    except Exception:
        pass


# =========================================================
# ADMIN /ARA
# =========================================================

async def ara(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    if not user or not is_admin(user.id):
        return

    if not update.message:
        return

    if not context.args:

        await update.message.reply_text(
            "❌ Dùng:\n"
            "<code>/ara -1001234567890</code>",
            parse_mode="HTML"
        )

        return

    group_id_text = context.args[0]

    try:
        group_id = int(group_id_text)

    except ValueError:

        await update.message.reply_text(
            "❌ ID nhóm không hợp lệ.",
            parse_mode="HTML"
        )

        return

    pending_group_broadcast[user.id] = group_id

    await update.message.reply_text(
        "📨 <b>ĐÃ CHỌN NHÓM</b>\n\n"
        f"🆔 Group ID: <code>{group_id}</code>\n\n"
        "👉 Bây giờ gửi <b>một tin nhắn thường</b> "
        "ở chat riêng với bot.\n\n"
        "Tin nhắn đó sẽ được gửi vào nhóm.\n\n"
        "❌ Dùng /cancel để hủy.",
        parse_mode="HTML"
    )


# =========================================================
# CANCEL
# =========================================================

async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    if not user or not is_admin(user.id):
        return

    if user.id in pending_group_broadcast:

        del pending_group_broadcast[user.id]

        await update.message.reply_text(
            "❌ Đã hủy gửi tin vào nhóm."
        )

    else:

        await update.message.reply_text(
            "ℹ️ Hiện không có yêu cầu /ara nào."
        )


# =========================================================
# USERS
# =========================================================

async def users_cmd(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    if not user or not is_admin(user.id):
        return

    total = len(users)

    active = sum(
        1
        for item in users.values()
        if item.get("active", True)
    )

    await update.message.reply_text(
        "👥 <b>THỐNG KÊ USER</b>\n\n"
        f"📊 Tổng: <b>{total}</b>\n"
        f"🟢 Active: <b>{active}</b>\n"
        f"🔴 Không active: <b>{total - active}</b>",
        parse_mode="HTML"
    )


# =========================================================
# PRIVATE TEXT HANDLER
# =========================================================

async def text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await remember_user(update)

    user = update.effective_user
    message = update.message

    if not user or not message:
        return

    if user.id not in pending_group_broadcast:

        return

    group_id = pending_group_broadcast[user.id]

    text = message.text

    if not text:
        return

    try:

        await context.bot.send_message(
            chat_id=group_id,
            text=text,
            disable_web_page_preview=False
        )

        del pending_group_broadcast[user.id]

        await message.reply_text(
            "✅ <b>ĐÃ GỬI VÀO NHÓM</b>\n\n"
            f"🆔 Group: <code>{group_id}</code>",
            parse_mode="HTML"
        )

    except RetryAfter as e:

        await message.reply_text(
            f"⏳ Telegram đang giới hạn gửi.\n"
            f"Thử lại sau {e.retry_after} giây."
        )

    except Forbidden:

        del pending_group_broadcast[user.id]

        await message.reply_text(
            "❌ Bot không có quyền gửi tin vào nhóm."
        )

    except BadRequest as e:

        del pending_group_broadcast[user.id]

        await message.reply_text(
            "❌ Không thể gửi vào nhóm.\n\n"
            f"<code>{html.escape(str(e))}</code>",
            parse_mode="HTML"
        )

    except Exception as e:

        logger.exception(
            "Lỗi gửi /ara"
        )

        await message.reply_text(
            "❌ Gửi thất bại:\n"
            f"<code>{html.escape(str(e))}</code>",
            parse_mode="HTML"
        )


# =========================================================
# ERROR HANDLER
# =========================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    logger.exception(
        "Bot error:",
        exc_info=context.error
    )


# =========================================================
# MAIN
# =========================================================

def run():

    if not TOKEN:

        raise RuntimeError(
            "Chưa cấu hình BOT TOKEN."
        )

    app = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    # Public commands
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            ["ff", "freefire"],
            ff
        )
    )

    app.add_handler(
        CommandHandler(
            "tt",
            tt
        )
    )

    app.add_handler(
        CommandHandler(
            ["likes", "like"],
            likes_cmd
        )
    )

    app.add_handler(
        CommandHandler(
            "help",
            help_command
        )
    )

    # Admin commands
    app.add_handler(
        CommandHandler(
            "tb",
            tb
        )
    )

    app.add_handler(
        CommandHandler(
            "ara",
            ara
        )
    )

    app.add_handler(
        CommandHandler(
            "cancel",
            cancel
        )
    )

    app.add_handler(
        CommandHandler(
            "amin",
            amin
        )
    )

    app.add_handler(
        CommandHandler(
            "users",
            users_cmd
        )
    )

    # Buttons
    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    # Private text
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE
            & filters.TEXT
            & ~filters.COMMAND,
            text_handler
        )
    )

    app.add_error_handler(
        error_handler
    )

    logger.info(
        "================================"
    )

    logger.info(
        "BOT BAO ARA ĐANG CHẠY"
    )

    logger.info(
        "================================"
    )

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    run()
