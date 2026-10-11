import os
import json
import time
import random
import threading
import base64
from flask import Flask, render_template_string, request, jsonify
from neonize.client import NewClient
from neonize.types import MessageWithContext

DB_FILE = "db_hinata.json"
QRIS_FILE = "qris_dana.jpg"
CAPTION_FILE = "caption_surga.json"
BAD_WORDS = ["anjing","babi","tolol","goblok","kontol","memek","ngentot","bangsat","jancok"]

app = Flask(__name__)
triggers = {}
client_obj = None
chess_games = {}
caption_surga = "masyaAllah kak 🥺\n\nmakasih ya udah mampir kesini\nsekecil apapun yang kakak kasih, Allah yang bales berkali lipat\n\nsemoga jadi amal jariyah yang ngalir terus\nsemoga rezeki kakak dilapangin, hati ditenangin, langkah diringanin menuju surga\n\nscan qris ini ya kak kalau berkenan\nikhlasnya aja, Allah Maha Melihat\n\njazakumullah khairan katsiran kak"

if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE,"r",encoding="utf-8") as f:
            triggers = json.load(f)
    except:
        triggers = {}

if os.path.exists(CAPTION_FILE):
    try:
        with open(CAPTION_FILE,"r",encoding="utf-8") as f:
            caption_surga = json.load(f).get("cap", caption_surga)
    except:
        pass

def is_bad(t):
    low = t.lower()
    for b in BAD_WORDS:
        if b in low:
            return True
    return False

def save_db():
    with open(DB_FILE,"w",encoding="utf-8") as f:
        json.dump(triggers,f,ensure_ascii=False)

def save_caption():
    with open(CAPTION_FILE,"w",encoding="utf-8") as f:
        json.dump({"cap": caption_surga}, f, ensure_ascii=False)

def get_menu_text():
    return (
        "halo kak, aku hinata 🥺\n"
        ".menu = liat ini\n"
        ".donate = donasi surga edition\n"
        ".s = reply gambar jadi stiker\n"
        ".catur = tebak angka 1-100\n"
        ".suit = suit gunting batu kertas\n"
        ".add trigger|jawaban = tambah auto respon\n"
    )

