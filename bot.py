import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import re
from collections import Counter

# ============= LOGGING SETUP =============
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============= ENVIRONMENT VARIABLES =============
BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_USERNAME = os.environ.get('BOT_USERNAME', 'WordStyleBot')
BOT_NAME = os.environ.get('BOT_NAME', 'WordStyleBot')

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN environment variable is not set!")
    raise ValueError("BOT_TOKEN is required. Add it to Railway variables.")

logger.info(f"✅ Starting {BOT_NAME} (@{BOT_USERNAME})")

# ============= TEXT STYLING FUNCTIONS =============

# Unicode character maps for fancy text
FANCY_MAPS = {
    'bold': {
        'a': '𝗮', 'b': '𝗯', 'c': '𝗰', 'd': '𝗱', 'e': '𝗲', 'f': '𝗳', 'g': '𝗴',
        'h': '𝗵', 'i': '𝗶', 'j': '𝗷', 'k': '𝗸', 'l': '𝗹', 'm': '𝗺', 'n': '𝗻',
        'o': '𝗼', 'p': '𝗽', 'q': '𝗾', 'r': '𝗿', 's': '𝘀', 't': '𝘁', 'u': '𝘂',
        'v': '𝘃', 'w': '𝘄', 'x': '𝘅', 'y': '𝘆', 'z': '𝘇',
        'A': '𝗔', 'B': '𝗕', 'C': '𝗖', 'D': '𝗗', 'E': '𝗘', 'F': '𝗙', 'G': '𝗚',
        'H': '𝗛', 'I': '𝗜', 'J': '𝗝', 'K': '𝗞', 'L': '𝗟', 'M': '𝗠', 'N': '𝗡',
        'O': '𝗢', 'P': '𝗣', 'Q': '𝗤', 'R': '𝗥', 'S': '𝗦', 'T': '𝗧', 'U': '𝗨',
        'V': '𝗩', 'W': '𝗪', 'X': '𝗫', 'Y': '𝗬', 'Z': '𝗭'
    },
    'bold_italic': {
        'a': '𝙖', 'b': '𝙗', 'c': '𝙘', 'd': '𝙙', 'e': '𝙚', 'f': '𝙛', 'g': '𝙜',
        'h': '𝙝', 'i': '𝙞', 'j': '𝙟', 'k': '𝙠', 'l': '𝙡', 'm': '𝙢', 'n': '𝙣',
        'o': '𝙤', 'p': '𝙥', 'q': '𝙦', 'r': '𝙧', 's': '𝙨', 't': '𝙩', 'u': '𝙪',
        'v': '𝙫', 'w': '𝙬', 'x': '𝙭', 'y': '𝙮', 'z': '𝙯',
        'A': '𝘼', 'B': '𝘽', 'C': '𝘾', 'D': '𝘿', 'E': '𝙀', 'F': '𝙁', 'G': '𝙂',
        'H': '𝙃', 'I': '𝙄', 'J': '𝙅', 'K': '𝙆', 'L': '𝙇', 'M': '𝙈', 'N': '𝙉',
        'O': '𝙊', 'P': '𝙋', 'Q': '𝙌', 'R': '𝙍', 'S': '𝙎', 'T': '𝙏', 'U': '𝙐',
        'V': '𝙑', 'W': '𝙒', 'X': '𝙓', 'Y': '𝙔', 'Z': '𝙕'
    },
    'italic': {
        'a': '𝘢', 'b': '𝘣', 'c': '𝘤', 'd': '𝘥', 'e': '𝘦', 'f': '𝘧', 'g': '𝘨',
        'h': '𝘩', 'i': '𝘪', 'j': '𝘫', 'k': '𝘬', 'l': '𝘭', 'm': '𝘮', 'n': '𝘯',
        'o': '𝘰', 'p': '𝘱', 'q': '𝘲', 'r': '𝘳', 's': '𝘴', 't': '𝘵', 'u': '𝘶',
        'v': '𝘷', 'w': '𝘸', 'x': '𝘹', 'y': '𝘺', 'z': '𝘻',
        'A': '𝘈', 'B': '𝘉', 'C': '𝘊', 'D': '𝘋', 'E': '𝘌', 'F': '𝘍', 'G': '𝘎',
        'H': '𝘏', 'I': '𝘐', 'J': '𝘑', 'K': '𝘒', 'L': '𝘓', 'M': '𝘔', 'N': '𝘕',
        'O': '𝘖', 'P': '𝘗', 'Q': '𝘘', 'R': '𝘙', 'S': '𝘚', 'T': '𝘛', 'U': '𝘜',
        'V': '𝘝', 'W': '𝘞', 'X': '𝘟', 'Y': '𝘠', 'Z': '𝘡'
    },
    'script': {
        'a': '𝒶', 'b': '𝒷', 'c': '𝒸', 'd': '𝒹', 'e': 'ℯ', 'f': '𝒻', 'g': 'ℊ',
        'h': '𝒽', 'i': '𝒾', 'j': '𝒿', 'k': '𝓀', 'l': '𝓁', 'm': '𝓂', 'n': '𝓃',
        'o': 'ℴ', 'p': '𝓅', 'q': '𝓆', 'r': '𝓇', 's': '𝓈', 't': '𝓉', 'u': '𝓊',
        'v': '𝓋', 'w': '𝓌', 'x': '𝓍', 'y': '𝓎', 'z': '𝓏',
        'A': '𝒜', 'B': 'ℬ', 'C': '𝒞', 'D': '𝒟', 'E': 'ℰ', 'F': 'ℱ', 'G': '𝒢',
        'H': 'ℋ', 'I': 'ℐ', 'J': '𝒥', 'K': '𝒦', 'L': 'ℒ', 'M': 'ℳ', 'N': '𝒩',
        'O': '𝒪', 'P': '𝒫', 'Q': '𝒬', 'R': 'ℛ', 'S': '𝒮', 'T': '𝒯', 'U': '𝒰',
        'V': '𝒱', 'W': '𝒲', 'X': '𝒳', 'Y': '𝒴', 'Z': '𝒵'
    },
    'monospace': {
        'a': '𝚊', 'b': '𝚋', 'c': '𝚌', 'd': '𝚍', 'e': '𝚎', 'f': '𝚏', 'g': '𝚐',
        'h': '𝚑', 'i': '𝚒', 'j': '𝚓', 'k': '𝚔', 'l': '𝚕', 'm': '𝚖', 'n': '𝚗',
        'o': '𝚘', 'p': '𝚙', 'q': '𝚚', 'r': '𝚛', 's': '𝚜', 't': '𝚝', 'u': '𝚞',
        'v': '𝚟', 'w': '𝚠', 'x': '𝚡', 'y': '𝚢', 'z': '𝚣',
        'A': '𝙰', 'B': '𝙱', 'C': '𝙲', 'D': '𝙳', 'E': '𝙴', 'F': '𝙵', 'G': '𝙶',
        'H': '𝙷', 'I': '𝙸', 'J': '𝙹', 'K': '𝙺', 'L': '𝙻', 'M': '𝙼', 'N': '𝙽',
        'O': '𝙾', 'P': '𝙿', 'Q': '𝚀', 'R': '𝚁', 'S': '𝚂', 'T': '𝚃', 'U': '𝚄',
        'V': '𝚅', 'W': '𝚆', 'X': '𝚇', 'Y': '𝚈', 'Z': '𝚉'
    },
    'small_caps': {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ',
        'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
        'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ',
        'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
        'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F', 'G': 'G',
        'H': 'H', 'I': 'I', 'J': 'J', 'K': 'K', 'L': 'L', 'M': 'M', 'N': 'N',
        'O': 'O', 'P': 'P', 'Q': 'Q', 'R': 'R', 'S': 'S', 'T': 'T', 'U': 'U',
        'V': 'V', 'W': 'W', 'X': 'X', 'Y': 'Y', 'Z': 'Z'
    },
    'fraktur': {
        'a': '𝔞', 'b': '𝔟', 'c': '𝔠', 'd': '𝔡', 'e': '𝔢', 'f': '𝔣', 'g': '𝔤',
        'h': '𝔥', 'i': '𝔦', 'j': '𝔧', 'k': '𝔨', 'l': '𝔩', 'm': '𝔪', 'n': '𝔫',
        'o': '𝔬', 'p': '𝔭', 'q': '𝔮', 'r': '𝔯', 's': '𝔰', 't': '𝔱', 'u': '𝔲',
        'v': '𝔳', 'w': '𝔴', 'x': '𝔵', 'y': '𝔶', 'z': '𝔷',
        'A': '𝔄', 'B': '𝔅', 'C': 'ℭ', 'D': '𝔇', 'E': '𝔈', 'F': '𝔉', 'G': '𝔊',
        'H': 'ℌ', 'I': 'ℑ', 'J': '𝔍', 'K': '𝔎', 'L': '𝔏', 'M': '𝔐', 'N': '𝔑',
        'O': '𝔒', 'P': '𝔓', 'Q': '𝔔', 'R': 'ℜ', 'S': '𝔖', 'T': '𝔗', 'U': '𝔘',
        'V': '𝔙', 'W': '𝔚', 'X': '𝔛', 'Y': '𝔜', 'Z': 'ℨ'
    },
    'superscript': {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵',
        '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
        'a': 'ᵃ', 'b': 'ᵇ', 'c': 'ᶜ', 'd': 'ᵈ', 'e': 'ᵉ', 'f': 'ᶠ',
        'g': 'ᵍ', 'h': 'ʰ', 'i': 'ⁱ', 'j': 'ʲ', 'k': 'ᵏ', 'l': 'ˡ',
        'm': 'ᵐ', 'n': 'ⁿ', 'o': 'ᵒ', 'p': 'ᵖ', 'r': 'ʳ', 's': 'ˢ',
        't': 'ᵗ', 'u': 'ᵘ', 'v': 'ᵛ', 'w': 'ʷ', 'x': 'ˣ', 'y': 'ʸ', 'z': 'ᶻ'
    },
    'subscript': {
        '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅',
        '6': '₆', '7': '₇', '8': '₈', '9': '₉',
        'a': 'ₐ', 'e': 'ₑ', 'h': 'ₕ', 'i': 'ᵢ', 'j': 'ⱼ', 'k': 'ₖ',
        'l': 'ₗ', 'm': 'ₘ', 'n': 'ₙ', 'o': 'ₒ', 'p': 'ₚ', 'r': 'ᵣ',
        's': 'ₛ', 't': 'ₜ', 'u': 'ᵤ', 'v': 'ᵥ', 'x': 'ₓ'
    }
}

