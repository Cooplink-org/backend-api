import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler,
    filters,
    CallbackContext
)
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from apps.accounts.models import TelegramAuthSession, User
from apps.projects.models import Project
from apps.news.models import NewsArticle
import structlog
import asyncio
from datetime import datetime, timedelta
from asgiref.sync import sync_to_async

logger = structlog.get_logger(__name__)

# Bot command descriptions
BOT_COMMANDS = [
    BotCommand("start", "🚀 Start using Cooplink Bot"),
    BotCommand("help", "📚 Show help and commands"),
    BotCommand("login", "🔐 Login to your account"),
    BotCommand("profile", "👤 View your profile"),
    BotCommand("projects", "📁 Browse latest projects"),
    BotCommand("news", "📰 Latest platform news"),
    BotCommand("stats", "📊 Platform statistics"),
    BotCommand("balance", "💰 Check your balance"),
    BotCommand("notifications", "🔔 Notification settings"),
    BotCommand("support", "🆘 Get support"),
]

async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    
    # Create main menu keyboard
    keyboard = [
        [
            InlineKeyboardButton("🔐 Login/Register", callback_data="auth_login"),
            InlineKeyboardButton("📱 Link Account", callback_data="auth_link")
        ],
        [
            InlineKeyboardButton("📁 Browse Projects", callback_data="menu_projects"),
            InlineKeyboardButton("📰 Latest News", callback_data="menu_news")
        ],
        [
            InlineKeyboardButton("📊 Platform Stats", callback_data="menu_stats"),
            InlineKeyboardButton("🆘 Support", callback_data="menu_support")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
            InlineKeyboardButton("ℹ️ About", callback_data="menu_about")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = (
        f"🎉 Welcome to **Cooplink Bot**, {user.first_name}! 👋\n\n"
        f"🚀 Your gateway to the ultimate developer marketplace!\n\n"
        f"🌟 **What can you do here?**\n"
        f"• 🔐 Securely login to your account\n"
        f"• 📁 Browse amazing code projects\n"
        f"• 📰 Stay updated with platform news\n"
        f"• 💰 Manage your transactions\n"
        f"• 📊 View platform statistics\n\n"
        f"💡 Choose an option below to get started!"
    )
    
    if update.message:
        await update.message.reply_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.callback_query.edit_message_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def handle_callback_query(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = query.from_user
    
    if data == "auth_login":
        await handle_auth_login(update, context)
    elif data == "auth_link":
        await handle_auth_link(update, context)
    elif data == "menu_projects":
        await handle_projects_menu(update, context)
    elif data == "menu_news":
        await handle_news_menu(update, context)
    elif data == "menu_stats":
        await handle_stats_menu(update, context)
    elif data == "menu_support":
        await handle_support_menu(update, context)
    elif data == "menu_settings":
        await handle_settings_menu(update, context)
    elif data == "menu_about":
        await handle_about_menu(update, context)
    elif data == "back_main":
        await start(update, context)
    elif data.startswith("project_"):
        await handle_project_details(update, context, data)
    elif data.startswith("news_"):
        await handle_news_details(update, context, data)
    elif data.startswith("page_"):
        await handle_pagination(update, context, data)

async def handle_auth_login(update: Update, context: CallbackContext):
    user = update.callback_query.from_user
    
    # Check if user is already linked
    try:
        cooplink_user = await sync_to_async(User.objects.get)(telegram_id=user.id)
        keyboard = [
            [
                InlineKeyboardButton("👤 View Profile", callback_data="profile_view"),
                InlineKeyboardButton("💰 Check Balance", callback_data="profile_balance")
            ],
            [
                InlineKeyboardButton("📁 My Projects", callback_data="profile_projects"),
                InlineKeyboardButton("🛒 My Purchases", callback_data="profile_purchases")
            ],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"✅ **Account Already Linked!** 🎉\n\n"
            f"👤 **Welcome back, {cooplink_user.username}!**\n\n"
            f"📊 **Account Summary:**\n"
            f"• 🎭 Role: {cooplink_user.get_role_display()}\n"
            f"• 💰 Balance: {cooplink_user.balance:,.0f} UZS\n"
            f"• ✅ Verified: {'Yes' if cooplink_user.is_verified else 'No'}\n"
            f"• 📅 Member since: {cooplink_user.created_at.strftime('%B %Y')}\n\n"
            f"🚀 What would you like to do?"
        )
        
    except User.DoesNotExist:
        # Create auth session
        auth_url = f"{settings.TELEGRAM_WEBHOOK_URL.rstrip('/')}/auth/login/{user.id}"
        keyboard = [
            [InlineKeyboardButton("🔐 Login to Cooplink", url=auth_url)],
            [InlineKeyboardButton("📝 Create New Account", url=f"{settings.TELEGRAM_WEBHOOK_URL.rstrip('/')}/register")],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"🔐 **Account Authentication** 🚀\n\n"
            f"👋 Hi {user.first_name}! To access your Cooplink account:\n\n"
            f"1️⃣ **Existing User?** Click 'Login' to authenticate\n"
            f"2️⃣ **New User?** Click 'Create New Account' to register\n\n"
            f"🔒 **Security Note:** This is a secure authentication process.\n"
            f"Your Telegram account will be safely linked to Cooplink.\n\n"
            f"✨ After linking, you'll have full access to all platform features!"
        )
    
    await update.callback_query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_auth_link(update: Update, context: CallbackContext):
    user = update.callback_query.from_user
    
    link_url = f"{settings.TELEGRAM_WEBHOOK_URL.rstrip('/')}/auth/link/{user.id}"
    keyboard = [
        [InlineKeyboardButton("🔗 Link My Account", url=link_url)],
        [InlineKeyboardButton("❓ How It Works", callback_data="link_help")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        f"🔗 **Link Your Cooplink Account** 📱\n\n"
        f"🎯 **Connect your existing account to Telegram:**\n\n"
        f"1️⃣ Click the 'Link My Account' button\n"
        f"2️⃣ Login with your Cooplink credentials\n"
        f"3️⃣ Authorize the Telegram connection\n"
        f"4️⃣ Enjoy seamless access! 🚀\n\n"
        f"🔒 **100% Secure** - Your data is protected\n"
        f"⚡ **Instant Access** - No waiting time\n"
        f"🎉 **Full Features** - Everything at your fingertips!"
    )
    
    await update.callback_query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_projects_menu(update: Update, context: CallbackContext):
    # Get latest projects
    projects = await sync_to_async(list)(Project.objects.filter(is_approved=True, is_active=True)[:5])
    
    if not projects:
        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"📁 **No Projects Available** 😔\n\n"
            f"🔍 There are currently no approved projects.\n"
            f"Check back later for awesome code projects!"
        )
    else:
        keyboard = []
        for project in projects:
            keyboard.append([
                InlineKeyboardButton(
                    f"📁 {project.title[:30]}{'...' if len(project.title) > 30 else ''}",
                    callback_data=f"project_{project.id}"
                )
            ])
        
        keyboard.extend([
            [
                InlineKeyboardButton("🔍 Search Projects", url=f"{settings.TELEGRAM_WEBHOOK_URL.rstrip('/')}/projects"),
                InlineKeyboardButton("📊 Browse by Category", callback_data="projects_categories")
            ],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_main")]
        ])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"📁 **Latest Projects** 🔥\n\n"
            f"🌟 **{len(projects)} Featured Projects Available:**\n\n"
            f"🚀 Select a project to view details\n"
            f"💡 Or browse more on our website!\n\n"
            f"💰 **Total Projects:** {Project.objects.filter(is_approved=True).count()}\n"
            f"👨‍💻 **Active Sellers:** {Project.objects.filter(is_approved=True).values('seller').distinct().count()}"
        )
    
    await update.callback_query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_news_menu(update: Update, context: CallbackContext):
    # Get latest news
    news_articles = await sync_to_async(list)(NewsArticle.objects.filter(status='published')[:5])
    
    if not news_articles:
        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"📰 **No News Available** 📭\n\n"
            f"🔍 No news articles are currently published.\n"
            f"Stay tuned for platform updates!"
        )
    else:
        keyboard = []
        for article in news_articles:
            keyboard.append([
                InlineKeyboardButton(
                    f"📰 {article.title[:35]}{'...' if len(article.title) > 35 else ''}",
                    callback_data=f"news_{article.id}"
                )
            ])
        
        keyboard.extend([
            [
                InlineKeyboardButton("📖 Read All News", url=f"{settings.TELEGRAM_WEBHOOK_URL.rstrip('/')}/news"),
                InlineKeyboardButton("🔔 Subscribe", callback_data="news_subscribe")
            ],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_main")]
        ])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"📰 **Latest Platform News** 🔥\n\n"
            f"🗞️ **{len(news_articles)} Recent Articles:**\n\n"
            f"📖 Click on any article to read\n"
            f"🔔 Subscribe to get notified of new updates!\n\n"
            f"✨ Stay informed about platform improvements and features!"
        )
    
    await update.callback_query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_stats_menu(update: Update, context: CallbackContext):
    # Get platform statistics
    total_users = await sync_to_async(User.objects.count)()
    total_projects = await sync_to_async(Project.objects.filter(is_approved=True).count)()
    total_sellers = await sync_to_async(User.objects.filter(role='seller').count)()
    total_news = await sync_to_async(NewsArticle.objects.filter(status='published').count)()
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Detailed Stats", url=f"{settings.TELEGRAM_WEBHOOK_URL.rstrip('/')}/stats"),
            InlineKeyboardButton("📈 Growth Chart", callback_data="stats_growth")
        ],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        f"📊 **Cooplink Platform Statistics** 🚀\n\n"
        f"🌟 **Community Overview:**\n\n"
        f"👥 **Total Users:** {total_users:,}\n"
        f"👨‍💻 **Active Sellers:** {total_sellers:,}\n"
        f"📁 **Available Projects:** {total_projects:,}\n"
        f"📰 **News Articles:** {total_news:,}\n\n"
        f"⚡ **Platform Activity:**\n"
        f"• 🔥 Growing community of developers\n"
        f"• 💰 Secure payment processing\n"
        f"• 🚀 New projects added daily\n"
        f"• 🌍 Global developer marketplace\n\n"
        f"🎯 **Join the movement!**"
    )
    
    await update.callback_query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_support_menu(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("📧 Contact Support", url="mailto:support@cooplink.uz"),
            InlineKeyboardButton("💬 Live Chat", url=f"{settings.TELEGRAM_WEBHOOK_URL.rstrip('/')}/support")
        ],
        [
            InlineKeyboardButton("📚 Documentation", url=f"{settings.TELEGRAM_WEBHOOK_URL.rstrip('/')}/docs"),
            InlineKeyboardButton("❓ FAQ", callback_data="support_faq")
        ],
        [
            InlineKeyboardButton("🐛 Report Bug", callback_data="support_bug"),
            InlineKeyboardButton("💡 Feature Request", callback_data="support_feature")
        ],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        f"🆘 **Support Center** 🛠️\n\n"
        f"👋 **Need help? We're here for you!**\n\n"
        f"🚀 **Quick Support Options:**\n\n"
        f"📧 **Email Support** - Get detailed help\n"
        f"💬 **Live Chat** - Instant assistance\n"
        f"📚 **Documentation** - Self-help guides\n"
        f"❓ **FAQ** - Common questions\n\n"
        f"🔧 **Report Issues:**\n"
        f"🐛 Found a bug? Let us know!\n"
        f"💡 Have a feature idea? Share it!\n\n"
        f"⏰ **Response Time:** Usually within 24 hours"
    )
    
    await update.callback_query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_settings_menu(update: Update, context: CallbackContext):
    user = update.callback_query.from_user
    
    keyboard = [
        [
            InlineKeyboardButton("🔔 Notifications", callback_data="settings_notifications"),
            InlineKeyboardButton("🌐 Language", callback_data="settings_language")
        ],
        [
            InlineKeyboardButton("🔐 Privacy", callback_data="settings_privacy"),
            InlineKeyboardButton("📱 Account", callback_data="settings_account")
        ],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        f"⚙️ **Bot Settings** 🛠️\n\n"
        f"🎛️ **Customize your experience:**\n\n"
        f"🔔 **Notifications** - Manage alerts\n"
        f"🌐 **Language** - Choose your language\n"
        f"🔐 **Privacy** - Control your data\n"
        f"📱 **Account** - Manage account settings\n\n"
        f"💡 **Tip:** Settings are synced with your Cooplink account!"
    )
    
    await update.callback_query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_about_menu(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("🌐 Visit Website", url="https://cooplink.uz"),
            InlineKeyboardButton("📱 Mobile App", callback_data="about_app")
        ],
        [
            InlineKeyboardButton("👥 Team", callback_data="about_team"),
            InlineKeyboardButton("📄 Terms", url=f"{settings.TELEGRAM_WEBHOOK_URL.rstrip('/')}/terms")
        ],
        [
            InlineKeyboardButton("🔒 Privacy Policy", url=f"{settings.TELEGRAM_WEBHOOK_URL.rstrip('/')}/privacy"),
            InlineKeyboardButton("📞 Contact", callback_data="about_contact")
        ],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        f"ℹ️ **About Cooplink** 🚀\n\n"
        f"🌟 **The Ultimate Developer Marketplace**\n\n"
        f"🎯 **Our Mission:**\n"
        f"Connect developers worldwide through a secure,\n"
        f"innovative platform for buying and selling code.\n\n"
        f"💡 **What We Offer:**\n"
        f"• 🔒 Secure transactions\n"
        f"• 🌍 Global marketplace\n"
        f"• 💰 Fair pricing\n"
        f"• 🛡️ Quality assurance\n"
        f"• 🚀 Fast delivery\n\n"
        f"📅 **Version:** 1.0.0\n"
        f"🏢 **Company:** Cooplink LLC\n"
        f"📍 **Location:** Uzbekistan"
    )
    
    await update.callback_query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("🚀 Get Started", callback_data="back_main"),
            InlineKeyboardButton("🆘 Support", callback_data="menu_support")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        f"📚 **Cooplink Bot Help** 🤖\n\n"
        f"🎯 **Available Commands:**\n\n"
        f"🚀 `/start` - Open main menu\n"
        f"📚 `/help` - Show this help\n"
        f"🔐 `/login` - Quick login\n"
        f"👤 `/profile` - View profile\n"
        f"📁 `/projects` - Browse projects\n"
        f"📰 `/news` - Latest news\n"
        f"📊 `/stats` - Platform stats\n"
        f"💰 `/balance` - Check balance\n"
        f"🔔 `/notifications` - Manage alerts\n"
        f"🆘 `/support` - Get help\n\n"
        f"💡 **Tips:**\n"
        f"• Use buttons for easier navigation\n"
        f"• Link your account for full access\n"
        f"• Enable notifications for updates\n\n"
        f"🎉 **Ready to explore?**"
    )
    
    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Command handlers