HTML = """<!DOCTYPE html><html><head><title>Bot WA - Hinata Core</title><meta name="viewport" content="width=device-width, initial-scale=1"><style>
body{background:#050505;color:#00ff9d;font-family:monospace;padding:15px}
.wm{position:fixed;top:10px;right:10px;background:#111;border:1px solid #00ff9d;padding:6px 12px;font-size:11px;z-index:9999}
.box{border:1px solid #00ff9d;padding:18px;margin-top:18px;background:#121212;border-radius:14px}
input,textarea,select{width:95%;background:#000;color:#00ff9d;border:1px solid #00ff9d;padding:12px;margin:8px 0;border-radius:8px}
button{background:#00ff9d;color:#000;border:none;padding:11px 18px;font-weight:800;cursor:pointer;border-radius:8px}
.grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}
@media(max-width:800px){.grid{grid-template-columns:1fr}}
.fake-log{font-size:11px;color:#555;height:100px;overflow:hidden;background:#000;padding:8px;border:1px dashed #222}
img.donasi{width:100%;max-width:420px;border-radius:12px;border:1px solid #00ff9d}
canvas{border:1px solid #00ff9d;background:#000;border-radius:8px;width:100%}
</style></head><body>
<div class="wm">Hinata - Dev magang - @bugcrashid - ONLINE</div>
<div id="loading"><h1>Bot WA - the lonely security</h1><p>loading... 3 detik ke /dashboard</p><div class="fake-log" id="fakeLog"></div></div>
<div id="dash" style="display:none">
<h1 style="margin-top:50px">Bot WA - Hinata <span style="font-size:12px;color:#555">v9.9.9</span></h1>
<p>Status: <span style="color:lime">TERHUBUNG - {{jid}}</span></p>
<div class="grid">
<div class="box"><h3>Sticker Lab PRO MAX</h3><input type="file" id="stikerFile" accept="image/*"><input id="stikerText" placeholder="teks atas"><input id="stikerBottom" placeholder="teks bawah"><canvas id="stikerCanvas" width="512" height="512"></canvas><br><button onclick="renderStiker()">RENDER</button><button onclick="downloadStiker()">DOWNLOAD</button><button onclick="kirimStikerKeBot()">KIRIM KE BOT</button></div>
<div class="box"><h3>Catur + Tebak + Suit</h3><button onclick="startCatur()">.catur</button><button onclick="startSuit()">.suit</button><div id="gameBoard" style="margin-top:12px;background:#000;padding:10px;border-radius:8px;min-height:100px;color:#666">belum ada game</div><input id="tebakInput" placeholder="angka 1-100 atau gunting/batu/kertas"><button onclick="kirimTebakan()">TEBAK</button><p id="tebakRes" style="color:lime"></p></div>
<div class="box"><h3>Donasi Surga</h3><img class="donasi" src="https://raw.githubusercontent.com/placeholder/qris/main/qris.png" onerror="this.src='data:image/svg+xml;base64,[STRIPPED]'"><textarea id="qrisCaption" rows="8">{{caption}}</textarea><button onclick="saveQrisCap()">SIMPAN CAPTION</button></div>
</div>
<div class="grid">
<div class="box"><h3>Trigger</h3><input id="p" placeholder="pemicu"><textarea id="j" placeholder="jawaban"></textarea><button onclick="add()">SIMPAN</button><p id="msg"></p></div>
<div class="box"><h3>List Trigger</h3><div id="list" style="max-height:300px;overflow:auto"></div></div>
<div class="box"><h3>Honeypot Pembobol</h3><div class="fake-log">DB_PASS=hinata123_gampang_bobol<br>FAKE_TOKEN=XXXX<br>root@hinata:~# sudo rm -rf /<br>lol gak bisa</div></div>
</div>
<div class="box" style="border-color:red"><h3 style="color:red">Shutdown</h3><button style="background:red;color:white" onclick="sd()">SAVE & MATIKAN</button></div>
<br><br><br></div>
<script>
let logs=["[OK] sticker module"," [OK] chess engine"," [WARN] blocked 182.1.xx"," [INFO] QRIS loaded"];let i=0;setInterval(()=>{let el=document.getElementById("fakeLog");if(el){el.innerHTML+=logs[i%logs.length]+"<br>";i++}},500);
setTimeout(()=>{if(location.pathname==="/"){location.href="/dashboard"}else{showDash()}},3000);if(location.pathname==="/dashboard"){showDash()}
function showDash(){document.getElementById("loading").style.display="none";document.getElementById("dash").style.display="block";load()}
async function add(){let p=document.getElementById("p").value;let j=document.getElementById("j").value;let r=await fetch("/api/add",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({pemicu:p,jawaban:j})});let d=await r.json();document.getElementById("msg").innerText=d.message;if(d.ok)load()}
async function load(){let r=await fetch("/api/list");let d=await r.json();let h="";for(let k in d){h+=`<div style="display:flex;justify-content:space-between;border-bottom:1px dashed #333;padding:6px 0"><span><b>${k}</b> => ${d[k].slice(0,80)}</span><button onclick="delT('${k}')" style="background:red;padding:2px 8px">X</button></div>`}document.getElementById("list").innerHTML=h||"kosong"}
async function delT(k){await fetch("/api/delete",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({pemicu:k})});load()}
async function sd(){if(!confirm("Simpan?"))return;document.body.innerHTML="<h1>Menyimpan... bye</h1>";await fetch("/api/shutdown",{method:"POST"})}
const canvas=document.getElementById("stikerCanvas");const ctx=canvas.getContext("2d");let imgObj=null;
document.getElementById("stikerFile").addEventListener("change",(e)=>{const file=e.target.files[0];const url=URL.createObjectURL(file);imgObj=new Image();imgObj.onload=()=>renderStiker();imgObj.src=url;});
function renderStiker(){ctx.fillStyle="#000";ctx.fillRect(0,0,512,512);if(imgObj){ctx.drawImage(imgObj,0,0,512,512);}const top=document.getElementById("stikerText").value;const bot=document.getElementById("stikerBottom").value;ctx.fillStyle="white";ctx.strokeStyle="black";ctx.lineWidth=6;ctx.font="bold 42px monospace";ctx.textAlign="center";if(top){ctx.strokeText(top,256,70);ctx.fillText(top,256,70);}if(bot){ctx.strokeText(bot,256,470);ctx.fillText(bot,256,470);}}
function downloadStiker(){const a=document.createElement("a");a.download="stiker.webp";a.href=canvas.toDataURL("image/webp");a.click();}
async function kirimStikerKeBot(){const data=canvas.toDataURL("image/webp");await fetch("/api/stiker",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({img:data})});alert("dikirim");}
function startCatur(){document.getElementById("gameBoard").innerHTML="tebak angka 1-100 aktif";}function startSuit(){document.getElementById("gameBoard").innerHTML="suit: gunting batu kertas";}
async function kirimTebakan(){let v=document.getElementById("tebakInput").value;let r=await fetch("/api/game",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({tebak:v})});let d=await r.json();document.getElementById("tebakRes").innerText=d.msg;}
async function saveQrisCap(){let c=document.getElementById("qrisCaption").value;await fetch("/api/save_caption",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({cap:c})});alert("kesimpen");}
</script></body></html>
"""

