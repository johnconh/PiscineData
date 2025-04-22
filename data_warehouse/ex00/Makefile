all: up

up:
	@docker-compose up -d postgres adminer

postgres:
	-docker exec -it postgres psql -U jdasilva -d piscineds -h localhost -W

run-ex01:
	@docker-compose run --rm python python /app/ex01/customers_table.py
	@echo "Presiona cualquier tecla para continuar..."
	@read key

run-ex02:
	@docker-compose run --rm python python /app/ex02/remove_duplicates.py
	@echo "Presiona cualquier tecla para continuar..."
	@read key

run-ex03:
	@docker-compose run --rm python python /app/ex03/fusion.py

run-all: run-ex01 run-ex02 run-ex03
	@echo "Todos los archivos se han ejecutado correctamente."

down:
	@docker compose -f docker-compose.yml down --rmi all --remove-orphans -v;

clean: down 
	@yes | docker system prune -a -f
	@docker network prune -f

log:
	@docker logs -f postgres

.PHONY: all up down clean log volume  postgres run-ex01 run-ex02 run-ex03 run-all