async def login_command(update: Update, context: CallbackContext):
    await handle_auth_login(update, context)

async def profile_command(update: Update, context: CallbackContext):
    user = update.effective_user
    try:
        cooplink_user = await sync_to_async(User.objects.get)(telegram_id=user.id)
        message = (
            f"👤 **Your Profile** 🌟\n\n"
            f"📝 **Username:** {cooplink_user.username}\n"
            f"📧 **Email:** {cooplink_user.email}\n"
            f"🎭 **Role:** {cooplink_user.get_role_display()}\n"
            f"💰 **Balance:** {cooplink_user.balance:,.0f} UZS\n"
            f"✅ **Verified:** {'Yes' if cooplink_user.is_verified else 'No'}\n"
            f"📅 **Member since:** {cooplink_user.created_at.strftime('%B %Y')}\n\n"
            f"📊 **Activity:**\n"
            f"• 📁 Projects: {getattr(cooplink_user, 'seller_projects', cooplink_user.projects if hasattr(cooplink_user, 'projects') else []).count() if hasattr(getattr(cooplink_user, 'seller_projects', cooplink_user.projects if hasattr(cooplink_user, 'projects') else []), 'count') else 0}\n"
            f"• 🛒 Purchases: {getattr(cooplink_user, 'buyer_transactions', []).count() if hasattr(getattr(cooplink_user, 'buyer_transactions', []), 'count') else 0}\n"
        )
    except User.DoesNotExist:
        message = (
            f"❌ **Account Not Linked** 🔗\n\n"
            f"Please use /start to link your account first!"
        )
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def projects_command(update: Update, context: CallbackContext):
    await handle_projects_menu(update, context)

