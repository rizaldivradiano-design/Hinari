import os
import sys
import json
import random
import subprocess
from io import BytesIO

fake = type(sys)('magic')
fake.from_buffer = lambda *a, **k: "image/jpeg"
fake.from_file = lambda *a, **k: "image/jpeg"
sys.modules['magic'] = fake

from neonize.client import NewClient
from neonize.types import MessageWithContext

client = NewClient("session.db")
games = {}
xp_data = {}
DONATE_LINK = "https://m.dana.id/n/link/minta?full_url=https://qr.dana.id/v1/281012012026090814007849"

if os.path.exists("xp.json"):
    try:
        xp_data = json.load(open("xp.json"))
    except:
        xp_data = {}

def save_xp():
    json.dump(xp_data, open("xp.json","w"))

def add_xp(jid, n=5):
    if jid not in xp_data:
        xp_data[jid] = {"xp":0,"level":1}
    xp_data[jid]["xp"] += n
    lvl = xp_data[jid]["xp"] // 100 + 1
    up = lvl > xp_data[jid]["level"]
    if up:
        xp_data[jid]["level"] = lvl
    save_xp()
    return up, lvl, xp_data[jid]["xp"]

def try_get_chess():
    try:
        import chess
        from PIL import Image, ImageDraw
        return chess, Image, ImageDraw, True
    except:
        return None, None, None, False

def render_board(board):
    chess, Image, ImageDraw, _ = try_get_chess()
    s = 70
    img = Image.new("RGB", (s*8, s*8), "white")
    draw = ImageDraw.Draw(img)
    light = (240, 217, 181)
    dark = (181, 136, 99)
    for r in range(8):
        for c in range(8):
            col = light if (r+c)%2==0 else dark
            draw.rectangle([c*s, r*s, (c+1)*s, (r+1)*s], fill=col)
    pmap = {"K":"♔","Q":"♕","R":"♖","B":"♗","N":"♘","P":"♙","k":"♚","q":"♛","r":"♜","b":"♝","n":"♞","p":"♟"}
    for sq in chess.SQUARES:
        pc = board.piece_at(sq)
        if pc:
            f = chess.square_file(sq)
            rk = 7 - chess.square_rank(sq)
            draw.text((f*s+20, rk*s+12), pmap.get(pc.symbol(), pc.symbol()), fill="black")
    bio = BytesIO()
    img.save(bio, format="PNG")
    return bio.getvalue()

def install_catur(chat):
    chat.send_message("⚠️ Catur belum terinstall\nSedang menginstall python-chess + pillow...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-chess", "pillow"])
        chat.send_message("✅ Catur berhasil diinstall, ketik .catur lagi")
    except:
        chat.send_message("❌ Gagal auto install, manual: pip install python-chess pillow")

def image_to_sticker(image_bytes, text=""):
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.open(BytesIO(image_bytes)).convert("RGBA")
        img.thumbnail((512,512))
        if text:
            draw = ImageDraw.Draw(img)
            w, h = img.size
            try:
                font = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
            except:
                font = ImageFont.load_default()
            draw.text((10, h-40), text, fill="white", stroke_width=3, stroke_fill="black", font=font)
        bio = BytesIO()
        img.save(bio, format="WEBP")
        return bio.getvalue()
    except:
        return None

def menu_art():
    return """
╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
┃ ⛩️ H I N A T A B O T ⛩️ ┃
┃ by Rizal | Gunung Edition ⛰️ ┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

╭─ 💎 DONATE SUPPORT ─╮
│.donate │ QR gunung + link dana
│.owner │ info owner
│.sewabot │ sewa bot
╰─────────────────────╯

╭─ ⭐ XP & LEVEL ─╮
│.xp.level.rank.leaderboard
│.afk alasan
╰────────────────╯

╭─ ♟️ MINIGAME HALAL ─╮
│.catur │ mulai gambar
│.catur D4 / e2 e4 │ jalan
│.ttt.ttt 5 │ tictactoe
│.suit.suit batu
│.tebakgambar.tebakangka
│.tekateki.asahotak.susunkata
│.siapaaku.caklontong.family100
│.math.truth.dare
╰────────────────────╯

╭─ 📱 HP KENTANG ─╮
│.optimasi.cekhp.bersihkan
│.boost.hematbaterai.ping
╰────────────────╯

╭─ 🎨 STIKER & FUN ─╮
│.s │ gambar jadi stiker
│.st Hai │ stiker + teks
│.joke.quotes.fakta.pantun
│.gombal.puisi.apakah.kapankah
│.rate.cekganteng.cekcantik
│.cekkhodam.jodoh.artinama
╰──────────────────╯
"""

