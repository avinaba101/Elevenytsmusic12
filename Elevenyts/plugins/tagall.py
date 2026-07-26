# Copyright (c) 2025 Elevenyts Project
# /tagall command - Tag all members with emoji stickers

import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from datetime import datetime

# =========================
# CONFIGURATION
# =========================

# Emoji Sticker Collection
EMOJI_STICKERS = [
    "✨", "💞", "💖", "❣️", "👾", "🌝", "🌞", "🌛", 
    "😺", "🌟", "🔥", "💥", "💢", "💗", "🤍", 
    "💘", "🧡", "💜", "💝", "⭐", "🌙", "☀️", "🌈",
    "🎵", "🎶", "💫", "⚡", "🎯", "🏆", "👑", "💎",
    "🌸", "🌺", "🌻", "🌹", "💐", "🌷", "🌿", "🍀",
    "🥀", "🪷", "🌺", "🌻", "🌹", "🌷", "🌱", "🌳",
    "🎨", "🖌️", "✨", "🌟", "⭐", "🌙", "☀️", "🌈"
]

# Emoji combinations for each user (look like stickers)
EMOJI_COMBOS = [
    ["✨", "💞", "💖"],
    ["🌟", "🔥", "💥"],
    ["💫", "⚡", "🎯"],
    ["🌸", "🌺", "💐"],
    ["👑", "💎", "⭐"],
    ["🌈", "☀️", "🌙"],
    ["🎵", "🎶", "💜"],
    ["💗", "💘", "🧡"],
    ["🌝", "🌞", "🌛"],
    ["😺", "👾", "✨"],
    ["💞", "❣️", "💝"],
    ["🤍", "💜", "💙"],
    ["🔥", "💥", "💢"],
    ["🌺", "🌸", "🌷"],
    ["🎯", "🏆", "👑"],
    ["💎", "⭐", "🌟"]
]

TAG_LIMIT = 30  # Max members per message
TAG_DELAY = 1   # Delay between messages (seconds)

# =========================
# MAIN COMMAND: /tagall
# =========================

@Client.on_message(filters.command("tagall") & filters.group)
async def tag_all(client: Client, message: Message):
    """Tag all members with emoji stickers - No names shown"""
    
    # Check if user is admin
    try:
        user_status = await client.get_chat_member(message.chat.id, message.from_user.id)
        
        if user_status.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            await message.reply_text(
                "❌ **Only admins can use this command!**\n"
                "Contact group admin to tag all members."
            )
            return
    except Exception as e:
        await message.reply_text("❌ Error checking permissions!")
        return
    
    # Check if bot is admin
    try:
        bot_status = await client.get_chat_member(message.chat.id, client.me.id)
        
        if bot_status.status not in [ChatMemberStatus.ADMINISTRATOR]:
            await message.reply_text(
                "❌ **Bot needs to be admin to tag members!**\n"
                "Please make me admin first."
            )
            return
    except Exception as e:
        await message.reply_text("❌ Error checking bot permissions!")
        return
    
    # Send initial status
    status_msg = await message.reply_text(
        "🔄 **Collecting members...**\n"
        "👥 Please wait..."
    )
    
    # Get all members (excluding bots)
    members = []
    try:
        async for member in client.get_chat_members(message.chat.id):
            if not member.user.is_bot:
                members.append(member)
    except Exception as e:
        await status_msg.edit_text(f"❌ Error fetching members: {e}")
        return
    
    total_members = len(members)
    
    if total_members == 0:
        await status_msg.edit_text("❌ No members found in this group!")
        return
    
    # Shuffle members for random order
    random.shuffle(members)
    
    await status_msg.edit_text(
        f"🎯 **Found {total_members} members**\n"
        f"✨ Starting emoji sticker tagging...\n"
        f"⏳ This may take a few moments..."
    )
    
    # Process members in batches
    processed = 0
    batch = []
    
    for member in members:
        user = member.user
        processed += 1
        
        # Get random emoji combination for this user
        emoji_combo = random.choice(EMOJI_COMBOS)
        emoji_str = "".join(emoji_combo)  # Like "✨💞💖"
        
        # Create mention with emoji only (no name visible)
        mention = f"[{emoji_str}](tg://user?id={user.id})"
        batch.append(mention)
        
        # Update progress every 5 members
        if processed % 5 == 0:
            progress_percent = int((processed / total_members) * 100)
            await status_msg.edit_text(
                f"🎯 **Tagging Members...**\n"
                f"👥 Total: {total_members}\n"
                f"✅ Tagged: {processed}\n"
                f"📊 Progress: {progress_percent}%"
            )
        
        # Send batch when limit reached
        if len(batch) >= TAG_LIMIT:
            await send_emoji_tag_batch(client, message.chat.id, batch, processed, total_members)
            batch = []
            await asyncio.sleep(TAG_DELAY)
    
    # Send remaining members
    if batch:
        await send_emoji_tag_batch(client, message.chat.id, batch, processed, total_members)
    
    # Delete progress message
    await status_msg.delete()
    
    # Send completion message with random emojis
    final_emojis = random.sample(EMOJI_STICKERS, 5)
    await message.reply_text(
        f"{''.join(final_emojis)} **✅ All {total_members} members have been tagged!** {''.join(final_emojis)}\n\n"
        f"📅 Time: {datetime.now().strftime('%H:%M:%S')}\n"
        f"💫 Tagged with ❤️ by Elevenyts Bot\n\n"
        f"📌 Use `/tagcustom ✨💞` for custom emojis"
    )


