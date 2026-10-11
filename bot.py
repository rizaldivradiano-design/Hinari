import os
import sys
import json
import time
import threading

fake = type(sys)('magic')
fake.from_buffer = lambda *a, **k: "image/jpeg"
fake.from_file = lambda *a, **k: "image/jpeg"
fake.from_buffer = fake.from_buffer
sys.modules['magic'] = fake

from flask import Flask, render_template_string, request, jsonify
from neonize.client import NewClient
from neonize.types import MessageWithContext

app = Flask(__name__)
pairing_code_global = "BELUM GENERATE"
client_obj = None
triggers = {}

if os.path.exists("db.json"):
    try:
        triggers = json.load(open("db.json"))
    except:
        triggers = {}

def save_db():
    json.dump(triggers, open("db.json","w"), ensure_ascii=False)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hinata bot</title>
<style>
body{margin:0;height:100vh;display:flex;align-items:center;justify-content:center;background:#0a0a0a;color:#fff;font-family:monospace}
.card{background:#151515;border:1px solid #222;border-radius:22px;padding:38px 26px;width:88%;max-width:340px;text-align:center}
h1{margin:0 0 24px 0;font-size:30px}
.btn{width:100%;background:#00ff9d;color:#000;border:none;padding:16px;border-radius:12px;font-weight:900;font-size:16px;cursor:pointer}
#kode{margin-top:18px;background:#000;border:1px dashed #00ff9d;padding:14px;border-radius:10px;color:#00ff9d;font-size:22px;letter-spacing:4px;display:none;cursor:pointer}
.dev{margin-top:24px;color:#888;font-size:13px}
#toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#00ff9d;color:#000;padding:10px 22px;border-radius:20px;font-weight:800;display:none}
</style>
</head>
<body>
<div class="card">
<h1>Hinata bot</h1>
<button class="btn" onclick="getKode()">Dapatkan kode</button>
<div id="kode" onclick="copyLagi()"></div>
<div class="dev">Developer: Rizal</div>
</div>
<div id="toast">disalin ke papan klip</div>
<script>
async function getKode(){
  let r = await fetch('/api/getcode');
  let d = await r.json();
  let box = document.getElementById('kode');
  box.style.display='block';
  box.innerText = d.code;
  await navigator.clipboard.writeText(d.code);
  let el = document.getElementById('toast');
  el.style.display='block';
  setTimeout(()=>el.style.display='none',2000);
}
async function copyLagi(){
  let t = document.getElementById('kode').innerText;
  await navigator.clipboard.writeText(t);
  let el = document.getElementById('toast');
  el.style.display='block';
  setTimeout(()=>el.style.display='none',2000);
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/api/getcode")
def getcode():
    return jsonify({"code": pairing_code_global})

def start_bot():
    global client_obj, pairing_code_global
    no = input("Nomor WA 62xxx: ").strip()
    client_obj = NewClient("session.db")

    @client_obj.event
    def on_message(chat, message: MessageWithContext):
        try:
            txt = ""
            if message.Message.conversation:
                txt = message.Message.conversation
            elif message.Message.extendedTextMessage and message.Message.extendedTextMessage.text:
                txt = message.Message.extendedTextMessage.text
            low = txt.lower()
            if low == ".menu":
                chat.send_message("Halo kak, aku Hinata")
                return
            if low in triggers:
                chat.send_message(triggers[low])
        except Exception as e:
            print(e)

    if not client_obj.is_logged_in:
        code = client_obj.pair_phone(no, show_push_notification=True)
        pairing_code_global = code
        print(f"KODE LU: {code}")
    else:
        pairing_code_global = "SUDAH LOGIN"
        client_obj.connect()
    client_obj.loop.run_forever()

if __name__ == "__main__":
    threading.Thread(target=start_bot, daemon=True).start()
    time.sleep(1)
    app.run(host="127.0.0.1", port=5000, use_reloader=False)