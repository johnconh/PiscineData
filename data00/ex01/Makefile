all: up

up:
	docker compose up -d

down:
	docker compose -f docker-compose.yml down --rmi all --remove-orphans -v;

clean: down 
	@yes | docker system prune -a -f
	@docker network prune -f

log:
	docker logs -f postgres

.PHONY: all up down clean log