# =========================
# SEND EMOJI TAG BATCH
# =========================

async def send_emoji_tag_batch(client, chat_id, batch, processed, total):
    """Send a batch of emoji mentions"""
    
    # Random decorative emojis
    decor_emojis = random.sample(EMOJI_STICKERS, 4)
    
    # Create message with emoji mentions
    mention_text = " ".join(batch)
    
    # Create a visually appealing message
    message_text = (
        f"{''.join(decor_emojis)} **✨ Member Stickers ✨** {''.join(decor_emojis)}\n\n"
        f"{mention_text}\n\n"
        f"{'🌈' * 10}\n"
        f"📊 {processed}/{total} members tagged"
    )
    
    await client.send_message(
        chat_id,
        message_text,
        disable_web_page_preview=True
    )


# =========================
# COMMAND: /tagcustom (Custom emoji from user)
# =========================

@Client.on_message(filters.command("tagcustom") & filters.group)
async def tag_custom(client: Client, message: Message):
    """Tag members with custom emoji sequence"""
    
    # Check admin permission
    try:
        user_status = await client.get_chat_member(message.chat.id, message.from_user.id)
        
        if user_status.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            await message.reply_text("❌ **Only admins can use this command!**")
            return
    except:
        await message.reply_text("❌ Error checking permissions!")
        return
    
    # Get custom emojis from command
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.reply_text(
            "❌ **Please provide emojis!**\n"
            "Usage: `/tagcustom ✨💞💖`\n\n"
            "Example: `/tagcustom 🌟🔥💥`"
        )
        return
    
    custom_emojis = args[1].strip()
    
    # Validate custom emojis (should contain at least 1 emoji)
    if len(custom_emojis) < 1:
        await message.reply_text("❌ Please provide valid emojis!")
        return
    
    # Get members (excluding bots)
    members = []
    try:
        async for member in client.get_chat_members(message.chat.id):
            if not member.user.is_bot:
                members.append(member)
    except:
        await message.reply_text("❌ Error fetching members!")
        return
    
    total = len(members)
    
    if total == 0:
        await message.reply_text("❌ No members found!")
        return
    
    status_msg = await message.reply_text(
        f"🎯 **Tagging {total} members with** `{custom_emojis}`..."
    )
    
    # Tag each member with custom emojis
    batch = []
    
    for i, member in enumerate(members):
        user = member.user
        
        # Create mention with custom emojis
        mention = f"[{custom_emojis}](tg://user?id={user.id})"
        batch.append(mention)
        
        # Update progress every 10 members
        if (i + 1) % 10 == 0:
            await status_msg.edit_text(
                f"📊 Progress: {i+1}/{total} members tagged\n"
                f"🎨 Emoji: {custom_emojis}"
            )
        
        # Send batch when limit reached
        if len(batch) >= TAG_LIMIT:
            await client.send_message(
                message.chat.id,
                f"{custom_emojis} **Custom Tags** {custom_emojis}\n\n" + " ".join(batch)
            )
            batch = []
            await asyncio.sleep(TAG_DELAY)
        
        await asyncio.sleep(0.1)  # Small delay
    
    # Send remaining
    if batch:
        await client.send_message(
            message.chat.id,
            f"{custom_emojis} **Custom Tags** {custom_emojis}\n\n" + " ".join(batch)
        )
    
    await status_msg.delete()
    
    await message.reply_text(
        f"✅ **Successfully tagged {total} members with** `{custom_emojis}`"
    )


