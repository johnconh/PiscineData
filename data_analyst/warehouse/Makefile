all: up warehouse jupyter flog

up:
	@docker-compose up -d postgres adminer

postgres:
	-docker exec -it postgres psql -U jdasilva -d piscineds -h localhost -W

warehouse:
	@docker-compose run --rm python python /app/warehouse/warehouse.py

jupyter:
	@docker-compose up -d jupyter

down:
	@docker compose -f docker-compose.yml down --rmi all --remove-orphans -v;

clean: down 
	@yes | docker system prune -a -f
	@docker network prune -f

log:
	@docker logs -f postgres

flog:
	@docker logs jupyter 2>&1 | grep -Eo 'http://127\.0\.0\.1:8888/\S+token=\S+' | tail -n 1

.PHONY: all up down clean flog log postgres jupyter warehouse