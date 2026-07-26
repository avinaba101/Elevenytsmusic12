# Elevenyts/plugins/tagall.py
# Complete Working Version - Copy Paste This Exact Code

import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

# =========================
# EMOJI STICKERS
# =========================

EMOJI_STICKERS = [
    "✨", "💞", "💖", "❣️", "👾", "🌝", "🌞", "🌛", 
    "😺", "🌟", "🔥", "💥", "💢", "💗", "🤍", 
    "💘", "🧡", "💜", "💝", "⭐", "🌙", "☀️", "🌈",
    "🎵", "🎶", "💫", "⚡", "🎯", "🏆", "👑", "💎"
]

EMOJI_COMBOS = [
    ["✨", "💞", "💖"], ["🌟", "🔥", "💥"], ["💫", "⚡", "🎯"],
    ["🌸", "🌺", "💐"], ["👑", "💎", "⭐"], ["🌈", "☀️", "🌙"],
    ["🎵", "🎶", "💜"], ["💗", "💘", "🧡"], ["🌝", "🌞", "🌛"],
    ["😺", "👾", "✨"], ["💞", "❣️", "💝"]
]

TAG_LIMIT = 30

# =========================
# TEST COMMAND
# =========================

@Client.on_message(filters.command("tagtest") & filters.group, group=1)
async def tag_test(client: Client, message: Message):
    """Test if plugin is working"""
    await message.reply_text("✅ **Tagall plugin is ALIVE and WORKING!**\n\nTry /tagall now!")

@Client.on_message(filters.command("tagtest") & filters.private, group=1)
async def tag_test_private(client: Client, message: Message):
    """Test in private"""
    await message.reply_text("✅ **Tagall plugin is working in private!**\n\nAdd me to a group as admin and try /tagall")

# =========================
# TAGALL COMMAND - GROUP
# =========================

@Client.on_message(filters.command("tagall") & filters.group, group=1)
async def tag_all(client: Client, message: Message):
    """Tag all members with emoji stickers"""
    
    try:
        # Send immediate acknowledgment
        await message.reply_text("⏳ **Processing /tagall...**")
        
        # Check if user is admin
        user_status = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user_status.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            await message.reply_text("❌ **Only admins can use this command!**")
            return
        
        # Check if bot is admin
        bot_status = await client.get_chat_member(message.chat.id, client.me.id)
        if bot_status.status not in [ChatMemberStatus.ADMINISTRATOR]:
            await message.reply_text("❌ **Bot needs to be admin to tag members!**")
            return
        
        # Send status
        status_msg = await message.reply_text("🔄 **Collecting members...**")
        
        # Get members (excluding bots)
        members = []
        async for member in client.get_chat_members(message.chat.id):
            if not member.user.is_bot:
                members.append(member)
        
        total = len(members)
        
        if total == 0:
            await status_msg.edit_text("❌ No members found!")
            return
        
        await status_msg.edit_text(f"🎯 **Tagging {total} members...**")
        
        # Process in batches
        processed = 0
        batch = []
        
        for member in members:
            user = member.user
            processed += 1
            
            # Random emoji combo
            emoji_combo = random.choice(EMOJI_COMBOS)
            emoji_str = "".join(emoji_combo)
            
            # Create mention
            mention = f"[{emoji_str}](tg://user?id={user.id})"
            batch.append(mention)
            
            if processed % 5 == 0:
                await status_msg.edit_text(f"📊 Progress: {processed}/{total}")
            
            if len(batch) >= TAG_LIMIT:
                await client.send_message(
                    message.chat.id,
                    "✨ **Member Stickers** ✨\n\n" + " ".join(batch)
                )
                batch = []
                await asyncio.sleep(1)
        
        # Send remaining
        if batch:
            await client.send_message(
                message.chat.id,
                "✨ **Member Stickers** ✨\n\n" + " ".join(batch)
            )
        
        await status_msg.delete()
        
        await message.reply_text(
            f"✅ **Successfully tagged {total} members!**\n\n"
            f"💫 Tagged with ❤️ by Elevenyts Bot"
        )
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# =========================
# TAGLIST COMMAND
# =========================

@Client.on_message(filters.command("taglist") & filters.group, group=1)
async def tag_list(client: Client, message: Message):
    """Show available emojis"""
    emoji_list = " ".join(EMOJI_STICKERS[:20])
    await message.reply_text(
        f"🎨 **Available Emoji Stickers:**\n\n"
        f"{emoji_list}\n\n"
        f"📌 **Commands:**\n"
        f"• `/tagall` - Tag all members\n"
        f"• `/taglist` - Show emojis\n"
        f"• `/tagtest` - Test plugin"
    )

# =========================
# PRIVATE CHAT HANDLER
# =========================

@Client.on_message(filters.command("tagall") & filters.private, group=1)
async def tag_all_private(client: Client, message: Message):
    """Tag all members - Private chat"""
    await message.reply_text(
        "❌ **This command only works in groups!**\n\n"
        "Add me to a group as admin and try again."
                                             )
