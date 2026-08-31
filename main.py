import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# تفعيل الـ Logging لمتابعة الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ==================== DATABASE & CONFIG ====================
# ضع التوكن الخاص بك هنا
TOKEN = "8671890016:AAE8BHBQh-90oqVvtom2UlMLnCLHl19DLkY"

# قاعدة بيانات وهمية للمستخدمين والستوك (يمكن ربطها بـ SQLite لاحقاً)
user_balances = {}

# قائمة كافة المنتجات والخطط
PRODUCTS_DATA = {
    "unseen_mods": {
        "name": "UNSEEN MODS ROOT",
        "plans": [
            {"id": "unseen_1d", "name": "1 Day", "price": 0.50, "stock": "In Stock"},
            {"id": "unseen_3d", "name": "3 Day", "price": 2.00, "stock": "In Stock"},
            {"id": "unseen_7d", "name": "7 Day", "price": 4.00, "stock": "In Stock"},
        ]
    },
    "bala_mod": {
        "name": "BALA MOD ANDROID [NON ROOT]",
        "plans": [
            {"id": "bala_1h", "name": "1 Hours", "price": 0.20, "stock": "In Stock"},
            {"id": "bala_3h", "name": "3 Hours", "price": 0.60, "stock": "In Stock"},
            {"id": "bala_6h", "name": "6 Hours", "price": 0.90, "stock": "In Stock"},
            {"id": "bala_12h", "name": "12 Hours", "price": 1.80, "stock": "In Stock"},
            {"id": "bala_24h", "name": "24 Hours", "price": 3.00, "stock": "In Stock"},
            {"id": "bala_48h", "name": "48 Hours (2 DAY)", "price": 5.50, "stock": "In Stock"},
            {"id": "bala_72h", "name": "72 Hours (3 DAY)", "price": 8.50, "stock": "In Stock"},
            {"id": "bala_168h", "name": "168 Hours (7 DAY)", "price": 20.00, "stock": "In Stock"},
        ]
    }
}

