import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3

# تنظیمات اولیه
API_TOKEN = '8248228783:AAETdSTAdkCloBGGO2j-HuELsPgvDu3WpmE'
ADMIN_ID = 8905899077  # آیدی عددی خودتان
CHANNEL_ID = "@starzraygan_channel"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# --- مدیریت دیتابیس ---
conn = sqlite3.connect('bot_data.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (user_id INTEGER PRIMARY KEY, balance INTEGER, refs INTEGER, is_banned INTEGER)''')
conn.commit()

# --- دکمه‌ها ---
def main_menu(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔗 زیرمجموعه‌گیری", callback_data="referral"),
        types.InlineKeyboardButton("🎁 دریافت استارز", callback_data="get_stars"),
        types.InlineKeyboardButton("👤 حساب من", callback_data="profile"),
        types.InlineKeyboardButton("🏆 برترین‌ها", callback_data="top_list")
    )
    if user_id == ADMIN_ID:
        markup.add(types.InlineKeyboardButton("🔴 پنل مدیریت", callback_data="admin_panel"))
    return markup

# --- سیستم چک کردن عضویت ---
async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# --- دستور استارت ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    
    # چک عضویت
    if not await is_subscribed(user_id):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📢 عضویت در کانال", url="https://t.me/starzraygan_channel"))
        kb.add(types.InlineKeyboardButton("✅ تایید عضویت", callback_data="check_join"))
        await message.answer("⚠️ برای استفاده از ربات باید در کانال عضو باشید:", reply_markup=kb)
        return

    # ثبت کاربر در دیتابیس (اگر نبود)
    cursor.execute("INSERT OR IGNORE INTO users VALUES (?, 0, 0, 0)", (user_id,))
    conn.commit()
    
    await message.answer("✨ خوش آمدید به ربات استارز رایگان!", reply_markup=main_menu(user_id))

# --- بخش مدیریت پاسخ‌ها (Callback) ---
@dp.callback_query_handler(lambda c: c.data == 'check_join')
async def check_join(call: types.CallbackQuery):
    if await is_subscribed(call.from_user.id):
        await call.message.edit_text("✅ عضویت تایید شد! حالا می‌توانید استفاده کنید.", reply_markup=main_menu(call.from_user.id))
    else:
        await call.answer("❌ هنوز عضو کانال نشدید!", show_alert=True)

@dp.callback_query_handler(lambda c: c.data == 'profile')
async def profile(call: types.CallbackQuery):
    cursor.execute("SELECT balance, refs FROM users WHERE user_id=?", (call.from_user.id,))
    data = cursor.fetchone()
    await call.message.answer(f"👤 حساب کاربری شما:\n🆔 آیدی: {call.from_user.id}\n💎 موجودی: {data[0]}\n🔗 دعوت‌ها: {data[1]}")

# --- اجرای ربات ---
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)