@app.route("/")
def idx():
    return render_template_string(HTML,jid="...", caption=caption_surga)

@app.route("/dashboard")
def dash():
    jid = str(client_obj.jid) if client_obj and hasattr(client_obj,"jid") else "connected"
    return render_template_string(HTML,jid=jid, caption=caption_surga)

@app.route("/api/add",methods=["POST"])
def api_add():
    d=request.json
    p=d.get("pemicu","").strip().lower()
    j=d.get("jawaban","").strip()
    if not p or not j:
        return jsonify({"ok":False,"message":"kosong"})
    if is_bad(p) or is_bad(j):
        return jsonify({"ok":False,"message":"kata kasar"})
    triggers[p]=j
    save_db()
    return jsonify({"ok":True,"message":"tersimpan"})

@app.route("/api/list")
def api_list():
    return jsonify(triggers)

@app.route("/api/delete",methods=["POST"])
def api_del():
    p=request.json.get("pemicu")
    if p in triggers:
        del triggers[p]
        save_db()
    return jsonify({"ok":True})

@app.route("/api/save_caption",methods=["POST"])
def api_save_cap():
    global caption_surga
    caption_surga = request.json.get("cap","").strip()
    if caption_surga:
        save_caption()
    return jsonify({"ok":True})

@app.route("/api/stiker",methods=["POST"])
def api_stiker():
    try:
        data = request.json.get("img","")
        if "," in data:
            b64 = data.split(",")[1]
            img_bytes = base64.b64decode(b64)
            with open("tmp_stiker_from_dash.webp","wb") as f:
                f.write(img_bytes)
        return jsonify({"ok":True})
    except Exception as e:
        return jsonify({"ok":False,"msg":str(e)})

@app.route("/api/game",methods=["POST"])
def api_game():
    teb = request.json.get("tebak","").lower()
    try:
        if teb.isdigit():
            ang = int(teb)
            target = random.randint(1,100)
            if ang == target:
                return jsonify({"msg": f"BENAR angka {target} masyaAllah"})
            elif ang < target:
                return jsonify({"msg": f"kekecilan, coba lebih gede dari {ang}"})
            else:
                return jsonify({"msg": f"kegedean, coba lebih kecil dari {ang}"})
        if teb in ["gunting","batu","kertas"]:
            bot = random.choice(["gunting","batu","kertas"])
            if teb == bot:
                return jsonify({"msg": f"seri aku juga {bot}"})
            win = (teb=="gunting" and bot=="kertas") or (teb=="batu" and bot=="gunting") or (teb=="kertas" and bot=="batu")
            if win:
                return jsonify({"msg": f"kamu menang aku {bot} kamu {teb}"})
            else:
                return jsonify({"msg": f"aku menang aku {bot} kamu {teb}"})
        return jsonify({"msg":"ketik angka 1-100 atau gunting/batu/kertas"})
    except Exception as e:
        return jsonify({"msg":str(e)})

@app.route("/api/shutdown",methods=["POST"])
def api_sd():
    def seq():
        try:
            if client_obj:
                client_obj.disconnect()
        except:
            pass
        time.sleep(1)
        os._exit(0)
    threading.Thread(target=seq).start()
    return jsonify({"ok":True})

