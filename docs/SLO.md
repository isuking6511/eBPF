# SLO
- ROC-AUC≥0.96 (최종), FPR=1%에서 Precision≥0.9
- p95 추론 지연 ≤ 300ms
- Agent CPU ≤ 5%, 드롭률=0
Prometheus 예시식: `histogram_quantile(0.95, sum(rate(infer_latency_ms_bucket[5m])) by (le)) < 300`
