
from __future__ import annotations

class Config:

    def __init__(self, config:dict = {}) -> None:
        self.mon_img_base = "/static/img/art" if 'monImgBase' not in config else config['monImgBase']
        self.google_tag = "" if 'googleTag' not in config else config['googleTag']
        self.live_refresh = 420 if 'liveRefresh' not in config else config['liveRefresh']

    def get_by_token(self, token:str) -> Any:
        if token == 'monImgBase':
            return self.mon_img_base
        if token == 'googleTag':
            return self.google_tag
        if token == 'liveRefresh':
            return self.live_refresh

        return False
