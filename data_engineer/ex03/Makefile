all: up  exec

up:
	docker compose up -d

exec:
	bash automatic_table.sh

postgres:
	-docker exec -it postgres psql -U jdasilva -d piscineds -h localhost -W

down:
	docker compose -f docker-compose.yml down --rmi all --remove-orphans -v;

clean: down 
	@yes | docker system prune -a -f
	@docker network prune -f

log:
	docker logs -f postgres

.PHONY: all up down clean log volume exec postgres