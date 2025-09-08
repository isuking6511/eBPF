from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn, time, os, requests
import onnxruntime as ort
from prometheus_client import start_http_server, Histogram

MODEL_PATH = os.getenv('MODEL_PATH', '/models/model.onnx')
THRESHOLD = float(os.getenv('THRESHOLD', '0.7'))
ALERTMANAGER = os.getenv('ALERTMANAGER', 'http://alertmanager:9093/api/v2/alerts')
METRICS_PORT = int(os.getenv('METRICS_PORT', '9101'))

app = FastAPI()
INF = Histogram('infer_latency_ms', 'inference latency ms')
session = None
try:
    session = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])
except Exception:
    session = None

class Item(BaseModel):
    src: str
    conn_rate: float
    uniq_dports: int

class Batch(BaseModel):
    items: list[Item]

@app.on_event("startup")
async def _startup():
    start_http_server(METRICS_PORT)

@app.post('/infer')
def infer(batch: Batch):
    t0 = time.time()
    alerts = []
    for it in batch.items:
        score = simple_score(it) if session is None else onnx_score(it)
        if score >= THRESHOLD:
            alerts.append({
                'labels': {'alertname': 'AnomalyScoreHigh', 'src': it.src},
                'annotations': {'summary': f'score={score:.3f}', 'detail': f"rate={it.conn_rate}, uniq_dports={it.uniq_dports}"}
            })
    if alerts:
        try: requests.post(ALERTMANAGER, json=alerts, timeout=0.2)
        except Exception: pass
    INF.observe((time.time()-t0)*1000)
    return {'ok': True, 'alerts': len(alerts)}

def simple_score(it: Item) -> float:
    return min(1.0, 0.5*it.conn_rate + 0.05*it.uniq_dports)

def onnx_score(it: Item) -> float:
    X = [[it.conn_rate, float(it.uniq_dports)]]
    out = session.run(None, {session.get_inputs()[0].name: X})[0]
    return float(out[0][0])

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)
