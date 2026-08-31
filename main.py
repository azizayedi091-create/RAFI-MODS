
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# تفعيل الـ Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ==================== CONFIG & DATABASE ====================
TOKEN = "8671890016:AAE8BHBQh-90oqVvtom2UlMLnCLHl19DLkY"
ADMIN_ID = 6605879863  # ⚠️ حط الـ Telegram ID متاعك هنا باش تنجم تزيد الـ Keys

# مخزن المفاتيح (Stock الديناميكي)
STOCK_DB = {
    # الهيكل: "plan_id": ["KEY1", "KEY2", ...]
}

USER_BALANCES = {}

# قائمة الـ 21 منتج
ALL_PRODUCTS = [
    ("brmod_root", "🛒 BrMod Root Android"),
    ("drip_client", "🛒 Drip Client ApkMod"),
    ("angry_mod", "🛒 Angry Mod Root"),
    ("brmods_silent", "🛒 BrMods SilentAim Pc"),
    ("esign_ios", "🛒 ESign Certificate iOS"),
    ("hex_blade", "🛒 Hex Blade Root"),
    ("hg_cheat", "🛒 Hg Cheat ApkMod"),
    ("migul_pro", "🛒 Migul Pro iOS"),
    ("pato_or lo ange", "🛒 Pato Team Orange Apkmod"),
    ("rapid_core", "🔑 Rapid Core Root"),
    ("silentcheats", "🛒 SilentCheats ApkMod"),
    ("silentcheat_brutal", "🛒 SilentCheat Root Brutal"),
    ("zytron_pro", "🛒 Zytron Pro Internal Root"),
    ("bala_mod", "🛒 Bala Mod Android [Non Root]"),
    ("skb_mod", "🛒 Skb Mod Root"),
    ("abcd_panel", "🛒 ABCD Panel Non Root"),
    ("aim_hack", "🛒 Aim Hack Android [Non Root]"),
    ("unseen_mods", "🛒 Unseen Mods Root"),
    ("xreg_android", "🛒 XReg Android [Non Root]"),
    ("guild_glory", "🛒 Guild Glory Bot"),
    ("hg_prime", "🛒 Hg Cheat Prime Proxy")
]

# بيانات المنتجات والخطط
PRODUCTS_DATA = {
    "unseen_mods": {
        "name": "UNSEEN MODS ROOT",
        "plans": [
            {"id": "unseen_1d", "name": "1 Day", "price": 0.50},
            {"id": "unseen_3d", "name": "3 Day", "price": 2.00},
            {"id": "unseen_7d", "name": "7 Day", "price": 4.00},
        ]
    },
    "bala_mod": {
        "name": "BALA MOD ANDROID [NON ROOT]",
        "plans": [
            {"id": "bala_1h", "name": "1 Hours", "price": 0.20},
            {"id": "bala_3h", "name": "3 Hours", "price": 0.60},
            {"id": "bala_6h", "name": "6 Hours", "price": 0.90},
            {"id": "bala_12h", "name": "12 Hours", "price": 1.80},
            {"id": "bala_24h", "name": "24 Hours", "price": 3.00},
            {"id": "bala_48h", "name": "48 Hours (2 Day)", "price": 5.50},
            {"id": "bala_72h", "name": "72 Hours (3 Day)", "price": 8.50},
            {"id": "bala_168h", "name": "168 Hours (7 Day)", "price": 20.00},
        ]
    }
}

# ==================== HELPERS ====================
def get_main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Shop Now", callback_data="shop_now")],
        [
            InlineKeyboardButton("💰 Add Balance", callback_data="add_balance"),
            InlineKeyboardButton("📝 My Orders", callback_data="my_orders")
        ],
        [
            InlineKeyboardButton("👤 My Profile", callback_data="my_profile"),
            InlineKeyboardButton("🎁 Refer & Earn", callback_data="refer_earn")
        ],
        [
            InlineKeyboardButton("🖼 Tutorial", callback_data="tutorial"),
            InlineKeyboardButton("🎡 Daily Spin", callback_data="daily_spin")
        ],
        [
            InlineKeyboardButton("💸 Share & Earn", callback_data="share_earn"),
            InlineKeyboardButton("💬 Get Help", callback_data="get_help")
        ]
    ])

def get_main_text(user_name):
    return (
        "🏪 — **RAFIMODZ SHOP** — 🏪\n\n"
        f"🎉 *Hello, {user_name}!*\n\n"
        "🔑 *Digital keys delivered in seconds.*\n\n"
        "➨ 🏪 *Huge product catalog*\n"
        "➨ ⚡ *Lightning-fast delivery*\n"
        "➨ 💸 *Pay how you want*\n"
        "➨ 📤 *Refer & earn rewards*\n"
        "➨ 🔒 *24/7 priority support*\n\n"
        "_Pick an option below to get started._"
    )

# ==================== HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.set_my_commands([BotCommand("start", "Open shop")])
    reply_kb = ReplyKeyboardMarkup([["🛒 Open shop"]], resize_keyboard=True)
    await update.message.reply_text("Welcome!", reply_markup=reply_kb)

    await update.message.reply_text(
        text=get_main_text(update.effective_user.first_name),
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard()
    )

# --- أمر للأدمين لإضافة الـ Keys ---
async def add_key_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text("❌ طريقة الاستخدام:\n`/addkey plan_id THE_KEY_HERE`", parse_mode="Markdown")
        return

    plan_id = context.args[0]
    key_val = " ".join(context.args[1:])

    if plan_id not in STOCK_DB:
        STOCK_DB[plan_id] = []

    STOCK_DB[plan_id].append(key_val)
    count = len(STOCK_DB[plan_id])
    await update.message.reply_text(f"✅ تم إضافة المفتاح لـ `{plan_id}`!\nالـ Stock الحالي: **{count}**", parse_mode="Markdown")