def apply_fancy_style(text, style_map):
    """Apply fancy Unicode style to text"""
    result = []
    for char in text:
        if char in style_map:
            result.append(style_map[char])
        else:
            result.append(char)
    return ''.join(result)

def uppercase(text):
    return text.upper()

def lowercase(text):
    return text.lower()

def title_case(text):
    return text.title()

def reverse_text(text):
    return text[::-1]

def remove_extra_spaces(text):
    return ' '.join(text.split())

def count_words(text):
    return len(text.split())

def count_chars(text):
    return len(text)

# ============= USER DATA =============
user_data = {}

# ============= COMMAND HANDLERS =============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    first_name = user.first_name or "User"
    
    welcome_text = (
        f"✨ *Welcome to {BOT_NAME}, {first_name}!*\n\n"
        f"I'm @{BOT_USERNAME}, your text styling bot!\n\n"
        "🎨 *What I can do:*\n"
        "• Fancy Unicode text styles\n"
        "• Bold, Italic, Script fonts\n"
        "• Superscript & Subscript\n"
        "• Small caps & Fraktur\n"
        "• Case conversion\n"
        "• Text analysis\n\n"
        "👇 *How to use:*\n"
        "1. Send me any text\n"
        "2. Select a style\n"
        "3. Get your styled text!\n\n"
        "📤 *Or use commands:*\n"
        "/style - Apply styles\n"
        "/analyze - Analyze text\n"
        "/about - About this bot"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🎨 Fancy Styles", callback_data="fancy"),
            InlineKeyboardButton("🔤 Case Converter", callback_data="case"),
        ],
        [
            InlineKeyboardButton("📊 Text Analyzer", callback_data="analyze"),
            InlineKeyboardButton("ℹ️ About", callback_data="about"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command."""
    about_text = (
        "ℹ️ *About WordStyleBot*\n\n"
        "✨ Text Styling Bot\n\n"
        "🎨 *Features:*\n"
        "• 8+ Fancy Unicode styles\n"
        "• Bold, Italic, Script\n"
        "• Superscript & Subscript\n"
        "• Small caps & Fraktur\n"
        "• Case conversion\n"
        "• Text analysis\n\n"
        "Made with ❤️ using Python"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        about_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def style_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /style command."""
    user_id = str(update.effective_user.id)
    
    if user_id not in user_data:
        user_data[user_id] = {'action': None}
    
    user_data[user_id]['action'] = 'style'
    
    keyboard = [
        [
            InlineKeyboardButton("𝗕𝗼𝗹𝗱", callback_data="style_bold"),
            InlineKeyboardButton("𝘪𝘵𝘢𝘭𝘪𝘤", callback_data="style_italic"),
        ],
        [
            InlineKeyboardButton("𝙱𝚘𝚕𝚍 𝙸𝚝𝚊𝚕𝚒𝚌", callback_data="style_bold_italic"),
            InlineKeyboardButton("𝓢𝓬𝓻𝓲𝓹𝓽", callback_data="style_script"),
        ],
        [
            InlineKeyboardButton("𝙼𝚘𝚗𝚘𝚜𝚙𝚊𝚌𝚎", callback_data="style_monospace"),
            InlineKeyboardButton("ꜱᴍᴀʟʟ ᴄᴀᴘꜱ", callback_data="style_small_caps"),
        ],
        [
            InlineKeyboardButton("𝔉𝔯𝔞𝔨𝔱𝔲𝔯", callback_data="style_fraktur"),
            InlineKeyboardButton("ˢᵘᵖᵉʳˢᶜʳᶦᵖᵗ", callback_data="style_superscript"),
        ],
        [
            InlineKeyboardButton("ₛᵤbₛcᵣᵢₚₜ", callback_data="style_subscript"),
            InlineKeyboardButton("🔙 Back to Menu", callback_data="menu"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎨 *Select a text style:*\n\n"
        "Choose a style for your text.\n"
        "Then send me the text to style!",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /analyze command."""
    user_id = str(update.effective_user.id)
    
    if user_id not in user_data:
        user_data[user_id] = {'action': None}
    
    user_data[user_id]['action'] = 'analyze'
    
    await update.message.reply_text(
        "📊 *Text Analyzer*\n\n"
        "Send me text and I'll analyze:\n"
        "• Word count\n"
        "• Character count\n"
        "• Character count (no spaces)\n"
        "• Estimated reading time\n"
        "• Most common words\n\n"
        "📝 Send any text message!",
        parse_mode='Markdown'
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages."""
    user_id = str(update.effective_user.id)
    text = update.message.text
    
    if user_id not in user_data:
        user_data[user_id] = {'action': 'style', 'style_type': 'bold'}
    
    action = user_data[user_id].get('action', 'style')
    style_type = user_data[user_id].get('style_type', 'bold')
    
    if action == 'analyze':
        # Analyze text
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        char_no_space = len(text.replace(' ', ''))
        
        # Estimate reading time (assuming 200 words per minute)
        reading_time = max(1, round(word_count / 200))
        
        # Find most common words
        word_counts = Counter([w.lower() for w in words if len(w) > 3])
        common_words = word_counts.most_common(5)
        
        response = (
            f"📊 *Text Analysis Results*\n\n"
            f"📝 *Text:*\n{text[:200]}{'...' if len(text) > 200 else ''}\n\n"
            f"📈 *Statistics:*\n"
            f"• Words: *{word_count}*\n"
            f"• Characters: *{char_count}*\n"
            f"• Characters (no spaces): *{char_no_space}*\n"
            f"• Estimated reading time: *~{reading_time} min*\n\n"
        )
        
        if common_words:
            response += f"🔤 *Most common words:*\n"
            for word, count in common_words:
                response += f"• {word}: *{count}* times\n"
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Analyze Again", callback_data="analyze"),
                InlineKeyboardButton("🎨 Style Text", callback_data="fancy"),
            ],
            [
                InlineKeyboardButton("🔙 Menu", callback_data="menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return
    
    elif action == 'style':
        # Apply style
        styled_text = text
        
        if style_type == 'bold':
            styled_text = apply_fancy_style(text, FANCY_MAPS['bold'])
        elif style_type == 'italic':
            styled_text = apply_fancy_style(text, FANCY_MAPS['italic'])
        elif style_type == 'bold_italic':
            styled_text = apply_fancy_style(text, FANCY_MAPS['bold_italic'])
        elif style_type == 'script':
            styled_text = apply_fancy_style(text, FANCY_MAPS['script'])
        elif style_type == 'monospace':
            styled_text = apply_fancy_style(text, FANCY_MAPS['monospace'])
        elif style_type == 'small_caps':
            styled_text = apply_fancy_style(text, FANCY_MAPS['small_caps'])
        elif style_type == 'fraktur':
            styled_text = apply_fancy_style(text, FANCY_MAPS['fraktur'])
        elif style_type == 'superscript':
            styled_text = apply_fancy_style(text, FANCY_MAPS['superscript'])
        elif style_type == 'subscript':
            styled_text = apply_fancy_style(text, FANCY_MAPS['subscript'])
        elif style_type == 'upper':
            styled_text = uppercase(text)
        elif style_type == 'lower':
            styled_text = lowercase(text)
        elif style_type == 'title':
            styled_text = title_case(text)
        elif style_type == 'reverse':
            styled_text = reverse_text(text)
        
        response = (
            f"🎨 *Styled Text*\n\n"
            f"📝 {styled_text}\n\n"
            f"📊 *Info:*\n"
            f"• Style: *{style_type}*\n"
            f"• Words: {count_words(styled_text)}\n"
            f"• Characters: {count_chars(styled_text)}"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Style Again", callback_data="fancy"),
                InlineKeyboardButton("📊 Analyze", callback_data="analyze"),
            ],
            [
                InlineKeyboardButton("🔙 Menu", callback_data="menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return


# ============= CALLBACK QUERY HANDLERS =============

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = str(query.from_user.id)
    
    if user_id not in user_data:
        user_data[user_id] = {'action': 'style', 'style_type': 'bold'}
    
    # ===== MENU =====
    if data == "menu":
        keyboard = [
            [
                InlineKeyboardButton("🎨 Fancy Styles", callback_data="fancy"),
                InlineKeyboardButton("🔤 Case Converter", callback_data="case"),
            ],
            [
                InlineKeyboardButton("📊 Text Analyzer", callback_data="analyze"),
                InlineKeyboardButton("ℹ️ About", callback_data="about"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "✨ *Welcome to WordStyleBot!*\n\nWhat would you like to do?",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # ===== FANCY STYLES =====
    elif data == "fancy":
        user_data[user_id]['action'] = 'style'
        
        keyboard = [
            [
                InlineKeyboardButton("𝗕𝗼𝗹𝗱", callback_data="style_bold"),
                InlineKeyboardButton("𝘪𝘵𝘢𝘭𝘪𝘤", callback_data="style_italic"),
            ],
            [
                InlineKeyboardButton("𝙱𝚘𝚕𝚍 𝙸𝚝𝚊𝚕𝚒𝚌", callback_data="style_bold_italic"),
                InlineKeyboardButton("𝓢𝓬𝓻𝓲𝓹𝓽", callback_data="style_script"),
            ],
            [
                InlineKeyboardButton("𝙼𝚘𝚗𝚘𝚜𝚙𝚊𝚌𝚎", callback_data="style_monospace"),
                InlineKeyboardButton("ꜱᴍᴀʟʟ ᴄᴀᴘꜱ", callback_data="style_small_caps"),
            ],
            [
                InlineKeyboardButton("𝔉𝔯𝔞𝔨𝔱𝔲𝔯", callback_data="style_fraktur"),
                InlineKeyboardButton("ˢᵘᵖᵉʳˢᶜʳᶦᵖᵗ", callback_data="style_superscript"),
            ],
            [
                InlineKeyboardButton("ₛᵤbₛcᵣᵢₚₜ", callback_data="style_subscript"),
                InlineKeyboardButton("🔙 Menu", callback_data="menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🎨 *Select a text style:*\n\n"
            "Choose a style for your text.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # ===== CASE =====
    elif data == "case":
        keyboard = [
            [
                InlineKeyboardButton("🔠 UPPERCASE", callback_data="style_upper"),
                InlineKeyboardButton("🔡 lowercase", callback_data="style_lower"),
            ],
            [
                InlineKeyboardButton("📝 Title Case", callback_data="style_title"),
                InlineKeyboardButton("🔄 Reverse", callback_data="style_reverse"),
            ],
            [
                InlineKeyboardButton("🔙 Menu", callback_data="menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🔤 *Case Converter*\n\n"
            "Select a case format for your text.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # ===== ANALYZE =====
    elif data == "analyze":
        user_data[user_id]['action'] = 'analyze'
        await query.edit_message_text(
            "📊 *Text Analyzer*\n\n"
            "Send me text and I'll analyze it!",
            parse_mode='Markdown'
        )
    
    # ===== ABOUT =====
    elif data == "about":
        about_text = (
            "ℹ️ *About WordStyleBot*\n\n"
            "✨ Text Styling Bot\n\n"
            "🎨 *Features:*\n"
            "• 8+ Fancy Unicode styles\n"
            "• Bold, Italic, Script\n"
            "• Superscript & Subscript\n"
            "• Small caps & Fraktur\n"
            "• Case conversion\n"
            "• Text analysis\n\n"
            "Made with ❤️ using Python"
        )
        keyboard = [[InlineKeyboardButton("🔙 Menu", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            about_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # ===== STYLE HANDLERS =====
    elif data.startswith('style_'):
        style_type = data.replace('style_', '')
        user_data[user_id]['action'] = 'style'
        user_data[user_id]['style_type'] = style_type
        
        style_names = {
            'bold': 'Bold',
            'italic': 'Italic',
            'bold_italic': 'Bold Italic',
            'script': 'Script',
            'monospace': 'Monospace',
            'small_caps': 'Small Caps',
            'fraktur': 'Fraktur',
            'superscript': 'Superscript',
            'subscript': 'Subscript',
            'upper': 'UPPERCASE',
            'lower': 'lowercase',
            'title': 'Title Case',
            'reverse': 'Reverse'
        }
        
        name = style_names.get(style_type, style_type)
        
        await query.edit_message_text(
            f"✅ *Selected: {name}*\n\n"
            "Now send me the text to style!\n\n"
            "📝 Send any text message.",
            parse_mode='Markdown'
        )


def main():
    """Start the bot."""
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("about", about))
        application.add_handler(CommandHandler("style", style_command))
        application.add_handler(CommandHandler("analyze", analyze_command))
        
        # Callback handler
        application.add_handler(CallbackQueryHandler(button_handler))
        
        # Message handler for text
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        
        logger.info("🚀 Bot started successfully!")
        logger.info(f"📱 Bot username: @{BOT_USERNAME}")
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise


if __name__ == '__main__':
    main()
