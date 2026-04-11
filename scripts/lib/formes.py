from __future__ import annotations

import json


pokedex = {}
with open("data/common/pokedex.json") as file:
    pokedex = json.loads(file.read())


cosmetic_forms = {
    "tatsugiridroopy": "tatsugiri",
    "tatsugiristretchy": "tatsugiri",
}

# returns dex #, primary typing
def get_mon_data_from_code(mon_code:str) -> (int, str):
    if mon_code in pokedex:
        return pokedex[mon_code]['num'], pokedex[mon_code]['types'][0]
    
    if mon_code in cosmetic_forms:
        cosmetic_code = cosmetic_forms[mon_code]
        return pokedex[cosmetic_code]['num'], pokedex[cosmetic_code]['types'][0]

    return 0, ''

# same idea, but just returns the name
def get_mon_name_fromn_code(mon_code:str) -> str:
    if mon_code in pokedex:
        return pokedex[mon_code]['name']

    print(f"{mon_code} not found in pokedex")

    return ''


# for mapping alternate forms to images
# left out a lot of mons not legal in SV
# need to be mindful of what's in champs though!
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
    "oricoriopau": 10124,
    "oricoriopompom": 10123,
    "oricoriosensu": 10125,
    "lycanrocdusk": 10152,
    "lycanrocmidnight": 10126,
    # silvally -- todo probably?
    # minior?
    "necrozmadawnwings": 10156,
    "necrozmaduskmane": 10155,
    "necrozmaultra": 10157, # can't be in a teamsheet?
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
    "sandslashalola": 10102,
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
    "golemalola": 10111,
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
    "stunfiskgalar": 10180,
    "samurotthisui": 10236,
    "lilliganthisui": 10237,
    "yanmaskgalar": 10179,
    "zoruahisui": 10238,
    "zoroarkhisui": 10239,
    "braviaryhisui": 10240,
    "sliggoohisui": 10241,
    "goodrahisui": 10242,
    "avalugghisui": 10243,
    "decidueyehisui": 10244,
    "floetteeternal": 10060,

    # gmax forms can go here, if needed
    # 10196 -> 10228

    #MEGAS -- these won't be in teamsheets, but we might edit them in for asthetics
    "venusaurmega": 10033,
    "charizardmegax": 10034,
    "charizardmegay": 10035,
    "blastoisemega": 10036,
    "alakazammega": 10037,
    "gengarmega": 10038,
    "kangaskhanmega": 10039,
    "pinsirmega": 10040,
    "gyaradosmega": 10041,
    "aerodactylmega": 10042,
    "mewtwomegax": 10043,
    "mewtwomegay": 10044,
    "ampharosmega": 10045,
    "scizormega": 10046,
    "heracrossmega": 10047,
    "houndoommega": 10048,
    "tyranitarmega": 10049,
    "blazikenmega": 10050,
    "gardevoirmega": 10051,
    "mawilemega": 10052,
    "aggronmega": 10053,
    "medichammega": 10054,
    "magnetricmega": 10055,
    "banettemega": 10056,
    "absolmega": 10057,
    "garchompmega": 10058,
    "lucariomega": 10059,
    "abomasnowmega": 10060,
    "latiosmega": 10062,
    "latiasmega": 10063,
    "swampertmega": 10064,
    "sceptilemega": 10065,
    "sableyemega": 10066,
    "altariamega": 10067,
    "gallademega": 10068,
    "audinomega": 10069,
    "sharpedomega": 10070,
    "slowbromega": 10071,
    "steelixmega": 10072,
    "pidgeotmega": 10073,
    "glaliemega": 10074,
    "dianciemega": 10075, # not legal
    "metagrossmega": 10076,
    "kyogreprimal": 10077,
    "groudonprimal": 10078,
    "rayquazamega": 10079,
    "cameruptmega": 10087,
    "lopunnymega": 10088,
    "salamencemega": 10089,
    "beedrillmega": 10090,

    # NEW megas -- these likely need to be uploaded
    "clefablemega": 10278,
    "victreebelmega": 10279,
    "starmiemega": 10280,
    "dragonitemega": 10281,
    "meganiummega": 10282,
    "feraligatrmega": 10283,
    "skarmorymega": 10284,
    "froslassmega": 10285,
    "emboaremega": 10286,
    "excadrillmega": 10287,
    "scolipedemega": 10288,
    "scraftymega": 10289,
    "eeletrossmega": 10290,
    "chandeluremega": 10291,
    "chesnaughtmega": 10292,
    "delphoxmega": 10293,
    "greninjamega": 10294,
    "pyroarmega": 10295,
    "floettemega": 10296,
    "malamarmega": 10297,
    "barbariclemega": 10298,
    "dragalgemega": 10299,
    "hawluchamega": 10300,
    "zygardemega": 10301,
    "drampamega": 10302,
    "falinksmega": 10303,
    "raichumegax": 10304,
    "raichumegay": 10305,
    "chimecomega": 10306,
    "absolmegaz": 10307,
    "staraptormega": 10308,
    "lucariomegaz": 10309,
    "heatranmega": 10310,
    "darkraimega": 10311, # probably not legal
    "golurkmega": 10313,
    "meowsticmmega": 10314,
    "meowsticfmega": 10314,
    "crabominablemega": 10315,
    "golisopodmega": 10316,
    "magearnamega": 10317, # also not legal
    "zeraoramega": 10319, #samsies
    "scovillianmega": 10320,
    "glimmoramega": 10321,
    "tatsugirimega": 10324,
    "baxcaliburmega": 10325,
}

