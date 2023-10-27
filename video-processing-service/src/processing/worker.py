from redis import Redis

r = Redis(host='localhost', port=6379, decode_responses=True)

while True:
    print(r.brpop("video_details")[1])


