"""
given a number of competitors, return how many will earn points
"""
def get_points_threshold(competitors:int) -> int | None:
    if competitors >= 1024:
        return 512
    if competitors >= 512:
        return 256
    if competitors >= 256:
        return 128
    if competitors >= 128:
        return 64
    if competitors >= 80:
        return 32
    if competitors >= 48:
        return 16
    if competitors >= 8:
        return 8

    return None

"""
Get the champ points a player earned based on # of competitors and placement
"""
def get_points_earned(competitors:int, place:int, ic:bool = False) -> int | None:
    if place == 1:
        return 500 if ic else 200
    elif place == 2:
        return 400 if ic else 160
    elif place <= 4:
        return 320 if ic else 130
    elif place <= 8:
        return 250 if ic else 100
    elif place <= 16 and competitors >= 48:
        return 200 if ic else 80
    elif place <= 32 and competitors >= 80:
        return 160 if ic else 60
    elif place <= 64 and competitors >= 128:
        return 130 if ic else 50
    elif place <= 128 and competitors >= 256:
        return 100 if ic else 40
    elif place <= 256 and competitors >= 512:
        return 80 if ic else 30
    elif place <= 512 and competitors >= 1024:
        return 60 if ic else 20
    elif place <= 1024 and competitors >= 2046 and ic:
        return 50

    return 0
