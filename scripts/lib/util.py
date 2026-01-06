
import re
import unicodedata

# make player names URL friendly:
#  Chuppa Cross IV -> chuppa-cross-iv
#  Jérémy Côté     -> jeremy-cote
def make_code(name):
    coded = re.sub(r"[^\w-]+", '', name.lower().replace(' ', '-'))
    coded = unicodedata.normalize('NFKD', coded)
    return coded.encode('ascii', 'ignore').decode('utf-8')


# make a lookup code from a mon name
def make_mon_code(name):
    return re.sub(r"[^\w]+", '', name.lower())


# convert mon name from rk9 to showdown
def fix_mon_name(name):
    ignored = (
        "Male",
        "Unremarkable",
        "Family of Three",
        "Amped",
        "Curly",
        "Baile",
    )

    converted = {
        "Female": "F",
        "Paldean Form - Aqua Breed": "Paldea-Aqua",
        "Paldean Form - Blaze Breed": "Paldea-Blaze",
        "Paldean Form - Combat Breed": "Paldea-Combat",
        "Paldean": "Paldea",
        "Hisuian": "Hisui",
        "Galarian": "Galar",
        "Alolan": "Alola",
        "Family of Four": "Four",
    }

    monInfo = re.findall(r"([\w -]+)(\[(\w)\]){0,1}", name)
    fixedName = monInfo[0][0].strip()

    if len(monInfo) > 1:
        # this will have form/gender etc
        secondary = monInfo[1][0]
        if secondary.endswith(" Form"):
            secondary = secondary[:-5]
        elif secondary.endswith(" Style") or secondary.endswith(" Rotom"):
            secondary = secondary[:-6]

        if secondary in ignored:
            secondary = ""
        elif secondary in converted:
            secondary = converted[secondary]

        if len(secondary):
            fixedName = f"{fixedName}-{secondary}"

    return fixedName
