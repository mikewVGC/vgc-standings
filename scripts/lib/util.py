
import datetime
import re
import unicodedata

from urllib.parse import quote


# make player names URL friendly:
#  Chuppa Cross IV -> chuppa-cross-iv
#  Jérémy Côté     -> jeremy-cote
def make_code(name):
    if len(name.strip()) == 0:
        return ""

    coded = name.encode('utf-8').decode('unicode_escape')
    coded = re.sub(r"[^\w-]+", '', coded.lower().replace(' ', '-'))
    coded = unicodedata.normalize('NFKD', coded)
    coded = coded.encode('ascii', 'ignore').decode('utf-8')

    # likely non-western characters, so we'll just url encode
    if len(coded.replace('-', '')) == 0:
        return quote(name)

    return coded


# make a lookup code from a mon name
def make_mon_code(name):
    return re.sub(r"[^\w]+", '', name.lower())


# convert to showdown item code: Covert Cloak -> covertcloak
def make_item_code(name):
    return re.sub(r"[^\w]+", '', name.lower().replace(' ', ''))


# convert mon name from rk9 to showdown
# this is missing anything not present in SV
def fix_mon_name(name):
    # these are "default" for multi-forme mons on Showdown
    # they get removed: Urshifu [Single Strike Form] -> Urshifu
    ignored = (
        "Male",
        "Unremarkable",
        "Counterfeit",
        "Family of Three",
        "Amped",
        "Curly",
        "Baile",
        "Single Strike",
        "Midday",
        "Incarnate",
        "Teal",
        "Green", # Squawkabilly
        "Red-Striped",
        "Chest",
    )

    # convert map -> rk9: Showdown
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
        "Rapid Strike": "Rapid-Strike",
    }

    # these are present in rk9 but not in Showdown names
    # basically if a name ends with this, chop it off
    chopped = (
        "Form",
        "Forme",
        "Mask",
        "Style",
        "Rotom",
        "Rider",
        "Plumage",
        "Kyurem",
    )

    monInfo = re.findall(r"([\w -]+)(\[(\w)\]){0,1}", name)
    fixedName = monInfo[0][0].strip()

    if len(monInfo) > 1:
        # this will have form/gender etc
        secondary = monInfo[1][0]

        for chop in chopped:
            if secondary.endswith(f" {chop}"):
                secondary = secondary[:-(len(chop)+1)]
                break

        if secondary in ignored:
            secondary = ""
        elif secondary in converted:
            secondary = converted[secondary]

        if len(secondary):
            fixedName = f"{fixedName}-{secondary}"

    return fixedName


# makes the "________ the XXXX season!" string on the homa page
def make_season_info_str(majors):
    total = len(majors)
    complete = len(list(filter(lambda major: major['processed'] == True, list(majors.values()))))
    upcoming = len(list(filter(lambda major: major['processed'] == False, list(majors.values()))))

    if complete == 0:
        return "We're getting ready for the first events of"

    if complete <= 4:
        return "We've just started"

    if upcoming <= 6 and upcoming > 3:
        return "We're getting closer to the end of"

    if upcoming <= 3 and upcoming > 1:
        return "We're nearly done with"

    if upcoming == 1:
        return "With only Worlds to go, we've almost wrapped up"

    if upcoming <= 0:
        return "We've completed"

    return "We are currently in the middle of"


# get first, last, and worlds from a list of majors
def get_season_bookends(majors):
    major_codes = list(majors.keys())
    first_major = majors[major_codes[0]]
    last_major = majors[major_codes[len(major_codes) - 2]]
    worlds = majors[major_codes[len(major_codes) - 1]]

    return first_major, last_major, worlds


# this makes lame-o 2025-10-15 - 2025-10-17 style dates into coolio Oct. 15 - 17, 2025 style
def make_nice_date_str(start, end, separator = '-', use_full_months = False):
    start_dt = datetime.datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.datetime.strptime(end, "%Y-%m-%d")

    month_code = '%b'
    if use_full_months == True:
        month_code = '%B'

    start_year = start_dt.strftime('%Y')
    end_year = end_dt.strftime('%Y')
    start_month = start_dt.strftime(month_code)
    start_day = int(start_dt.strftime('%d'))
    end_month = end_dt.strftime(month_code)
    end_day = int(end_dt.strftime('%d'))

    if use_full_months == False:
        if start_month != 'May':
            start_month = f"{start_month}."
        if end_month != 'May':
            end_month = f"{end_month}."

    insert_start_year = ''
    if start_year != end_year:
        insert_start_year = f", {start_year}"

    nice_str = f"{start_month} {start_day}{insert_start_year} {separator} {end_day}"
    if start_month != end_month:
        nice_str = f"{start_month} {start_day}{insert_start_year} {separator} {end_month} {end_day}"

    return f"{nice_str}, {end_year}"

