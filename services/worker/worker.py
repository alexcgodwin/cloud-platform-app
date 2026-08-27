import os,time,redis
r=redis.from_url(os.getenv("REDIS_URL","redis://localhost:6379/0")); print("worker started",flush=True)
while True:
 job=r.brpop("jobs",timeout=5)
 if job: print("processed",job[1].decode(),flush=True)
 time.sleep(.2)
