from __future__ import annotations

import os
from dataclasses import dataclass

# === 設定管理クラス ===
# 環境変数を一箇所で管理するためのクラスです
# 使い方: from config import Config; print(Config.ECONOMY_SYMBOL)

@dataclass(frozen=True)
class Config:
    """Botの基本設定"""
    # 通貨の記号 (デフォルト: 🦢)
    ECONOMY_SYMBOL: str = os.getenv("ECONOMY_SYMBOL", "🦢")
    
    # 初期所持金
    STARTING_BALANCE: int = int(os.getenv("STARTING_BALANCE", "1000"))
    
    # デバッグモードの有効化
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # APIキーなどの外部設定が必要な場合はここに追加します
    # 例: OPENWEATHER_API_KEY: str | None = os.getenv("OPENWEATHER_API_KEY")