.PHONY: up down logs demo bench seed fmt test
up:
	docker compose up -d --build
	sleep 2
	@echo "Grafana http://localhost:3000"

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

demo:
	# 포트스캔 유사 이벤트 생성
	docker compose exec -T simulator python gen.py --mode scan --seconds 10

bench:
	# SYN flood (네트워크 부하 예시)
	docker compose exec -T trafficgen hping3 grafana -S -p 80 --flood || true

seed:
	# pcap 재생 (있을 때)
	docker compose exec -T trafficgen sh -c "test -f /pcaps/sample_attack.pcap && tcpreplay -i eth0 /pcaps/sample_attack.pcap || true"
