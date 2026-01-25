
def download():
    base_url = "https://pairings.playlatam.net/refresh-pairings/_id_/2/_round_"
    ...

def parse():
    ...

def main():

    parser = argparse.ArgumentParser(
        prog="python3 hawlucha.py",
        description="Hawlucha is a rudimentaty script for scraping playlatam",
    )
    parser.add_argument('--id', help="The ID of the event on playlatam")
    parser.add_argument('--rounds', help="The number of rounds to download/parse")
    parser.add_argument('--download', action="store_true", help="Force download, otherwise the files in the cache will be parsed")

    cl = parser.parse_args()

    print("All done!")

main()
