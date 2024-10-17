import redis

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Define the pattern for session keys (e.g., all keys starting with 'session:')
pattern = 'session:*'

# SCAN and delete keys in batches
cursor = '0'
while cursor != 0:
    cursor, keys = r.scan(cursor=cursor, match=pattern, count=1000)
    if keys:
        r.delete(*keys)

print("Deleted session keys with long names.")
