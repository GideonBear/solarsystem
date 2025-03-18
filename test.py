from datetime import datetime

from api import Query, Planet, format_time

start_time = datetime(2025, 1, 1, 1)
stop_time = datetime(2025, 1, 1, 2)
step_size = "1hour"

query = Query(Planet.MARS, start_time, stop_time, step_size)
print(query.get())