# قائمة أسماء الـ 21 منتج الكاملة
ALL_PRODUCTS = [
    ("brmod_root", "🛒 BrMod Root Android"),
    ("drip_client", "🛒 Drip Client ApkMod"),
    ("angry_mod", "🛒 Angry Mod Root"),
    ("brmods_silent", "🛒 BrMods SilentAim Pc"),
    ("esign_ios", "🛒 ESign Certificate iOS"),
    ("hex_blade", "🛒 Hex Blade Root"),
    ("hg_cheat", "🛒 Hg Cheat ApkMod"),
    ("migul_pro", "🛒 Migul Pro iOS"),
    ("pato_orange", "🛒 Pato Team Orange Apkmod"),
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

# ==================== HELPER FUNCTIONS ====================
def get_main_menu_keyboard():
    keyboard = [
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
    ]
    return InlineKeyboardMarkup(keyboard)

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
    # إعداد الـ Menu button السفلي
    await context.bot.set_my_commands([BotCommand("start", "Open shop")])
    
    # إعداد الكيبورد السفلي (Reply Keyboard)
    reply_kb = ReplyKeyboardMarkup([["🛒 Open shop"]], resize_keyboard=True)
    await update.message.reply_text("Welcome!", reply_markup=reply_kb)

    user_name = update.effective_user.first_name
    await update.message.reply_text(
        text=get_main_text(user_name),
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    user_name = query.from_user.first_name

    # 1. القائمة الرئيسية (Main Menu)
    if data == "main_menu":
        await query.edit_message_text(
            text=get_main_text(user_name),
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard()
        )

    # 2. كتالوج المنتجات (Shop Catalog)
    elif data == "shop_now" or data == "all_products":
        text = (
            "⭐ **Product Lineup**\n\n"
            "➨ 🔑 *Premium Keys*\n"
            "➨ ⚡ *Instant Delivery*\n"
            "➨ 🔒 *Secure Payment*\n"
            "➨ 💬 *24/7 Support*\n\n"
            "👇 *Pick what you want* 👇\n"
            "_Tap any product to see options._"
        )
        keyboard = []
        for p_id, p_name in ALL_PRODUCTS:
            keyboard.append([InlineKeyboardButton(p_name, callback_data=f"prod_{p_id}")])
        keyboard.append([InlineKeyboardButton("🔙 Go Back", callback_data="main_menu")])

        await query.edit_message_text(
            text=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # 3. اختيار منتج معين (Product Details & Plans)
    elif data.startswith("prod_"):
        prod_key = data.replace("prod_", "")
        prod_info = PRODUCTS_DATA.get(prod_key)

        if not prod_info:
            # افتراضي للمنتجات الأخرى بنفس التنسيق
            prod_info = {
                "name": prod_key.replace("_", " ").upper(),
                "plans": [
                    {"id": f"{prod_key}_1d", "name": "1 Day", "price": 1.00, "stock": "In Stock"},
                    {"id": f"{prod_key}_7d", "name": "7 Day", "price": 5.00, "stock": "In Stock"}
                ]
            }

        text = f"📱 **{prod_info['name']}**\n\n📋 **PLANS & PRICING:**\n\n"
        keyboard = []
        for plan in prod_info["plans"]:
            text += (
                f"🗝️ **{plan['name']}**\n"
                f"➨ 🔍 **Stock:** {plan['stock']}\n"
                f"➨ 💰 **Price:** ${plan['price']:.2f}\n\n"
            )
            keyboard.append([
                InlineKeyboardButton(
                    f"🛒 Buy {plan['name']} - ${plan['price']:.2f}",
                    callback_data=f"buy_{plan['id']}"
                )
            ])
        
        text += "🌐 **CHOOSE A PLAN:**"
        keyboard.append([InlineKeyboardButton("🛒 All Products", callback_data="all_products")])

        await query.edit_message_text(
            text=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # 4. زر شحن الرصيد (Add Balance - Step 1)
    elif data == "add_balance":
        balance = user_balances.get(user_id, 0.0)
        text = (
            "💸 **Add Balance**\n\n"
            f"💸 **Current balance:** ${balance:.2f} USD\n"
            "🔄 **Min:** $0.50 USD  ·  🔄 **Max:** $1000 USD\n\n"
            "_Pick an amount below. Local-currency total appears on the gateway button._"
        )
        keyboard = [
            [
                InlineKeyboardButton("💰 $1 USD", callback_data="pay_1"),
                InlineKeyboardButton("💰 $2 USD", callback_data="pay_2")
            ],
            [
                InlineKeyboardButton("💰 $3 USD", callback_data="pay_3"),
                InlineKeyboardButton("💰 $4 USD", callback_data="pay_4")
            ],
            [
                InlineKeyboardButton("💰 $5 USD", callback_data="pay_5"),
                InlineKeyboardButton("💰 $10 USD", callback_data="pay_10")
            ],
            [
                InlineKeyboardButton("💰 $50 USD", callback_data="pay_50"),
                InlineKeyboardButton("💰 $100 USD", callback_data="pay_100")
            ],
            [InlineKeyboardButton("✏️ Custom Amount (USD)", callback_data="pay_custom")],
            [InlineKeyboardButton("🔙 Go Back", callback_data="main_menu")]
        ]
        await query.edit_message_text(
            text=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # 5. خطوة الشحن الثانية (Add Balance - Step 2)
    elif data.startswith("pay_"):
        amount_str = data.replace("pay_", "")
        amount = 100.0 if amount_str == "100" else float(amount_str) if amount_str.isdigit() else 1.0
        balance = user_balances.get(user_id, 0.0)
        after_dep = balance + amount

        text = (
            "💸 **ADD BALANCE — Step 2 of 2**\n\n"
            f"💸 **Current balance:** ${balance:.2f} USD\n"
            f"➕ **Adding:** ${amount:.2f} USD\n"
            f"✨ **After deposit:** ${after_dep:.2f} USD\n\n"
            "⚡ **Pick how to fund your wallet**\n"
            "_Each button shows the amount in the gateway's native currency._"
        )
        keyboard = [
            [InlineKeyboardButton(f"Binance Pay — ${amount:.0f} USDT", callback_data=f"binance_{amount}")],
            [InlineKeyboardButton("🔙 Back", callback_data="add_balance")]
        ]
        await query.edit_message_text(
            text=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# Handle Text Commands (like typing '🛒 Open shop')
async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🛒 Open shop":
        user_name = update.effective_user.first_name
        await update.message.reply_text(
            text=get_main_text(user_name),
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard()
        )

# ==================== MAIN RUNNER ====================
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))

    logging.info("Bot started successfully...")
    app.run_polling()

if __name__ == "__main__":
    main()
