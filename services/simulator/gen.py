import asyncio, json, os, random, time, argparse
from nats.aio.client import Client as NATS

NATS_URL = os.getenv('NATS_URL', 'nats://nats:4222')
SUBJECT = os.getenv('SUBJECT', 'telemetry.flow')

def rnd_ip():
    return ".".join(str(random.randint(1,254)) for _ in range(4))

async def run(mode="scan", seconds=10):
    nc = NATS(); await nc.connect(servers=[NATS_URL])
    t_end = time.time() + seconds
    src = rnd_ip()
    while time.time() < t_end:
        if mode == "scan":
            dport = random.choice([22,23,80,443,3306,8080,9000,6379,5432]) if random.random()<0.7 else random.randint(1,65535)
            evt = {"ts": time.time(), "pid": 0, "saddr": src, "daddr": rnd_ip(), "dport": dport}
        else:
            # benign
            evt = {"ts": time.time(), "pid": 0, "saddr": rnd_ip(), "daddr": rnd_ip(), "dport": random.choice([80,443,8080])}
        await nc.publish(SUBJECT, json.dumps(evt).encode())
        await asyncio.sleep(0.01 if mode=="scan" else 0.05)
    await nc.drain()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["scan","benign"], default="scan")
    ap.add_argument("--seconds", type=int, default=10)
    args = ap.parse_args()
    asyncio.run(run(args.mode, args.seconds))
