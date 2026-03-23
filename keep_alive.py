import os
from flask import Flask
from threading import Thread

app = Flask("")

@app.route("/")
def home():
    return "Bot is alive!"

def run():
    # Render sẽ tự cấp một cổng qua biến môi trường 'PORT'
    # Nếu không có (chạy máy cá nhân), nó sẽ mặc định dùng 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()
