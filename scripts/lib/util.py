
import datetime
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


# makes the empty part of the "________ the XXXX season!" string on the homa page
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

