# Capstone: eBPF/Cloud-Native IDS (Sim-first)
목표: 운영 네트워크 공격·오동작을 수 초 내 탐지. 가시성→탐지→알림→대시보드 End-to-End.

## 스택
NATS JetStream, FastAPI, ONNX Runtime, scikit-learn/XGBoost, Prometheus, Grafana, Alertmanager, Loki, Docker.

## 빠른 시작
```bash
cp .env.example .env
make up
make demo     # 시뮬레이터가 포트스캔 패턴 생성 → 3초 내 알림
```
- Grafana: http://localhost:3000  (admin / admin)
- Prometheus: http://localhost:9090
- Alertmanager: http://localhost:9093
- NATS 모니터: http://localhost:8222

## 구조
Simulator → NATS(`telemetry.flow`) → Feature Extractor → Inferencer(ONNX) → Alertmanager(Webhook) → Notifier → Grafana

오프라인 학습(로컬): `training/train.py` → `models/model.onnx` → Inferencer가 마운트로 사용.

## 60일 계획
- Week1-2: 시뮬+파이프라인, 기본 대시보드, 알림 튜닝, 성능 계측.
- Week3-4: 공개 IDS 전처리, 1차 모델(XGB), PR-AUC≥0.6, TH@FPR1% 산출, ONNX 서빙.
- Week5-6: eBPF 에이전트 전환(옵션), 피처 확장, PR-AUC≥0.8, 대시보드 정제.
- Week7-8: 장애주입 SLO 검증, 보고서/발표 준비, 최종 데모 스크립트.

세부 일정과 KPI는 `docs/PLAN.md` 참조.



---
## docker compose -> 툴들 컨테이너 -> k8s로 마이그레이션 예정

## Makefile
up 빌드/기동, down 종료, logs 로그, demo 시뮬 이벤트 주입(→ docker compose run --rm simulator ...).

## services
	•	services/simulator/gen.py + Dockerfile
기능: 포트스캔 유사 이벤트 생성 후 NATS 공개.
입력: 없음. 실행 옵션 --mode scan|benign --seconds N.
출력 메시지(JSON, NATS telemetry.flow):

/code {"ts": 169..., "pid": 0, "saddr": "10.0.0.5", "daddr": "10.0.0.9", "dport": 80}


	•	services/feature-extractor/extractor.py + Dockerfile
기능: NATS 구독→2초 슬라이딩 윈도→피처 계산→추론 API 호출.
피처: conn_rate(초당 연결시도), uniq_dports(윈도 내 고유 목적지포트 수).
출력(HTTP POST /infer):

{"items":[{"src":"10.0.0.5","conn_rate":12.5,"uniq_dports":8}]}

메트릭(9100): fe_window_build_ms, fe_events_in.

	•	services/inferencer/app.py + Dockerfile
기능: ONNX Runtime로 점수화(모델 없으면 단순식). 임계(THRESHOLD) 이상이면 Alertmanager로 경보 POST.
점수식(모델 없을 때): min(1.0, 0.5*conn_rate + 0.05*uniq_dports)
입력: 위 배치 JSON. 출력: {"ok":true,"alerts":N}
Alertmanager로 보내는 페이로드 예:

[{"labels":{"alertname":"AnomalyScoreHigh","src":"10.0.0.5"},
  "annotations":{"summary":"score=0.91","detail":"rate=12.5, uniq_dports=8"}}]

메트릭(9101): infer_latency_ms 히스토그램.

	•	services/notifier/app.py + Dockerfile
기능: Alertmanager 웹훅 수신 /alert. 콘솔로 경보 출력.
메트릭(9102): notifier_alerts_total.

## configs
- configs/alertmanager/alertmanager.yml
		모든 알림을 http://notifier:8080/alert 로 전달.
- configs/prometheus/prometheus.yml
1초 간격 스크랩. 대상: feature-extractor:9100, inferencer:9101, notifier:9102.
- configs/grafana/provisioning/datasources/datasource.yml
데이터소스 등록: Prometheus, Loki.
- configs/grafana/provisioning/dashboards/ids.json
기본 패널 3개.
- Inference p95 latency(ms):
histogram_quantile(0.95, sum(rate(infer_latency_ms_bucket[1m])) by (le))
- Alerts received(1m): sum(increase(notifier_alerts_total[1m]))
- Feature window build ms(avg):
rate(fe_window_build_ms_sum[1m]) / rate(fe_window_build_ms_count[1m]) * 1000
- configs/loki/config.yml, configs/loki/promtail-config.yml
Loki 서버와 Promtail 스크래핑 설정(호스트 /var/log/*.log).

## tools
- tools/trafficgen/Dockerfile
tcpreplay, hping3 포함. 수동 부하·pcap 재생용.

## models / training
- models/
model.onnx 저장 위치(마운트로 inferencer가 로드).
- training/train.py
  자리표시자. 공개 IDS로 전처리→XGBoost 학습→ONNX 내보내기 흐름 템플릿.

## 실행 순서 요약

docker compose up -d --build alertmanager prometheus grafana loki promtail inferencer feature-extractor notifier
docker compose run --rm simulator python gen.py --mode scan --seconds 10
docker compose logs -f notifier inferencer feature-extractor

Grafana 3000, Alertmanager 9093에서 결과 확인.

## 핵심 환경변수
- NATS_URL 기본 nats://nats:4222
- THRESHOLD 기본 0.7 (민감도)
- ALERTMANAGER 기본 http://alertmanager:9093/api/v2/alerts
- GF_SECURITY_ADMIN_PASSWORD 기본 admin


