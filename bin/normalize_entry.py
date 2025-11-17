from collections import defaultdict
from os import environ, walk
from pprint import pprint

from fefelson_sports.utils.file_agent import PickleAgent
from fefelson_sports.utils.logging_manager import get_logger



from fefelson_sports.analytics import MLBAnalytics, NFLAnalytics, NCAAFAnalytics, NBAAnalytics, NCAABAnalytics

def main():

    a = NCAAFAnalytics()
    a.scheduled_analytics()



        
       
    
                                

if __name__ == "__main__":
    main()
