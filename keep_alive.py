from __future__ import annotations

import os
import logging
from threading import Thread

from flask import Flask

# === Flaskサーバーの設定 ===
# KoyebやRenderなどのホスティングサービスでBotを常時起動させるためのWebサーバーです
app = Flask(__name__)

# Werkzeugのログをエラーのみに制限してコンソールを綺麗に保ちます
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def home() -> tuple[str, int]:
    """ルートパスへのアクセスに応答"""
    return "SwanEconomy Bot is running!", 200

@app.route('/health')
def health() -> tuple[str, int]:
    """ヘルスチェック用エンドポイント"""
    return "OK", 200

def run() -> None:
    """サーバーを実行"""
    # 環境変数 PORT があればそれを使用し、なければ 8080 を使用します
    port = int(os.getenv("PORT", "8080"))
    app.run(host='0.0.0.0', port=port)

def keep_alive() -> None:
    """別スレッドでWebサーバーを起動"""
    t = Thread(target=run)
    t.daemon = True
    t.start()