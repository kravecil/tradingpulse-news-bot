from feeding.sources.base import BaseSource
from feeding.sources.cointelegraph import CointelegraphSource

RSS_SOURCES: list[type[BaseSource]] = [
    CointelegraphSource,
]

# [
#     # "https://cointelegraph.com/rss",  # CoinTelegraph
#     # "https://www.coindesk.com/arc/outboundfeeds/rss/",  # CoinDesk
#     # "https://decrypt.co/feed",  # Decrypt
#     # "https://thecryptobasic.com/feed/",  # The Crypto Basic
#     # "https://cryptopotato.com/feed/",  # CryptoPotato
# ]
