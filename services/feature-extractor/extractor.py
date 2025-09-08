import asyncio, json, os, time
from collections import deque, defaultdict
from nats.aio.client import Client as NATS
from prometheus_client import start_http_server, Counter, Histogram
import requests

NATS_URL = os.getenv('NATS_URL', 'nats://nats:4222')
SUB_IN = os.getenv('SUB_IN', 'telemetry.flow')
INFER_URL = os.getenv('INFER_URL', 'http://inferencer:8080/infer')
WINDOW_SEC = int(os.getenv('WINDOW_SEC', '2'))
METRIC_PORT = int(os.getenv('METRIC_PORT', '9100'))

FEATS = Histogram('fe_window_build_ms', 'window build time ms')
PUB = Counter('fe_events_in', 'input events')

buf = deque()

async def main():
    start_http_server(METRIC_PORT)
    nc = NATS(); await nc.connect(servers=[NATS_URL])

    async def handler(msg):
        global buf
        PUB.inc()
        evt = json.loads(msg.data.decode())
        now = time.time()
        buf.append(evt)
        cutoff = now - WINDOW_SEC
        while buf and buf[0]['ts'] < cutoff:
            buf.popleft()
        t0 = time.time()
        by_src = defaultdict(int)
        dports = defaultdict(set)
        for e in buf:
            by_src[e['saddr']] += 1
            dports[e['saddr']].add(e['dport'])
        feats = []
        for s, cnt in by_src.items():
            feats.append({'src': s,'conn_rate': cnt / WINDOW_SEC,'uniq_dports': len(dports[s])})
        FEATS.observe((time.time()-t0)*1000)
        if feats:
            try: requests.post(INFER_URL, json={'items': feats}, timeout=0.2)
            except Exception: pass

    await nc.subscribe(SUB_IN, cb=handler)
    print('feature-extractor started')
    while True: await asyncio.sleep(1)

if __name__ == '__main__': asyncio.run(main())