# --- إدارة الأزرار ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    user_name = query.from_user.first_name

    if data == "main_menu":
        await query.edit_message_text(
            text=get_main_text(user_name),
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard()
        )

    elif data in ["shop_now", "all_products"]:
        text = (
            "⭐ **Product Lineup**\n\n"
            "➨ 🔑 *Premium Keys*\n"
            "➨ ⚡ *Instant Delivery*\n"
            "➨ 🔒 *Secure Payment*\n"
            "➨ 💬 *24/7 Support*\n\n"
            "👇 *Pick what you want* 👇\n"
            "_Tap any product to see options._"
        )
        keyboard = [[InlineKeyboardButton(p_name, callback_data=f"prod_{p_id}")] for p_id, p_name in ALL_PRODUCTS]
        keyboard.append([InlineKeyboardButton("🔙 Go Back", callback_data="main_menu")])

        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("prod_"):
        prod_key = data.replace("prod_", "")
        prod_info = PRODUCTS_DATA.get(prod_key, {
            "name": prod_key.replace("_", " ").upper(),
            "plans": [
                {"id": f"{prod_key}_1d", "name": "1 Day", "price": 1.00},
                {"id": f"{prod_key}_7d", "name": "7 Day", "price": 5.00}
            ]
        })

        text = f"🛒 **{prod_info['name']}**\n\n📊 **PLANS & PRICING:**\n\n"
        keyboard = []

        for plan in prod_info["plans"]:
            keys_available = STOCK_DB.get(plan["id"], [])
            stock_count = len(keys_available)
            
            # تحديد العلامة ونص الـ Stock بناءً على العدد
            if stock_count > 0:
                status_icon = "✅"
                stock_str = f"{stock_count} Available"
                btn_label = f"🛒 Buy {plan['name']} - ${plan['price']:.2f}"
            else:
                status_icon = "❌"
                stock_str = "Out of Stock"
                btn_label = f"🛒 Buy {plan['name']} - ${plan['price']:.2f} (Out of Stock)"

            text += (
                f"{status_icon} **{plan['name']}**\n"
                f"➠ 📦 **Stock:** {stock_str}\n"
                f"➠ 💰 **Price:** ${plan['price']:.2f}\n\n"
            )

            keyboard.append([InlineKeyboardButton(btn_label, callback_data=f"buy_{plan['id']}")])
        
        text += "🎯 **CHOOSE A PLAN:**\n━━━━━━━━━━━━━━━━━━━━"
        keyboard.append([InlineKeyboardButton("🛒 All Products", callback_data="all_products")])

        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif data.startswith("buy_"):
        plan_id = data.replace("buy_", "")
        keys = STOCK_DB.get(plan_id, [])

        if not keys:
            await query.answer("❌ عفواً، هذا المنتج Out of Stock حالياً!", show_alert=True)
            return

        key_to_give = keys.pop(0)
        await query.message.reply_text(
            f"🎉 **تم الشراء بنجاح!**\n\n🔑 المفتاح الخاص بك:\n`{key_to_give}`",
            parse_mode="Markdown"
        )

    elif data == "add_balance":
        bal = USER_BALANCES.get(user_id, 0.0)
        text = (
            "💸 **Add Balance**\n\n"
            f"💸 **Current balance:** ${bal:.2f} USD\n"
            "🔄 **Min:** $0.50 USD  ·  🔄 **Max:** $1000 USD\n\n"
            "_Pick an amount below. Local-currency total appears on the gateway button._"
        )
        keyboard = [
            [InlineKeyboardButton("💰 $1 USD", callback_data="pay_1"), InlineKeyboardButton("💰 $2 USD", callback_data="pay_2")],
            [InlineKeyboardButton("💰 $5 USD", callback_data="pay_5"), InlineKeyboardButton("💰 $10 USD", callback_data="pay_10")],
            [InlineKeyboardButton("💰 $50 USD", callback_data="pay_50"), InlineKeyboardButton("💰 $100 USD", callback_data="pay_100")],
            [InlineKeyboardButton("✏️ Custom Amount (USD)", callback_data="pay_custom")],
            [InlineKeyboardButton("🔙 Go Back", callback_data="main_menu")]
        ]
        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("pay_"):
        amount_str = data.replace("pay_", "")
        amount = 100.0 if amount_str == "100" else float(amount_str) if amount_str.isdigit() else 1.0
        bal = USER_BALANCES.get(user_id, 0.0)
        after_dep = bal + amount

        text = (
            "💸 **ADD BALANCE — Step 2 of 2**\n\n"
            f"💸 **Current balance:** ${bal:.2f} USD\n"
            f"➕ **Adding:** ${amount:.2f} USD\n"
            f"✨ **After deposit:** ${after_dep:.2f} USD\n\n"
            "⚡ **Pick how to fund your wallet**\n"
            "_Each button shows the amount in the gateway's native currency._"
        )
        keyboard = [
            [InlineKeyboardButton(f"Binance Pay — ${amount:.0f} USDT", callback_data=f"binance_{amount}")],
            [InlineKeyboardButton("🔙 Back", callback_data="add_balance")]
        ]
        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🛒 Open shop":
        await update.message.reply_text(
            text=get_main_text(update.effective_user.first_name),
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard()
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addkey", add_key_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    logging.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