@client.event
def on_message(chat, message: MessageWithContext):
    try:
        txt = ""
        img_bytes = None
        if message.Message.conversation:
            txt = message.Message.conversation
        elif message.Message.extendedTextMessage and message.Message.extendedTextMessage.text:
            txt = message.Message.extendedTextMessage.text
            if message.Message.extendedTextMessage.contextInfo and message.Message.extendedTextMessage.contextInfo.quotedMessage:
                q = message.Message.extendedTextMessage.contextInfo.quotedMessage
                if q.imageMessage:
                    try:
                        img_bytes = client.download_any(q)
                    except:
                        pass
        if message.Message.imageMessage:
            try:
                img_bytes = client.download_any(message.Message)
            except:
                pass
            if message.Message.imageMessage.caption:
                txt = message.Message.imageMessage.caption

        if not txt and not img_bytes:
            return

        low = (txt or "").lower().strip()
        jid = chat.jid
        user = jid.split("@")[0]
        up, lvl, xp = add_xp(jid, 7)

        if low == ".menu":
            chat.send_message(menu_art())
            return

        if low == ".donate":
            try:
                if os.path.exists("donate_gunung.png"):
                    chat.send_image(open("donate_gunung.png","rb").read())
                elif os.path.exists("/mnt/data/image_20261011_110443.webp"):
                    chat.send_image(open("/mnt/data/image_20261011_110443.webp","rb").read())
            except:
                pass
            chat.send_message(f"""
╭─ DONATE HINATA BOT ⛰️ ─╮
Makasih kak udah mau support bot 🥺

⛰️ Tema: Gunung misty biru
📱 Scan QR di atas atau klik link di bawah

🔗 Link Dana Statis:
{DONATE_LINK}

Seikhlasnya aja buat beli kuota biar bot 24 jam
Donatur dapet XP x2 + role premium

Makasih banyak 🙏
""")
            return

        if low == ".owner":
            chat.send_message("Owner: Rizal\nDonate link: " + DONATE_LINK)
            return

        if low == ".sewabot":
            chat.send_message("Sewa 10k/bulan, chat owner, bonus welcome + minigame + donate gunung")
            return

        if low == ".xp":
            chat.send_message(f"📊 XP @{user}\nLevel: {lvl}\nXP: {xp}/{lvl*100}")
            return

        if low in [".rank",".leaderboard",".level"]:
            if low == ".level":
                chat.send_message(f"Level lu {lvl} GG")
            else:
                top = sorted(xp_data.items(), key=lambda x: x[1]["xp"], reverse=True)[:10]
                teks = "🏆 TOP 10 XP\n"
                for i, (jid2, d) in enumerate(top,1):
                    teks += f"{i}. {jid2.split('@')[0]} - Lv{d['level']} {d['xp']}XP\n"
                chat.send_message(teks)
            return

        if low == ".s":
            if not img_bytes:
                chat.send_message("Kirim gambar + caption .s")
                return
            st = image_to_sticker(img_bytes)
            if st:
                chat.send_sticker(st)
            return

        if low.startswith(".st "):
            if not img_bytes:
                chat.send_message("Kirim gambar + .st Hai")
                return
            teks = txt.split(" ",1)[1]
            st = image_to_sticker(img_bytes, teks)
            if st:
                chat.send_sticker(st)
            return

        if low == ".catur" or low.startswith(".catur "):
            chess, Image, ImageDraw, ok = try_get_chess()
            if not ok:
                install_catur(chat)
                return
            if low == ".catur":
                b = chess.Board()
                games[jid] = b
                chat.send_image(render_board(b))
                chat.send_message("♟️ Papan baru\nPutih duluan\n.catur D4 atau .catur e2 e4")
                return
            if jid not in games:
                chat.send_message("Ketik .catur dulu")
                return
            brd = games[jid]
            mv_raw = low.replace(".catur ","").strip().lower()
            try:
                if len(mv_raw) == 2:
                    target = mv_raw
                    found = None
                    for m in brd.legal_moves:
                        if chess.square_name(m.to_square) == target:
                            found = m
                            break
                    if found:
                        brd.push(found)
                        chat.send_image(render_board(brd))
                        chat.send_message(f"Gas ke {target.upper()}")
                        if brd.is_checkmate():
                            add_xp(jid,50)
                            chat.send_message("CHECKMATE +50 XP")
                            del games[jid]
                        return
                    chat.send_message(f"Gak bisa ke {target.upper()}")
                    return
                m = brd.parse_uci(mv_raw)
                if m in brd.legal_moves:
                    brd.push(m)
                    chat.send_image(render_board(brd))
                    chat.send_message(f"{mv_raw} jalan")
                    add_xp(jid,10)
                    if brd.is_checkmate():
                        add_xp(jid,50)
                        chat.send_message("CHECKMATE GG")
                        del games[jid]
                else:
                    chat.send_message("Ilegal")
            except:
                chat.send_message("Format: .catur D4 atau .catur e2 e4")
            return

        if low == ".ttt":
            chat.send_message("⭕❌\n1|2|3\n4|5|6\n7|8|9\n.ttt 5")
            return

        if low.startswith(".ttt ") or low.startswith(".suit ") or low in [".suit",".tebakgambar",".tebakangka",".joke",".quotes",".fakta",".pantun",".gombal",".optimasi",".cekhp",".bersihkan",".boost",".hematbaterai",".ping"]:
            if low == ".ping":
                chat.send_message(f"Pong {random.randint(10,80)}ms")
            elif low == ".optimasi":
                chat.send_message("⚙️ Optimasi\n✔️ Cache 120MB bersih\n✔️ Ram lega 400MB")
            elif low == ".cekhp":
                chat.send_message(f"📱 HP @{user}\nRam 3/4GB\nStorage 80%")
            elif low == ".bersihkan":
                chat.send_message(f"🧹 Bersih {random.randint(80,300)}MB")
            elif low == ".boost":
                chat.send_message("🚀 Boost RAM berhasil")
            elif low == ".hematbaterai":
                chat.send_message("🔋 Hemat baterai aktif")
            else:
                chat.send_message(f"Fitur {low} aktif +10 XP")
            add_xp(jid,10)
            return

        if low.startswith(".apakah ") or low.startswith(".kapankah ") or low.startswith(".bisakah ") or low.startswith(".rate ") or low in [".cekganteng",".cekcantik",".cekkhodam"]:
            chat.send_message(f"{txt} = {random.randint(1,100)}%")
            return

        if up:
            chat.send_message(f"🎉 @{user} NAIK LEVEL {lvl}")

    except Exception as e:
        print(e)

@client.event
def on_group_participants_updated(chat, participants, action):
    try:
        if action == "add":
            for p in participants:
                chat.send_message(f"Welcome @{p.split('@')[0]} ✨\nKetik .menu\nDonate .donate ⛰️\nXP dari 0 ya")
        if action == "remove":
            for p in participants:
                chat.send_message(f"Bye @{p.split('@')[0]} 🥀")
    except:
        pass

print("Hinata bot Gunung Edition by Rizal")
print(f"Donate link: {DONATE_LINK}")
no = input("Nomor WA 62xxx: ").strip()
if not client.is_logged_in:
    code = client.pair_phone(no, show_push_notification=True)
    print(f"KODE LU: {code}")
else:
    print("Udah login")
client.connect()
client.loop.run_forever()
