import logging
import os
import subprocess
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ================= KELOLA KONFIGURASI =================
BOT_TOKEN = "BOT_TOKEN"
ALLOWED_USER_ID = ID_TELEGRAM  # Ganti dengan User ID Telegram Anda (tipe data Integer)
# =======================================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def is_authorized(user_id: int) -> bool:
    """Memeriksa apakah pengirim pesan adalah pemilik bot."""
    return user_id == ALLOWED_USER_ID

def get_main_keyboard():
    """Membuat tombol menu utama yang selalu muncul di bawah chat."""
    keyboard = [
        [KeyboardButton("📋 Daftar Proses"), KeyboardButton("❓ Menu Utama / Bantuan")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return

    pesan_bantuan = (
        "🤖 *Server Control Bot Active*\n\n"
        "Gunakan tombol di bawah atau ketik perintah berikut:\n\n"
        "• `/ps` atau `/tasks` atau tombol *📋 Daftar Proses* - Menampilkan seluruh aplikasi berjalan\n"
        "• `/kill <nama/PID>` - Menghentikan aplikasi (contoh: `/kill notepad.exe`)\n"
        "• `/run <path_file.bat>` - Menjalankan file batch (contoh: `/run C:\\script\\backup.bat`)\n"
        "• `/cmd <perintah>` - Jalankan perintah CMD bebas"
    )
    # Menampilkan pesan bantuan + memasang ReplyKeyboard
    await update.message.reply_text(
        pesan_bantuan, 
        parse_mode="Markdown", 
        reply_markup=get_main_keyboard()
    )

async def list_processes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menampilkan SELURUH aplikasi/proses yang sedang berjalan (dipecah jika terlalu panjang)."""
    if not is_authorized(update.effective_user.id):
        return

    await update.message.reply_text("⏳ Mengambil daftar seluruh proses...")
    try:
        # Mengambil daftar seluruh proses di Windows
        cmd = 'tasklist /FO TABLE /NH'
        output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
        
        lines = output.strip().split('\n')
        
        # Karakter maks per pesan Telegram (aman di angka 3800 agar muat formatting markdown)
        MAX_CHUNK_SIZE = 3800 
        
        current_chunk = ""
        total_pesan = 0
        
        for line in lines:
            # Jika ditambah 1 baris ini melebihi batas, kirim chunk yang ada dulu
            if len(current_chunk) + len(line) + 1 > MAX_CHUNK_SIZE:
                total_pesan += 1
                await update.message.reply_text(f"```\n{current_chunk}\n```", parse_mode="Markdown")
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"
                
        # Kirim sisa chunk terakhir
        if current_chunk:
            total_pesan += 1
            await update.message.reply_text(
                f"```\n{current_chunk}\n```\n_Selesai. Total {len(lines)} proses ditampilkan dalam {total_pesan} pesan._", 
                parse_mode="Markdown",
                reply_markup=get_main_keyboard()
            )

    except Exception as e:
        await update.message.reply_text(f"❌ Gagal mengambil proses: {e}")

async def kill_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menghentikan aplikasi/proses."""
    if not is_authorized(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("⚠️ Gunakan format: `/kill <nama_proses/PID>`\nContoh: `/kill notepad.exe` atau `/kill 4520`", parse_mode="Markdown")
        return

    target = context.args[0]
    
    if target.isdigit():
        cmd = f'taskkill /F /PID {target}'
    else:
        if not target.endswith('.exe'):
            target += '.exe'
        cmd = f'taskkill /F /IM "{target}"'

    try:
        output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
        await update.message.reply_text(f"✅ *Sukses:*\n`{output.strip()}`", parse_mode="Markdown")
    except subprocess.CalledProcessError as e:
        await update.message.reply_text(f"❌ *Gagal/Proses tidak ditemukan:*\n`{e.output.strip()}`", parse_mode="Markdown")

async def run_bat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Memanggil dan menjalankan file .bat."""
    if not is_authorized(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("⚠️ Sertakan path lengkap file .bat!\nContoh: `/run C:\\Scripts\\start_app.bat`", parse_mode="Markdown")
        return

    bat_path = " ".join(context.args)

    if not os.path.exists(bat_path):
        await update.message.reply_text(f"❌ File tidak ditemukan pada path: `{bat_path}`", parse_mode="Markdown")
        return

    try:
        await update.message.reply_text(f"🚀 Menjalankan `{bat_path}`...", parse_mode="Markdown")
        
        # Eksekusi .bat non-blocking
        subprocess.Popen(f'"{bat_path}"', shell=True)
        
        await update.message.reply_text("✅ Perintah eksekusi .bat berhasil dikirim ke OS!")
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal menjalankan .bat: {e}")

async def run_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mengeksekusi perintah CMD bebas."""
    if not is_authorized(update.effective_user.id):
        return

    command = " ".join(context.args)
    if not command:
        await update.message.reply_text("⚠️ Masukkan perintah CMD.\nContoh: `/cmd dir C:\\`", parse_mode="Markdown")
        return

    try:
        output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
        if not output.strip():
            output = "Perintah berhasil dieksekusi (tanpa output)."
        
        # Jika output sangat panjang, kita bagi juga seperti daftar proses
        MAX_CHUNK_SIZE = 3800
        for i in range(0, len(output), MAX_CHUNK_SIZE):
            chunk = output[i:i + MAX_CHUNK_SIZE]
            await update.message.reply_text(f"```\n{chunk}\n```", parse_mode="Markdown")

    except subprocess.CalledProcessError as e:
        await update.message.reply_text(f"❌ *Error Executing:* \n`{e.output.strip()}`", parse_mode="Markdown")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Register Command Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler(["ps", "tasks"], list_processes))
    app.add_handler(CommandHandler("kill", kill_process))
    app.add_handler(CommandHandler("run", run_bat))
    app.add_handler(CommandHandler("cmd", run_cmd))

    # Register Text Listener (Untuk menangkap klik tombol keyboard)
    app.add_handler(MessageHandler(filters.Regex("^📋 Daftar Proses$"), list_processes))
    app.add_handler(MessageHandler(filters.Regex("^❓ Menu Utama / Bantuan$"), start))

    print("Bot Server Lokal berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()