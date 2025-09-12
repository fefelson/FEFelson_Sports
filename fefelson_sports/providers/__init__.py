from typing import Optional

from .espn.espn_downloader import ESPNDownloadAgent, ESPNNCAAFDownloadAgent, ESPNNCAABDownloadAgent, ESPNNFLDownloadAgent
from .espn.normalizers.espn_mlb_normalizer import ESPNMLBNormalizer
from .espn.normalizers.espn_basketball_normalizer import ESPNBasketballNormalizer
from .espn.normalizers.espn_football_normalizer import ESPNFootballNormalizer

from .yahoo.yahoo_downloader import YahooDownloadAgent, YahooNCAABDownloadAgent, YahooNCAAFDownloadAgent, YahooNFLDownloadAgent
from .yahoo.normalizers.yahoo_basketball_normalizer import YahooBasketballNormalizer
from .yahoo.normalizers.yahoo_mlb_normalizer import YahooMLBNormalizer
from .yahoo.normalizers.yahoo_football_normalizer import YahooFootballNormalizer



default_provider = "yahoo"


def get_normal_agent(leagueId: str, provider: Optional[str]=None) -> "NormalAgent":
    if not provider:
        provider = default_provider

    return {"yahoo": {"NBA": YahooBasketballNormalizer,
                      "NCAAB": YahooBasketballNormalizer,
                      "MLB": YahooMLBNormalizer,
                      "NFL": YahooFootballNormalizer,
                      "NCAAF": YahooFootballNormalizer},
            
            "espn": {"NBA": ESPNBasketballNormalizer,
                      "NCAAB": ESPNBasketballNormalizer,
                      "MLB": ESPNMLBNormalizer,
                      "NFL": ESPNFootballNormalizer,
                      "NCAAF": ESPNFootballNormalizer}
            }[provider][leagueId](leagueId)



def get_download_agent(leagueId: str, provider: Optional[str]=None) -> "DownloadAgent":
    if not provider:
        provider = default_provider
    
    return {"yahoo": {"NBA": YahooDownloadAgent,
                      "NCAAB": YahooNCAABDownloadAgent,
                      "NFL": YahooNFLDownloadAgent,
                      "NCAAF": YahooNCAAFDownloadAgent,
                      "MLB": YahooDownloadAgent},
            
            "espn": {"NBA": ESPNDownloadAgent,
                      "NCAAB": ESPNNCAABDownloadAgent,
                      "NFL": ESPNNFLDownloadAgent,
                      "NCAAF": ESPNNCAAFDownloadAgent,
                      "MLB": ESPNDownloadAgent}

            }[provider][leagueId](leagueId)