async def news_command(update: Update, context: CallbackContext):
    await handle_news_menu(update, context)

async def stats_command(update: Update, context: CallbackContext):
    await handle_stats_menu(update, context)

async def balance_command(update: Update, context: CallbackContext):
    user = update.effective_user
    try:
        cooplink_user = await sync_to_async(User.objects.get)(telegram_id=user.id)
        message = (
            f"💰 **Your Balance** 💳\n\n"
            f"💵 **Current Balance:** {cooplink_user.balance:,.0f} UZS\n\n"
            f"📊 **Recent Activity:**\n"
            f"• 🛒 Recent purchases\n"
            f"• 💰 Recent earnings\n"
            f"• 📈 Balance changes\n\n"
            f"🔗 View detailed transaction history on the website!"
        )
    except User.DoesNotExist:
        message = (
            f"❌ **Account Not Linked** 🔗\n\n"
            f"Please use /start to link your account first!"
        )
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def notifications_command(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("🔔 Enable All", callback_data="notif_enable_all"),
            InlineKeyboardButton("🔕 Disable All", callback_data="notif_disable_all")
        ],
        [
            InlineKeyboardButton("📁 Project Updates", callback_data="notif_projects"),
            InlineKeyboardButton("📰 News Alerts", callback_data="notif_news")
        ],
        [
            InlineKeyboardButton("💰 Payment Alerts", callback_data="notif_payments"),
            InlineKeyboardButton("🔔 System Alerts", callback_data="notif_system")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        f"🔔 **Notification Settings** ⚙️\n\n"
        f"🎛️ **Customize your alerts:**\n\n"
        f"📁 **Project Updates** - New projects, purchases\n"
        f"📰 **News Alerts** - Platform announcements\n"
        f"💰 **Payment Alerts** - Transaction notifications\n"
        f"🔔 **System Alerts** - Important system updates\n\n"
        f"💡 **Current Status:** All enabled"
    )
    
    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def support_command(update: Update, context: CallbackContext):
    await handle_support_menu(update, context)

