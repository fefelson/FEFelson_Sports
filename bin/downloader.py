from pprint import pprint

from fefelson_sports.models.leagues import MLB, NBA, NCAAB, NCAAF, NFL

from fefelson_sports.utils.file_agent import PickleAgent





def main():

    league = MLB()
    league.update()
        





if __name__ == "__main__":

    main()
