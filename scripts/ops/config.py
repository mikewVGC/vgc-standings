
from __future__ import annotations
from typing import Any

class Config:
    def __init__(self, config:dict = {}) -> None:
        self.mon_img_base = "/static/img/art"
        self.google_tag = ""
        self.live_refresh = 420
        self.mode = "dev"

        if 'monImgBase' in config:
            self.mon_img_base = config['monImgBase']

        if 'googleTag' in config:
            self.google_tag = config['googleTag']

        if 'liveRefresh' in config:
            self.live_refresh = config['liveRefresh']

        if 'mode' in config:
            self.mode = config['mode']

    def __dict__(self):
        return {
            "mon_img_base": self.mon_img_base,
            "google_tag": self.google_tag,
            "live_refresh": self.live_refresh,
            "mode": self.mode,
        }

    def get_by_token(self, token:str) -> Any:
        if hasattr(self, token):
            return getattr(self, token)

        if token == 'monImgBase':
            return self.mon_img_base
        if token == 'googleTag':
            return self.google_tag
        if token == 'liveRefresh':
            return self.live_refresh

        return False
