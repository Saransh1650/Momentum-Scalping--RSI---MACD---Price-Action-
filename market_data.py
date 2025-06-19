from dataclasses import dataclass
from typing import List, Optional
import datetime
@dataclass
class MarketData:
    price: Optional[float]
    high: Optional[float]
    low: Optional[float]
    volume: Optional[float]
    bids: List[List[float]]
    asks: List[List[float]]
    timestamp: datetime.datetime
