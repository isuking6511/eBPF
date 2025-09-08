# Architecture
```
[Simulator/eBPF] -> NATS(telemetry.flow) -> FeatureExtractor(window) -> Inferencer(ONNX, TH) -> Alertmanager(Webhook) -> Notifier
                                                                                 |
                                                                                Prometheus <-> Grafana
Logs -> Promtail -> Loki -> Grafana
```
