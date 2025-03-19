from datetime import datetime

from api import Query, Planet

time = datetime(2025, 1, 1, 1)

query = Query(Planet.MARS, time)
print(query.get())