def get_mon_alt_from_code(mon_code:str) -> int | None:
    if mon_code in image_alts:
        return image_alts[mon_code]
    return None


"""
For when we want to display the fancy form icon!

These are forms that change in battle -- such as zacian... mons like palkia-orgin
or ogerpon change when the item is given to them, not during battle, so they get
put on the teamsheets as palkia-origin or ogerpon-wellspring whereas zacian is
on teamsheets as just base zacian holding the rusted sword.
"""
item_change_forms = {
    # zacian / zam
    "zacian": [{ "item": "Rusted Sword", "form": "zaciancrowned" }],
    "zamazenta": [{ "item": "Rusted Shield", "form": "zamazentacrowned" }],

    # megas
    "venusaur": [{ "item": "Venusaurite", "form": "venusaurmega" }],
    "charizard": [
        { "item": "Charizardite X", "form": "charizardmegax" },
        { "item": "Charizardite Y", "form": "charizardmegay" },
    ],
    "blastoise": [{ "item": "Blastoisinite", "form": "blastoisemega" }],
    "alakazam": [{ "item": "Alakazite", "form": "alakazammega" }],
    "gengar": [{ "item": "Gengarite", "form": "gengarmega" }],
    "kangaskhan": [{ "item": "Kangaskhanite", "form": "kangaskhanmega" }],
    "pinsir": [{ "item": "Pinsirite", "form": "pinsirmega" }],
    "gyarados": [{ "item": "Gyaradosite", "form": "gyaradosmega" }],
    "aerodactyl": [{ "item": "Aerodactylite", "form": "aerodactylmega" }],
    "mewtwo": [
        { "item": "Mewtwonite X", "form": "mewtwomegax" },
        { "item": "Mewtwonite Y", "form": "mewtwomegay" },
    ],
    "ampharos": [{ "item": "Ampharosite", "form": "ampharosmega" }],
    "scizor": [{ "item": "Scizorite", "form": "scizormega" }],
    "heracross": [{ "item": "Heracronite", "form": "heracrossmega" }],
    "houndoom": [{ "item": "Houndoominite", "form": "houndoommega" }],
    "tyranitar": [{ "item": "Tyranitarite", "form": "tyranitarmega" }],
    "blaziken": [{ "item": "Blazikenite", "form": "blazikenmega" }],
    "gardevoir": [{ "item": "Gardevoirite", "form": "gardevoirmega" }],
    "mawile": [{ "item": "Mawilite", "form": "mawilemega" }],
    "aggron": [{ "item": "Aggronite", "form": "aggronmega" }],
    "medicham": [{ "item": "Medichamite", "form": "medichammega" }],
    "manectric": [{ "item": "Manectite", "form": "manectricmega" }],
    "banette": [{ "item": "Banettite", "form": "banettemega" }],
    "absol": [
        { "item": "Absolite", "form": "absolmega" },
        { "item": "Absolite Z", "form": "absolmegaz" }
    ],
    "gharchomp": [
        { "item": "Garchompite", "form": "garchompmega" },
        { "item": "Garchompite Z", "form": "garchompmegaz" },
    ],
    "lucario": [
        { "item": "Lucarionite", "form": "lucariomega" },
        { "item": "Lucarionite Z", "form": "lucariomegaz" },
    ],
    "abomasnow": [{ "item": "Abomasite", "form": "abomasnowmega" }],
    "latios": [{ "item": "Latiosite", "form": "latiosmega" }],
    "latias": [{ "item": "Latiasite", "form": "latiasmega" }],
    "swampert": [{ "item": "Swampertite", "form": "swampertmega" }],
    "sceptile": [{ "item": "Sceptilite", "form": "sceptilemega" }],
    "sableye": [{ "item": "Sablenite", "form": "sableyemega" }],
    "altaria": [{ "item": "Altarianite", "form": "altariamega" }],
    "gallade": [{ "item": "Galladite", "form": "gallademega" }],
    "audino": [{ "item": "Audinite", "form": "audinomega" }],
    "sharpedo": [{ "item": "Sharpedonite", "form": "sharpedomega" }],
    "slowbro": [{ "item": "Slowbronite", "form": "slowbromega" }],
    "steelix": [{ "item": "Steelixite", "form": "steelixmega" }],
    "pidgeot": [{ "item": "Pidgeotite", "form": "pidgeotmega" }],
    "glalie": [{ "item": "Glalitite", "form": "glaliemega" }],
    "diancie": [{ "item": "Diancite", "form": "dianciemega" }],
    "metagross": [{ "item": "Metagrossite", "form": "metagrossmega" }],
    "kyogre": [{ "item": "Blue Orb", "form": "kyogreprimal" }],
    "groudon": [{ "item": "Red Orb", "form": "groudonprimal" }],
    "camerupt": [{ "item": "Cameruptite", "form": "cameruptmega" }],
    "lopunny": [{ "item": "Lopunnite", "form": "lopunnymega" }],
    "salamence": [{ "item": "Salamencite", "form": "salamencemega" }],
    "beedrill": [{ "item": "Beedrillite", "form": "beedrillmega" }],
    "clefable": [{ "item": "Clefablite", "form": "clefablemega" }],
    "victreebel": [{ "item": "Victreebelite", "form": "victreebelmega" }],
    "starmie": [{ "item": "Starminite", "form": "starmiemega" }],
    "dragonite": [{ "item": "Dragoninite", "form": "dragonitemega" }],
    "meganium": [{ "item": "Meganiumite", "form": "meganiummega" }],
    "feraligatr": [{ "item": "Feraligite", "form": "feraligatrmega" }],
    "skarmory": [{ "item": "Skarmorite", "form": "skarmorymega" }],
    "froslass": [{ "item": "Froslassite", "form": "froslassmega" }],
    "emboare": [{ "item": "Emboarite", "form": "emboaremega" }],
    "excadrill": [{ "item": "Excadrite", "form": "excadrillmega" }],
    "scolipede": [{ "item": "Scolipite", "form": "scolipedemega" }],
    "scrafty": [{ "item": "Scraftinite", "form": "scraftymega" }],
    "eeletross": [{ "item": "Eelektrossite", "form": "eeletrossmega" }],
    "chandelure": [{ "item": "Chandelurite", "form": "chandeluremega" }],
    "chesnaught": [{ "item": "Chesnaughtite", "form": "chesnaughtmega" }],
    "delphox": [{ "item": "Delphoxite", "form": "delphoxmega" }],
    "greninja": [{ "item": "Greninjite", "form": "greninjamega" }],
    "pyroar": [{ "item": "Pyroarite", "form": "pyroarmega" }],
    "floetteeternal": [{ "item": "Floettite", "form": "floettemega" }],
    "malamar": [{ "item": "Malamarite", "form": "malamarmega" }],
    "barbaricle": [{ "item": "Barbaracite", "form": "barbariclemega" }],
    "dragalge": [{ "item": "Dragalgite", "form": "dragalgemega" }],
    "hawlucha": [{ "item": "Hawluchanite", "form": "hawluchamega" }],
    "zygarde": [{ "item": "Zygardite", "form": "zygardemega" }],
    "drampa": [{ "item": "Drampanite", "form": "drampamega" }],
    "falinks": [{ "item": "Falinksite", "form": "falinksmega" }],
    "raichu": [
        { "item": "Raichunite X", "form": "raichumegax" },
        { "item": "Raichunite Y", "form": "raichumegay" }
    ],
    "chimeco": [{ "item": "Chimechite", "form": "chimecomega" }],
    "staraptor": [{ "item": "Staraptite", "form": "staraptormega" }],
    "heatran": [{ "item": "Heatranite", "form": "heatranmega" }],
    "darkrai": [{ "item": "Darkranite", "form": "darkraimega" }],
    "golurk": [{ "item": "Golurkite", "form": "golurkmega" }],
    "meowstic": [{ "item": "Meowsticite", "form": "meowsticmmega" }],
    "meowsticf": [{ "item": "Meowsticite", "form": "meowsticfmega" }],
    "crabominable": [{ "item": "Crabominite", "form": "crabominablemega" }],
    "golisopod": [{ "item": "Golisopite", "form": "golisopodmega" }],
    "magearna": [{ "item": "Magearnite", "form": "magearnamega" }],
    "zeraora": [{ "item": "Zeraorite", "form": "zeraoramega" }],
    "scovillian": [{ "item": "Scovillainite", "form": "scovillianmega" }],
    "glimmora": [{ "item": "Glimmoranite", "form": "glimmoramega" }],
    "tatsugiri": [{ "item": "Tatsugirinite", "form": "tatsugirimega" }],
    "tatsugiridroopy": [{ "item": "Tatsugirinite", "form": "tatsugirimega" }],
    "tatsugiristretchy": [{ "item": "Tatsugirinite", "form": "tatsugirimega" }],
    "baxcalibur": [{ "item": "Baxcalibrite", "form": "baxcaliburmega" }],
}

# rayquaza just has to be different
move_change_forms = {
    "rayquaza": { "move": "Dragon Ascent", "form": "rayquazamega" },
}

# similar, these change just upon entering the field with no special requirements
battle_change_forms = {
    "terapagos": "terapagosterastal",
}

def get_icon_alt(mon_code:str, mon_data:dict, megas_legal:bool) -> str:
    if mon_code in item_change_forms:
        for item_change in item_change_forms[mon_code]:
            if mon_data['item'] == item_change['item']:
                altform = item_change['form']
                if not altform.endswith('mega') or (altform.endswith('mega') and megas_legal):
                    return altform

    moves_key = 'moves'
    if 'badges' in mon_data:
        moves_key = 'badges'
    if 'attacks' in mon_data:
        moves_key = 'attacks'

    if megas_legal and mon_code in move_change_forms and move_change_forms[mon_code]['move'] in mon_data[moves_key]:
        return move_change_forms[mon_code]['form']

    if mon_code in battle_change_forms:
        return battle_change_forms[mon_code]

    return ""
