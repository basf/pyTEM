from datetime import datetime

epoch_us = 1655112197284907  # Epoch in microseconds
epoch_s = epoch_us / 1000000  # Epoch in seconds

date_time = datetime.fromtimestamp(epoch_s)

print(date_time)

# Extract date and time
print(date_time.date())
print(date_time.time())
