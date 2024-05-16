init:
	git clone --recursive --branch release-v0.3_0.18 https://github.com/vtnerd/monero-lws
	git clone https://github.com/lalanza808/docker-monero-node
	git clone https://github.com/lalanza808/mymonero-web-js

release:
	docker-compose -f release.compose.yaml build
	docker tag monero-lw_mymonero-web lalanza808/mymonero-web:latest
	docker tag monero-lw_monero-lws lalanza808/lws:latest
	docker tag monero-lw_lwsadmin lalanza808/lwsadmin:latest
	docker push lalanza808/mymonero-web
	docker push lalanza808/lws
	docker push lalanza808/lwsadmin

prod-up:
	docker-compose -f prod.compose.yaml up -d

prod-down:
	docker-compose -f prod.compose.yaml down --remove-orphans

prod-logs:
	docker-compose -f prod.compose.yaml logs -f

dev-up:
	docker-compose -f dev.compose.yaml up -d

dev-down:
	docker-compose -f dev.compose.yaml down --remove-orphans

dev-logs:
	docker-compose -f dev.compose.yaml logs -f