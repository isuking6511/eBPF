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