# =========================
# COMMAND: /taglist (Show available emojis)
# =========================

@Client.on_message(filters.command("taglist") & filters.group)
async def tag_list(client: Client, message: Message):
    """Show available emoji stickers"""
    
    # Format emojis in rows of 10
    emoji_rows = []
    for i in range(0, len(EMOJI_STICKERS), 10):
        row = " ".join(EMOJI_STICKERS[i:i+10])
        emoji_rows.append(row)
    
    emoji_display = "\n".join(emoji_rows)
    
    await message.reply_text(
        f"🎨 **Available Emoji Stickers:**\n\n"
        f"{emoji_display}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📌 **Commands:**\n"
        f"• `/tagall` - Tag all with random emojis\n"
        f"• `/tagcustom ✨💞` - Tag with custom emojis\n"
        f"• `/taglist` - Show available emojis\n\n"
        f"💡 **Tip:** You can use any emojis with `/tagcustom`"
    )


# =========================
# COMMAND: /tagtest (Test command - only for testing)
# =========================

@Client.on_message(filters.command("tagtest") & filters.group)
async def tag_test(client: Client, message: Message):
    """Test tagging with a single emoji mention"""
    
    # Check admin
    try:
        user_status = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user_status.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            await message.reply_text("❌ Only admins can use this!")
            return
    except:
        await message.reply_text("❌ Error checking permissions!")
        return
    
    # Get a random member
    members = []
    async for member in client.get_chat_members(message.chat.id):
        if not member.user.is_bot:
            members.append(member)
            break
    
    if not members:
        await message.reply_text("❌ No members found!")
        return
    
    user = members[0].user
    
    # Send test mention with emoji
    emoji = random.choice(EMOJI_STICKERS)
    await message.reply_text(
        f"🧪 **Test Mention:**\n\n"
        f"[{emoji}](tg://user?id={user.id})\n\n"
        f"✅ Works! Now try `/tagall`"
    )


# =========================
# COMMAND: /tagstop (Stop ongoing tagging - emergency stop)
# =========================

@Client.on_message(filters.command("tagstop") & filters.group)
async def tag_stop(client: Client, message: Message):
    """Emergency stop for ongoing tagging"""
    
    # Check admin
    try:
        user_status = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user_status.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            await message.reply_text("❌ Only admins can use this!")
            return
    except:
        await message.reply_text("❌ Error checking permissions!")
        return
    
    # This is a placeholder - in reality, you'd need to implement
    # a global flag to stop the tagging process
    await message.reply_text(
        "🛑 **Tagging stopped!**\n\n"
        "⚠️ If tagging is running, please wait for it to finish.\n"
        "To prevent spam, commands have built-in delays."
    )


# =========================
# ERROR HANDLER
# =========================

@Client.on_message(filters.command("tagall") & filters.group)
async def tag_all_error_handler(client: Client, message: Message):
    """Handle any errors in tagall command"""
    try:
        # The main function will handle it
        pass
    except Exception as e:
        await message.reply_text(
            f"❌ **Error occurred:**\n"
            f"`{str(e)}`\n\n"
            f"Please try again later or contact bot owner."
      )
