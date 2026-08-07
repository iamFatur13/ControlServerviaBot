# 🤖 Windows Server Remote Control via Telegram Bot

A simple, lightweight Python-based Telegram bot designed to manage Windows tasks and applications remotely. Built as a quick-response tool when traditional remote desktop tools fail.

---

## 📌 Latar Belakang

Seringkali kita menghadapi situasi frustrasi di mana sebuah Virtual Machine (VM) Windows tiba-tiba *hang* atau tidak merespons saat ingin diakses secara remote. 

Aplikasi remote desktop populer seperti **AnyDesk** maupun backup-nya seperti **RustDesk** bisa ikut *hang* atau *freeze* di waktu yang bersamaan. Penggunaan **UltraViewer** pun sering bermasalah dan *hang* jika dikonfigurasi menggunakan *permanent password* setelah beberapa kali pemakaian.

**Dampaknya:**
Ketika koneksi remote desktop terputus total, kita terpaksa harus membuka VM secara manual melalui console virtualization (ESXi/Proxmox/Hyper-V) hanya untuk menguji atau meng-kill aplikasi yang bermasalah. Jika jarak antara ruang kerja dan ruangan server/lokasi VM cukup jauh, alur kerja menjadi sangat terhambat dan membuang waktu.

**Solusinya:**
Terpikir untuk memanfaatkan API Telegram dengan membuat bot internal yang tetap bisa berkomunikasi dari internet ke server lokal via metode *polling* (tanpa butuh *port forwarding*). Cukup lewat chat Telegram di HP/PC, kita bisa langsung melihat daftar aplikasi yang berjalan, meng-kill proses yang *hang*, dan menjalankannya kembali semudah melakukan perpesanan biasa.

---

## ✨ Fitur Utama

- **📋 Monitoring Process List (`/ps`)**  
  Menampilkan seluruh daftar aplikasi/proses Windows yang sedang berjalan (`tasklist`). Dilengkapi dengan fitur *auto-chunking* (pesan dipecah otomatis jika melebihi batas karakter Telegram).
- **🛑 Force Kill Application (`/kill`)**  
  Menghentikan aplikasi/proses yang *hang* atau tidak merespons berdasarkan nama file (`.exe`) maupun PID (*Process ID*).
- **🛑 ScreenShoot  (`/shot`)**  
  Melakukan proses screenshot dari desktop aktif .
- **🚀 Run Batch File (`/run`)**  
  Memanggil dan menjalankan script `.bat` secara *non-blocking* untuk merestart/membuka kembali aplikasi yang dibutuhkan.
- **⚡ Fast Command Line (`/cmd`)**  
  Mengeksekusi perintah dasar Windows Command Prompt (CMD) secara fleksibel.
- **🔒 Akses Aman (Authorized Users Only)**  
  Menggunakan penguncian `ALLOWED_USER_ID`, sehingga bot **hanya akan merespon perintah dari ID Telegram pemilik**. Pesan dari orang lain otomatis diabaikan.
- **🔘 Menu Tombol Persisten**  
  Dilengkapi *Reply Keyboard* bawaan di layar chat untuk memanggil menu utama atau daftar proses dengan sekali tap.

---

## 🛠️ Prasyarat (Prerequisites)

1. **Python 3.8+** terinstall di PC Server / VM Windows.
2. Token Bot Telegram dari [@BotFather](https://t.me/BotFather).
3. Telegram User ID milik Anda dari [@userinfobot](https://t.me/userinfobot).

---

## 🚀 Langkah Instalasi & Penggunaan

### 1. Clone atau Download Repository
Download file `server_bot.py` atau clone repository ini ke folder server Anda:

<pre>
```bash
```
git clone [https://github.com/username-anda/windows-telegram-control-bot.git](https://github.com/username-anda/windows-telegram-control-bot.git)

cd windows-telegram-control-bot'
</pre>

### 2. Install Library Python
Buka Command Prompt (CMD) di server dan install library yang dibutuhkan:
<pre>
```python
'pip install python-telegram-bot pillow python-dotenv'
</pre>

### 3. Konfigurasi Bot

Buka file server_bot.py menggunakan text editor (Notepad, VS Code, dll), lalu ubah baris variabel berikut:

<pre>
```Python

# ================= KELOLA KONFIGURASI =================
BOT_TOKEN = "ISI_TOKEN_BOT_TELEGRAM_ANDA"
ALLOWED_USER_ID = 123456789  # Ganti dengan User ID Telegram Anda (Integer)
# =======================================================
</pre>

### 4. Menjalankan Bot

Jalankan bot melalui Command Prompt:

<Pre>
```Bash
python server_bot.py
</Pre>

## 📖 Panduan Perintah Chat Telegram

| Tombol / Perintah | Contoh Penggunaan | Fungsi |
| 📋 Daftar Proses atau /ps | /ps | Menampilkan seluruh proses yang berjalan |
| /kill | /kill anydesk.exe atau /kill 4520 | Mematikan proses berdasarkan nama/PID |
| /shot | Melakukan proses screenshot layar aktif
| /run | /run C:\Scripts\start_app.bat | Menjalankan file .bat |
| /cmd | /cmd ipconfig | Mengeksekusi perintah CMD bebas |
|❓ Menu Utama atau /start | /start | Menampilkan pesan bantuan & tombol menu |


## 💡 Tips Autostart (Jalan Otomatis saat Server Boots)

Agar bot tetap berjalan secara otomatis di background saat PC Server / VM dinyalakan:

Buka Task Scheduler di Windows.

Buat Create Basic Task -> beri nama Telegram Server Bot.

Set Trigger ke When the computer starts atau At log on.

Set Action ke Start a Program:

Program/script: pythonw.exe (Menggunakan pythonw agar jendela CMD tidak muncul)

Add arguments: server_bot.py

Start in: C:\path\ke\folder\bot\anda

## 📝 Catatan Tambahan
Aplikasi ini dikembangkan secara sederhana sesuai kebutuhan spesifik untuk manajemen darurat server/VM lokal. Dibuat ringan tanpa dependency yang rumit agar mudah dipasang di environment Windows apa saja.

.