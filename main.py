import logging
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, BotCommand
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, 
    filters, ContextTypes, ConversationHandler
)

# تفعيل الـ Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ==================== CONFIG & DATABASE ====================
TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_ID = 123456789  # ⚠️ حط الـ Telegram ID متاعك هنا
MY_BINANCE_PAY_ID = "1258086568"

# حالات المحادثة لإدخال Order ID
WAITING_ORDER_ID = 1

# مخزن البيانات الوقتية للمشتريات
PENDING_ORDERS = {}  # {user_id: {"plan_id": ..., "order_id": ..., "amount": ...}}

# مخزن المفاتيح (Stock الديناميكي)
STOCK_DB = {}
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

PRODUCTS_DATA = {
    "unseen_mods": {
        "name": "Unseen Mods Root",
        "plans": [
            {"id": "unseen_1d", "name": "1 Day", "price": 0.50},
            {"id": "unseen_3d", "name": "3 Day", "price": 2.00},
            {"id": "unseen_7d", "name": "7 Day", "price": 4.00},
        ]
    },
    "bala_mod": {
        "name": "Bala Mod Android [Non Root]",
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
    },
    "guild_glory": {
        "name": "Guild Glory Bot",
        "plans": [
            {"id": "guild_1b", "name": "1 Besic 4 Bot", "price": 1.20},
            {"id": "guild_7d", "name": "7 Day", "price": 5.00}
        ]
    }
}

# توليد Order ID عشوائي
def generate_order_code():
    return "ORD" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

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
    
    remove_msg = await update.message.reply_text("Loading...", reply_markup=ReplyKeyboardRemove())
    await remove_msg.delete()

    await update.message.reply_text(
        text=get_main_text(update.effective_user.first_name),
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard()
    )
    return ConversationHandler.END

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
    await update.message.reply_text(f"✅ تم إضافة المفتاح لـ `{plan_id}`!\nالـ Stock الحالي: **{len(STOCK_DB[plan_id])}**", parse_mode="Markdown")

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
        return ConversationHandler.END

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
        keyboard.append([InlineKeyboardButton("🏠 Go Back", callback_data="main_menu")])

        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END

    elif data.startswith("prod_"):
        prod_key = data.replace("prod_", "")
        prod_info = PRODUCTS_DATA.get(prod_key, {
            "name": prod_key.replace("_", " ").title(),
            "plans": [
                {"id": f"{prod_key}_1d", "name": "1 Day", "price": 1.00},
                {"id": f"{prod_key}_7d", "name": "7 Day", "price": 5.00}
            ]
        })

        text = f"🛒 **{prod_info['name'].upper()}**\n\n📊 **PLANS & PRICING:**\n\n"
        keyboard = []

        for plan in prod_info["plans"]:
            keys_available = STOCK_DB.get(plan["id"], [])
            stock_count = len(keys_available)
            
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

            keyboard.append([InlineKeyboardButton(btn_label, callback_data=f"selectplan_{prod_key}_{plan['id']}")])
        
        text += "🎯 **CHOOSE A PLAN:**\n━━━━━━━━━━━━━━━━━━━━"
        keyboard.append([InlineKeyboardButton("🛒 All Products", callback_data="all_products")])

        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END

    # 1️⃣ صفحة CHECKOUT SUMMARY (التنسيق في الصورة الأولى)
    elif data.startswith("selectplan_"):
        _, prod_key, plan_id = data.split("_", 2)
        prod_info = PRODUCTS_DATA.get(prod_key, {"name": prod_key.title()})
        
        plan_name = "1 Day"
        price = 1.00
        if "plans" in prod_info:
            for p in prod_info["plans"]:
                if p["id"] == plan_id:
                    plan_name = p["name"]
                    price = p["price"]
                    break

        text = (
            "📋 **CHECKOUT SUMMARY**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"➠ 🔑 **Product:** 🏪 {prod_info['name']}\n"
            f"➠ 🔑 **Plan:** {plan_name}\n"
            f"➠ 📋 **Quantity:** 1\n"
            f"➠ 💰 **Unit price:** ${price:.2f} USD\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💰 **Final Total: ${price:.2f} USD**\n\n"
            "👇 **Pick how you want to pay**\n"
            "_Pick any option below — each button shows the exact amount in that currency. If you have wallet balance, you can pay instantly with it._"
        )

        keyboard = [
            [InlineKeyboardButton(f"💸 Binance Pay — ${price:.2f} USDT", callback_data=f"binancepay_{plan_id}_{price:.2f}")],
            [InlineKeyboardButton("🎡 Apply Coupon Code", callback_data="coupon")],
            [InlineKeyboardButton("🏠 All Plans", callback_data=f"prod_{prod_key}")]
        ]

        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END

    # 2️⃣ صفحة BINANCE PAY (التنسيق في الصورة الثانية)
    elif data.startswith("binancepay_"):
        _, plan_id, price_str = data.split("_", 2)
        order_code = generate_order_code()

        PENDING_ORDERS[user_id] = {
            "plan_id": plan_id,
            "order_code": order_code,
            "amount": price_str
        }

        text = (
            "⚠️ **BINANCE PAY** · 💸 *Auto-verified*\n"
            f"➠ 💰 **Amount: ${price_str} USDT**\n"
            f"➠ 🔒 **Order: {order_code}**\n"
            f"➠ 💰 **Pay ID: {MY_BINANCE_PAY_ID}**\n"
            "➠ ⏰ **Expires in: 5:00**\n\n"
            "ℹ️ **Steps**\n"
            "➠ 1️⃣ Open Binance app ➔ **Pay** ➔ **Send**\n"
            f"➠ 2️⃣ **Enter Pay ID: {MY_BINANCE_PAY_ID}**\n"
            f"➠ 3️⃣ Send **exactly ${price_str} USDT**\n"
            "➠ 4️⃣ Tap below and send your **Binance Order ID**\n\n"
            "⚠️ *This payment expires in 5 minutes.*"
        )

        keyboard = [
            [InlineKeyboardButton("📝 I Paid — Submit Order ID", callback_data="submit_order_id")],
            [InlineKeyboardButton("🏠 Go Back", callback_data="main_menu")]
        ]

        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END

    elif data == "submit_order_id":
        order_info = PENDING_ORDERS.get(user_id)
        if not order_info:
            await query.answer("❌ لا يوجد طلب معلق حالياً!", show_alert=True)
            return ConversationHandler.END

        order_code = order_info["order_code"]
        await query.message.reply_text(
            f"⏱ Send your Binance **Order ID** for order\n`{order_code}`:",
            parse_mode="Markdown"
        )
        return WAITING_ORDER_ID