async def search_command(update: Update, context: CallbackContext):
    """Handle project search command"""
    message = (
        f"🔍 **Project Search** 🚀\n\n"
        f"🌟 **Quick Search Tips:**\n\n"
        f"• Type keywords to find projects\n"
        f"• Use filters for better results\n"
        f"• Browse by categories\n"
        f"• Check trending projects\n\n"
        f"💡 Visit our website for advanced search!"
    )
    
    keyboard = [
        [InlineKeyboardButton("🌐 Open Search", url=f"{settings.TELEGRAM_WEBHOOK_URL.rstrip('/')}/projects")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def trending_command(update: Update, context: CallbackContext):
    """Show trending projects"""
    # Get trending projects (most purchased/viewed)
    trending_projects = await sync_to_async(list)(Project.objects.filter(
        is_approved=True, 
        is_active=True
    ).order_by('-view_count', '-created_at')[:5])
    
    if not trending_projects:
        message = "📈 No trending projects found right now!"
    else:
        message = f"📈 **Trending Projects** 🔥\n\n"
        for i, project in enumerate(trending_projects, 1):
            message += f"{i}. 📁 **{project.title}**\n"
            message += f"   💰 {project.price:,.0f} UZS\n"
            message += f"   👀 {project.view_count} views\n\n"
    
    keyboard = [
        [InlineKeyboardButton("🌐 View All Trending", url=f"{settings.TELEGRAM_WEBHOOK_URL.rstrip('/')}/projects?sort=trending")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def categories_command(update: Update, context: CallbackContext):
    """Show project categories"""
    message = (
        f"📊 **Project Categories** 📁\n\n"
        f"🎯 **Available Categories:**\n\n"
        f"💻 **Web Development** - Frontend & Backend\n"
        f"📱 **Mobile Apps** - iOS & Android\n"
        f"🤖 **AI/ML** - Machine Learning Projects\n"
        f"🎮 **Games** - Game Development\n"
        f"🔧 **Tools** - Developer Tools & Utilities\n"
        f"📊 **Data Science** - Analytics & Visualization\n"
        f"🔒 **Security** - Cybersecurity Tools\n"
        f"🌐 **API** - APIs & Integrations\n\n"
        f"💡 Click below to browse by category!"
    )
    
    keyboard = [
        [InlineKeyboardButton("🌐 Browse Categories", url=f"{settings.TELEGRAM_WEBHOOK_URL.rstrip('/')}/projects/categories")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_project_details(update: Update, context: CallbackContext, data: str):
    """Handle project detail view"""
    try:
        project_id = int(data.split('_')[1])
        project = Project.objects.get(id=project_id, is_approved=True)
        
        keyboard = [
            [InlineKeyboardButton("🌐 View Full Details", url=f"{settings.TELEGRAM_WEBHOOK_URL.rstrip('/')}/projects/{project.id}")],
            [InlineKeyboardButton("💰 Purchase Now", url=f"{settings.TELEGRAM_WEBHOOK_URL.rstrip('/')}/projects/{project.id}/purchase")],
            [InlineKeyboardButton("🔙 Back to Projects", callback_data="menu_projects")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"📁 **{project.title}** 🚀\n\n"
            f"📝 **Description:**\n{project.description[:200]}{'...' if len(project.description) > 200 else ''}\n\n"
            f"💰 **Price:** {project.price:,.0f} UZS\n"
            f"👨‍💻 **Seller:** {project.seller.username}\n"
            f"📊 **Category:** {project.category.title() if hasattr(project, 'category') else 'General'}\n"
            f"👀 **Views:** {project.view_count}\n"
            f"📅 **Created:** {project.created_at.strftime('%B %d, %Y')}\n\n"
            f"🚀 **Ready to purchase?**"
        )
        
    except (ValueError, Project.DoesNotExist):
        keyboard = [[InlineKeyboardButton("🔙 Back to Projects", callback_data="menu_projects")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = "❌ Project not found or no longer available."
    
    await update.callback_query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_news_details(update: Update, context: CallbackContext, data: str):
    """Handle news article detail view"""
    try:
        news_id = int(data.split('_')[1])
        article = NewsArticle.objects.get(id=news_id, status='published')
        
        keyboard = [
            [InlineKeyboardButton("📖 Read Full Article", url=f"{settings.TELEGRAM_WEBHOOK_URL.rstrip('/')}/news/{article.slug}")],
            [InlineKeyboardButton("🔙 Back to News", callback_data="menu_news")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"📰 **{article.title}** 📢\n\n"
            f"📝 **Summary:**\n{article.excerpt[:200]}{'...' if len(article.excerpt) > 200 else ''}\n\n"
            f"✍️ **Author:** {article.author.first_name} {article.author.last_name}\n"
            f"📅 **Published:** {article.created_at.strftime('%B %d, %Y')}\n"
            f"👀 **Views:** {article.view_count}\n"
            f"❤️ **Likes:** {article.like_count}\n\n"
            f"📖 **Click to read the full article!**"
        )
        
    except (ValueError, NewsArticle.DoesNotExist):
        keyboard = [[InlineKeyboardButton("🔙 Back to News", callback_data="menu_news")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = "❌ Article not found or no longer available."
    
    await update.callback_query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_pagination(update: Update, context: CallbackContext, data: str):
    """Handle pagination for lists"""
    # Implementation for pagination
    await update.callback_query.answer("Pagination feature coming soon! 🚧")

async def error_handler(update: object, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Try to send a user-friendly error message
    if update and hasattr(update, 'effective_chat'):
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="😔 Sorry, something went wrong. Our team has been notified and will fix this soon!"
            )
        except Exception:
            pass  # Ignore if we can't send the error message

def setup_bot_handlers(application):
    """Setup all bot handlers for the given application"""
    try:
        # Command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("login", login_command))
        application.add_handler(CommandHandler("profile", profile_command))
        application.add_handler(CommandHandler("projects", projects_command))
        application.add_handler(CommandHandler("news", news_command))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(CommandHandler("balance", balance_command))
        application.add_handler(CommandHandler("notifications", notifications_command))
        application.add_handler(CommandHandler("support", support_command))
        
        # Enhanced commands
        application.add_handler(CommandHandler("search", search_command))
        application.add_handler(CommandHandler("trending", trending_command))
        application.add_handler(CommandHandler("categories", categories_command))
        
        # Callback query handler
        application.add_handler(CallbackQueryHandler(handle_callback_query))
        
        # Error handler
        application.add_error_handler(error_handler)
        
        # Set bot commands after initialization
        async def post_init(app):
            try:
                await app.bot.set_my_commands(BOT_COMMANDS)
                logger.info("Bot commands set successfully")
            except Exception as e:
                logger.error(f"Failed to set bot commands: {str(e)}")
        
        application.post_init = post_init
        
        logger.info("Bot handlers configured successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup bot handlers: {str(e)}")
        return False

def setup_telegram_bot():
    """Setup telegram bot with webhook support"""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("Telegram bot token not configured")
        return None
    
    try:
        # Initialize the application with webhook support
        application = (
            Application.builder()
            .token(settings.TELEGRAM_BOT_TOKEN)
            .concurrent_updates(True)
            .build()
        )
        
        # Setup handlers first
        if setup_bot_handlers(application):
            logger.info("Telegram bot handlers configured successfully")
            
            # Setup webhook if URL is configured
            if settings.TELEGRAM_WEBHOOK_URL:
                logger.info(f"Setting webhook to: {settings.TELEGRAM_WEBHOOK_URL}")
                # Set webhook synchronously
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(application.bot.set_webhook(
                        url=settings.TELEGRAM_WEBHOOK_URL,
                        drop_pending_updates=True
                    ))
                    logger.info("Webhook set successfully")
                except Exception as e:
                    logger.error(f"Failed to set webhook: {e}")
                finally:
                    loop.close()
            
            return application
        else:
            return None
        
    except Exception as e:
        logger.error(f"Failed to setup telegram bot: {str(e)}")
        return None

async def run_polling_bot():
    """Run bot in polling mode for development"""
    try:
        # Create a fresh application instance for polling
        application = (
            Application.builder()
            .token(settings.TELEGRAM_BOT_TOKEN)
            .concurrent_updates(True)
            .build()
        )
        
        # Setup handlers
        setup_bot_handlers(application)
        
        logger.info("Starting Telegram bot in polling mode...")
        
        # Initialize and start the application
        await application.initialize()
        await application.start()
        await application.updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
        # Keep the bot running
        logger.info("Bot is now running in polling mode...")
        try:
            # Keep running until stopped
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            logger.info("Stopping bot...")
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
            
    except Exception as e:
        logger.error(f"Error in polling bot: {e}")
        raise
            
def start_polling_in_thread():
    """Start polling in a separate thread with proper event loop handling"""
    import threading
    import asyncio
    
    def run_bot():
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the bot
            loop.run_until_complete(run_polling_bot())
            
        except Exception as e:
            logger.error(f"Bot thread error: {e}")
        finally:
            try:
                # Clean up the loop
                loop = asyncio.get_event_loop()
                if not loop.is_closed():
                    loop.close()
            except Exception:
                pass
    
    # Start the bot in a daemon thread
    bot_thread = threading.Thread(target=run_bot, daemon=True, name="TelegramBot")
    bot_thread.start()
    logger.info("Bot polling thread started")
    return bot_thread

# Global application instance
application = None

def get_application():
    """Get or create the telegram bot application"""
    global application
    if application is None:
        application = setup_telegram_bot()
    return application
