
from redis import Redis

class CacheData():

    def __init__(self):
        self.redis = Redis(host='localhost', port=6379, db=0, decode_responses=True)

    def cache_event(self, year, event_code):
        data = ""
        try:
            with open(f"public/data/{year}/{event_code}.json") as file:
                data = file.read()
        except FileNotFoundError:
            return False

        self.redis.set(f"vgc-standings::api/v1/{year}/{event_code}", data)
        return True

    def cache_season(self, year):
        data = ""
        try:
            with open(f"public/data/{year}.json") as file:
                data = file.read()
        except FileNotFoundError:
            return False

        self.redis.set(f"vgc-standings::api/v1/{year}", data)
        return True

    # don't use this
    def keys(self):
        #return self.redis.get("vgc-standings::api/v1/2025/toronto")
        return self.redis.keys()