# 3️⃣ استلام الـ Order ID من الحريف (التنسيق في الصورة الثالثة)
async def receive_order_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    tx_id = update.message.text.strip()
    order_info = PENDING_ORDERS.get(user_id)

    if not order_info:
        await update.message.reply_text("❌ لم يتم العثور على طلب معلق. يرجى البدء من جديد.")
        return ConversationHandler.END

    plan_id = order_info["plan_id"]
    order_code = order_info["order_code"]
    amount = order_info["amount"]

    # إعلام الحريف بتسلم الطلب
    await update.message.reply_text(
        f"✅ **تم إرسال الطلب بنجاح!**\n\n"
        f"🔒 **Order:** `{order_code}`\n"
        f"🆔 **Binance Order ID:** `{tx_id}`\n\n"
        f"⏳ جاري التحقق وتسليم الـ Key أوتوماتيكياً...",
        parse_mode="Markdown"
    )

    # إرسال إشعار للأدمين للموافقة أو التثبيت
    admin_kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Accept & Send Key", callback_data=f"adm_acc_{user_id}_{plan_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"adm_rej_{user_id}")
        ]
    ])

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "🚨 **طلب دفع جديد (Binance Pay)**\n\n"
            f"👤 **المستعمل:** {user_name} (`{user_id}`)\n"
            f"🛒 **المنتج:** `{plan_id}`\n"
            f"💰 **المبلغ:** `${amount} USDT`\n"
            f"🔒 **Order Code:** `{order_code}`\n"
            f"🆔 **Binance Order ID:** `{tx_id}`"
        ),
        parse_mode="Markdown",
        reply_markup=admin_kb
    )

    return ConversationHandler.END

# أزرار الأدمين لقبول أو رفض الشراء
async def admin_decision_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data.startswith("adm_acc_"):
        _, _, user_id_str, plan_id = data.split("_", 3)
        target_id = int(user_id_str)
        keys = STOCK_DB.get(plan_id, [])

        if not keys:
            await query.answer("❌ الـ Stock فارغ لهذا المنتج!", show_alert=True)
            return

        key_to_give = keys.pop(0)

        # إرسال المفتاح للمشتري
        await context.bot.send_message(
            chat_id=target_id,
            text=f"🎉 **تم تأكيد الدفع بنجاح!**\n\n🔑 **المفتاح الخاص بك:**\n`{key_to_give}`",
            parse_mode="Markdown"
        )
        await query.edit_message_text(text=query.message.text + "\n\n✅ **تمت الموافقة وإرسال المفتاح.**")

    elif data.startswith("adm_rej_"):
        target_id = int(data.split("_")[2])
        await context.bot.send_message(
            chat_id=target_id,
            text="❌ **للأسف، تعذر التحقق من عملية الدفع الخاص بك.** يرجى الاتصال بالدعم إذا كان هناك خطأ."
        )
        await query.edit_message_text(text=query.message.text + "\n\n❌ **تم الرفض.**")

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^submit_order_id$")],
        states={
            WAITING_ORDER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_order_id)]
        },
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addkey", add_key_cmd))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(admin_decision_handler, pattern="^adm_"))
    app.add_handler(CallbackQueryHandler(button_handler))

    logging.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
