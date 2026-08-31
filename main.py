import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    ContextTypes, MessageHandler, filters
)

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # تحط التوكين متاعك هنا أو في Render
ADMIN_ID = 6605879863

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ---------------------------------------------------------
# DATABASE SETUP
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            key_code TEXT NOT NULL UNIQUE,
            is_sold INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            plan TEXT DEFAULT 'Free',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------
def get_db_connection():
    return sqlite3.connect('shop.db')

def add_user(user_id, username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", 
        (user_id, username)
    )
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# BOT COMMANDS & HANDLERS
# ---------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username)

    keyboard = [
        [InlineKeyboardButton("🛒 Shop Products", callback_data='menu_shop')],
        [InlineKeyboardButton("⭐ Subscription Plans", callback_data='menu_plans')],
        [InlineKeyboardButton("👤 My Account", callback_data='menu_account')],
        [InlineKeyboardButton("📞 Support", callback_data='menu_support')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"👋 Welcome {user.mention_html()} to RAFI-MODS Shop!\n\n"
        "Select an option below to explore our digital goods and services."
    )
    
    if update.message:
        await update.message.reply_html(welcome_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'menu_shop':
        keyboard = [
            [InlineKeyboardButton("🔑 Mod Keys", callback_data='shop_modkeys')],
            [InlineKeyboardButton("📜 Certificates", callback_data='shop_certs')],
            [InlineKeyboardButton("🔙 Back", callback_data='menu_main')]
        ]
        await query.message.edit_text(" Choose a category:", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif data in ['shop_modkeys', 'shop_certs']:
        category = "Mod Keys" if data == 'shop_modkeys' else "Certificates"
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM inventory WHERE category = ? AND is_sold = 0", (category,))
        count = cursor.fetchone()[0]
        conn.close()
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='menu_shop')]]
        await query.message.edit_text(
            f"📦 Category: *{category}*\n"
            f"Available Stock: `{count}` items\n\n"
            "To purchase, please contact support or select a subscription plan.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    elif data == 'menu_plans':
        text = (
            "⭐ *Subscription Plans*\n\n"
            "• *VIP Monthly*: Unlimited access to basic keys.\n"
            "• *PRO Lifetime*: Full access to mod keys & certificates.\n\n"
            "Contact admin to upgrade your tier."
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='menu_main')]]
        await query.message.edit_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'menu_account':
        user_id = query.from_user.id
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT plan FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        plan = row[0] if row else "Free"
        conn.close()
        
        text = f"👤 *Account Details*\n\nUser ID: `{user_id}`\nCurrent Plan: *{plan}*"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='menu_main')]]
        await query.message.edit_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'menu_support':
        text = "📞 For support and custom orders, contact @Admin."
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='menu_main')]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'menu_main':
        await start(update, context)

# ---------------------------------------------------------
# ADMIN COMMANDS
# ---------------------------------------------------------
async def add_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Unauthorized access.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /addkey <category> <key_code>\nExample: /addkey ModKeys ABCD-1234")
        return

    category = context.args[0]
    key_code = context.args[1]

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inventory (category, key_code) VALUES (?, ?)", (category, key_code))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"✅ Successfully added key to `{category}`.", parse_mode='Markdown')
    except sqlite3.IntegrityError:
        await update.message.reply_text("❌ Error: Key already exists in database.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ---------------------------------------------------------
# MAIN APPLICATION
# ---------------------------------------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addkey", add_key))
    app.add_handler(CallbackQueryHandler(button_handler))

    logging.info("Bot is starting...")
    app.run_polling()

if __name__ == '__main__':
    main()
