
import json


pokedex = {}
with open("data/common/pokedex.json") as file:
    pokedex = json.loads(file.read())


# return dex #, primary typing
def get_mon_data_from_code(mon_code):
    if mon_code in pokedex:
        return pokedex[mon_code]['num'], pokedex[mon_code]['types'][0]
    
    if mon_code in cosmetic_forms:
        cosmetic_code = cosmetic_forms[mon_code]
        return pokedex[cosmetic_code]['num'], pokedex[cosmetic_code]['types'][0]

    return 0, ''


# for mapping alternate forms to images
# left out a lot of mons not legal in SV
image_alts = {
    "taurospaldeacombat": 10250,
    "taurospaldeaaqua": 10252,
    "taurospaldeablaze": 10251,
    # castform -- not in SV
    # deoxys -- not VGC legal
    # burmy / wormadam -- not in SV
    "shelloseast": "422-e",
    "gastrodoneast": "423-e",
    "rotomfan": 10011,
    "rotomfrost": 10010,
    "rotomheat": 10008,
    "rotomwash": 10009,
    "rotommow": 100012,
    "dialgaorigin": 10245,
    "palkiaorigin": 10246,
    "giratinaorigin": 10007,
    # shaymin -- not VGC legal
    # arceus -- not VGC legal
    "basculinbluestriped": 10016,
    "basculinwhitestriped": 10247,
    "basculegionf": 10248,
    "darumakagalar": 10176,
    "darmanatangalar": 10177,
    "deerlingautumn": "585-a",
    "deerlingsummer": "585-s",
    "deerlingwinter": "585-w",
    "sawsbuckautumn": "586-a",
    "sawsbucksummer": "586-s",
    "sawsbuckwinter": "586-w",
    "tornadustherian": 10019,
    "thundurustherian": 10020,
    "landorustherian": 10021,
    "enamorustherian": 10249,
    "kyuremblack": 10022,
    "kyuremwhite": 10023,
    # keldeo
    # meloetta
    # genesect
    # greninja (???)
    # vivilion -- do I actually want to do this?
    "meowsticf": 10025,
    "zygarde10": 10118,
    "zygardecomplete": 10120,
    # hoa
    "oricoriopau": 10124,
    "oricoriopompom": 10123,
    "oricoriosensu": 10125,
    "lycanrocdusk": 10152,
    "lycanrocmidnight": 10126,
    # silvally
    # minior?
    "necrozmadawnwings": 10156,
    "necrozmaduskmane": 10155,
    # megearna
    "toxtricitylowkey": 10184,
    "indeedeef": 10186,
    "zaciancrowned": 10188,
    "zamazentacrowned": 10189,
    "urshifurapidstrike": 10191,
    # zarude
    "calyrexshadow": 10194,
    "calyrexice": 10193,
    "ursalunabloodmoon": 10272,
    "oinkolognef": 10254,
    "mausholdfour": 10257, # need to fix ts
    "squawkabillyblue": 10260,
    "squawkabillywhite": 10261,
    "squawkabillyyellow": 10262,
    "palafinhero": 10256,
    "tatsugiridroopy": 10258,
    "tatsugiristretchy": 10259,
    "dudunsparcethreesegment": 10255,
    "gimmighoulroaming": 10263,
    "poltchageistartisan": None,
    "sinistchamasterpiece": None,
    "ogerponhearthflame": 10274,
    "ogerponwellspring": 10273,
    "ogerponcornerstone": 10275,
    "terapagosstellar": 10275,
    "unfezantf": "521-f",
    "frillishf": "592-f",
    "jellicentf": "593-f",
    "pyroarf": "668-f",
    # ratatta
    # raticate
    "raichualola": 10100,
    "sandshrewalola": 10101,
    "sandshrewalola": 10102,
    "vulpixalola": 10103,
    "ninetalesalola": 10104,
    "diglettalola": 10105,
    "dugtrioalola": 10106,
    "meowthalola": 10107,
    "meowthgalar": 10161,
    "persianalola": 10108,
    "growlithehisui": 10229,
    "arcaninehisui": 10230,
    "geodudealola": 10109,
    "graveleralola": 10110,
    "golemalola": 1011,
    "ponytagalar": 10162,
    "rapidashgalar": 10163,
    "slowpokegalar": 10164,
    "slowbrogalar": 10165,
    "slowkinggalar": 10172,
    "farfetchdgalar": 10166,
    "grimeralola": 10112,
    "mukalola": 10113,
    "voltorbhisui": 10231,
    "electrodehisui": 10232,
    "exeggutoralola": 10114,
    "marowakalola": 10115,
    "weezinggalar": 10167,
    "mrmimegalar": 10168,
    "articunogalar": 10169,
    "zapdosgalar": 10170,
    "moltresgalar": 10171,
    "typhlosionhisui": 10233,
    "wooperpaldea": 10253,
    "qwilfishhisui": 10234,
    "sneaselhisui": 10235,
    "corsolagalar": 10173,
    "zigzagoongalar": 10174,
    "linoonegalar": 10175,
    "samurotthisui": 10236,
    "lilliganthisui": 10237,
    "yanmaskgalar": 10179,
    "zoruahisui": 10238,
    "zoroarkhisui": 10239,
    # stunfisk
    "braviaryhisui": 10240,
    "sliggoohisui": 10241,
    "goodrahisui": 10242,
    "avalugghisui": 10243,
    "decidueyehisui": 10244,
}

cosmetic_forms = {
    "tatsugiridroopy": "tatsugiri",
    "tatsugiristretchy": "tatsugiri",
}


def get_mon_alt_from_code(mon_code):
    if mon_code in image_alts:
        return image_alts[mon_code]
    return None
