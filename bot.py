TOKEN = '9204078607:AAEp6xe3UmwMZcCNH0S9MzmPmhtV0KtTYhg'
import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Railway se Token uthayen, agar wahan na mile toh fallback token use karein
TOKEN = os.environ.get('TELEGRAM_TOKEN', '9204078607:AAEp6xe3UmwMZcCNH0S9MzmPmhtV0KtTYhg')
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text:
        return

    query = update.message.text.strip()
    
    if not query.isdigit() or (len(query) != 11 and len(query) != 13):
        await update.message.reply_text("⚠️ Please send a valid 11-digit number or 13-digit CNIC.")
        return

    api_query = query
    if query.startswith('0'):
        api_query = '92' + query[1:]

    api_url = f"https://nexgen-tech-sim-api-v-01.vercel.app/api/search?number={api_query}"
    
    await update.message.reply_text("🔍 Fetching Data... ⏳")

    try:
        response = requests.get(api_url)
        
        if response.status_code != 200:
            await update.message.reply_text(f"⚠️ API Server Error: Status {response.status_code}")
            return
            
        data = response.json()

        if data.get('status') == 'success':
            result = data.get('result', {})
            sim_data = result.get('sim_data') or result.get('data') or []

            if not sim_data:
                await update.message.reply_text("❌ No records found in API response.")
                return

            truecaller_data = result.get('truecaller_data', [])
            
            final_message = "🛡️ **𝐕ᴏɪᴅ𝐗 𝐒𝐢𝐦 𝐃𝐚𝐭𝐚𝐛𝐚𝐬𝐞**\n"
            final_message += "━━━━━━━━━━━━━━━━━━━━\n\n"
            
            for idx, rec in enumerate(sim_data):
                num = rec.get('number', 'N/A')
                name = rec.get('name', 'N/A')
                cnic = rec.get('cnic', 'N/A')
                address = rec.get('address', 'N/A')
                network = rec.get('network', 'Unknown')
                
                for tc in truecaller_data:
                    if tc.get('number') == num and tc.get('name') and name == 'N/A':
                        name = tc.get('name')
                
                final_message += f"📌 **RECORD #{idx + 1}**\n"
                final_message += f"➔ **Number:**  `{num}`\n"
                final_message += f"➔ **Network:**  {network}\n"
                final_message += f"➔ **CNIC:**  `{cnic}`\n"
                final_message += f"➔ **Name:**  {name}\n"
                final_message += f"➔ **Address:**  {address}\n"
                final_message += "━━━━━━━━━━━━━━━━━━━━\n"
            
            final_message += "✅ *Powered by 𝐕ᴏɪᴅ𝐗*"
            
            await update.message.reply_text(final_message, parse_mode='Markdown')
                
        else:
            error_msg = data.get('message', 'No records found or API limit reached.')
            await update.message.reply_text(f"❌ API Error: {error_msg}")
            
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)[:150]}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot chal raha hai...")
    application.run_polling(close_loop=False, drop_pending_updates=True)
