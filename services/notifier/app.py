from fastapi import FastAPI, Request
import uvicorn, json, os
from prometheus_client import start_http_server, Counter

RCV = Counter('notifier_alerts_total', 'alerts received')
app = FastAPI()

@app.on_event('startup')
async def _s():
    start_http_server(int(os.getenv('METRICS_PORT', '9102')))

@app.post('/alert')
async def alert(req: Request):
    payload = await req.json()
    count = len(payload) if isinstance(payload, list) else 1
    RCV.inc(count)
    print("ALERT:", json.dumps(payload, ensure_ascii=False))
    return {"ok": True}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)