def start_bot():
    global client_obj
    print("Bot WA - the lonely security")
    no = input("Masukin No WA 62xxx: ").strip()
    client_obj = NewClient("session_hinata.db")

    @client_obj.event
    def on_message(chat, message: MessageWithContext):
        try:
            txt = ""
            if message.Message.conversation:
                txt = message.Message.conversation
            elif message.Message.extendedTextMessage and message.Message.extendedTextMessage.text:
                txt = message.Message.extendedTextMessage.text
            elif message.Message.imageMessage and message.Message.imageMessage.caption:
                txt = message.Message.imageMessage.caption
            low = txt.lower().strip()

            if len(txt) > 1500 or txt.count("\n") > 50 or (len(set(txt)) < 5 and len(txt) > 300):
                chat.send_message("Anti Virtex aktif")
                return

            if low in [".menu","menu"]:
                chat.send_message(get_menu_text())
                return

            if low in [".donate","donasi"]:
                if os.path.exists(QRIS_FILE):
                    chat.send_image(QRIS_FILE,caption=caption_surga)
                else:
                    chat.send_message(caption_surga)
                return

            if low.startswith(".s") and message.Message.imageMessage:
                chat.send_message("membuat stiker bentar ya kak")
                try:
                    client_obj.download_any(message, "tmp.webp")
                    chat.send_sticker("tmp.webp")
                except Exception as e:
                    chat.send_message(f"gagal {e}")
                return

            if low == ".catur":
                target = random.randint(1,100)
                chess_games[chat.JID] = target
                chat.send_message("aku mikirin angka 1-100 kak, tebak pake.tebak 50")
                return

            if low.startswith(".tebak"):
                try:
                    ang = int(low.split()[1])
                    target = chess_games.get(chat.JID, 50)
                    if ang == target:
                        chat.send_message(f"masyaAllah benar kak angkanya {target}")
                        chess_games.pop(chat.JID, None)
                    elif ang < target:
                        chat.send_message("kekecilan kak coba lebih besar")
                    else:
                        chat.send_message("kegedean kak coba lebih kecil")
                except:
                    chat.send_message("format:.tebak 50")
                return

            if low.startswith(".suit"):
                try:
                    pil = low.split()[1] if len(low.split())>1 else ""
                    if pil not in ["gunting","batu","kertas"]:
                        chat.send_message("ketik.suit gunting / batu / kertas")
                        return
                    bot = random.choice(["gunting","batu","kertas"])
                    if pil == bot:
                        chat.send_message(f"seri kak aku juga {bot}")
                    else:
                        win = (pil=="gunting" and bot=="kertas") or (pil=="batu" and bot=="gunting") or (pil=="kertas" and bot=="batu")
                        if win:
                            chat.send_message(f"kak menang aku {bot} kakak {pil}")
                        else:
                            chat.send_message(f"aku menang aku {bot} kakak {pil}")
                except:
                    chat.send_message("ketik.suit gunting / batu / kertas")
                return

            if low.startswith(".add "):
                try:
                    isi = txt[5:]
                    pem,jaw = isi.split("|",1)
                    pem=pem.strip().lower()
                    jaw=jaw.strip()
                    if is_bad(pem) or is_bad(jaw):
                        chat.send_message("kata kasar terdeteksi")
                        return
                    triggers[pem]=jaw
                    save_db()
                    chat.send_message(f"trigger {pem} disimpan")
                except:
                    chat.send_message("format:.add halo|halo juga kak")
                return

            if low in triggers:
                chat.send_message(triggers[low])
                return

            if "halo" in low and len(low) < 20:
                chat.send_message("halo kak welcome ketik.menu ya")

        except Exception as e:
            print(f"Error {e}")

    @client_obj.event
    def on_group_join(group, user):
        try:
            group.send_message(f"welcome @{user} semoga betah\n{get_menu_text()}")
        except:
            pass

    if not client_obj.is_logged_in:
        try:
            code = client_obj.pair_phone(no, show_push_notification=True)
            print(f"\nKODE PAIRING: {code}\n")
        except Exception as e:
            print(f"Pair gagal {e}")
            client_obj.connect()
    else:
        client_obj.connect()

    client_obj.loop.run_forever()

if __name__ == "__main__":
    threading.Thread(target=start_bot,daemon=True).start()
    time.sleep(2)
    print("Buka 127.0.0.1:5000")
    app.run(host="127.0.0.1",port=5000,use_reloader=False)