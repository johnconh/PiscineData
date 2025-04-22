all: up postgres

up:
	docker compose up -d

down:
	docker compose -f docker-compose.yml down --rmi all --remove-orphans -v;

restart:
	docker compose restart

exec:
	-docker exec -it postgres bash

sed:
	-docker exec -it postgres sed -i 's/trust/scram-sha-256/g' /var/lib/postgresql/data/pg_hba.conf

postgres:
	-docker exec -it postgres psql -U jdasilva -d piscineds -h localhost -W

clean: down
	@yes | docker system prune -a -f
	@docker network prune -f

log:
	docker logs -f postgres

.PHONY: all up down exec postgres clean restart log sed