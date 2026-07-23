"""
given a number of competitors, return how many will earn points
"""
def get_points_threshold(competitors:int) -> int | None:
    if competitors >= 2049:
        return 1024
    if competitors >= 1025:
        return 512
    if competitors >= 513:
        return 256
    if competitors >= 257:
        return 128
    if competitors >= 129:
        return 64
    if competitors >= 65:
        return 32
    if competitors >= 33:
        return 16
    if competitors >= 17:
        return 8
    if competitors >= 8:
        return 4
    if competitors >= 4:
        return 2

    return None

"""
Get the champ points a player earned based on # of competitors and placement
"""
def get_points_earned(competitors:int, place:int, ic:bool = False) -> int | None:
    if place == 1:
        return 500 if ic else 350
    elif place == 2 and competitors >= 4:
        return 480 if ic else 325
    elif place <= 4 and competitors >= 8:
        return 420 if ic else 300
    elif place <= 8 and competitors >= 17:
        return 380 if ic else 280
    elif place <= 16 and competitors >= 33:
        return 300 if ic else 200
    elif place <= 32 and competitors >= 65:
        return 240 if ic else 160
    elif place <= 64 and competitors >= 129:
        return 180 if ic else 120
    elif place <= 128 and competitors >= 257:
        return 140 if ic else 80
    elif place <= 256 and competitors >= 513:
        return 100 if ic else 60
    elif place <= 512 and competitors >= 1025:
        return 85 if ic else 45
    elif place <= 1024 and competitors >= 2049:
        return 42 if ic else 22

    return 0
