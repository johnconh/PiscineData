all: up warehouse

up:
	@docker-compose up -d postgres adminer

postgres:
	-docker exec -it postgres psql -U jdasilva -d piscineds -h localhost -W

warehouse:
	@docker-compose run --rm python python /app/warehouse/warehouse.py

run-ex00:
	@docker-compose up -d jupyter
	@docker exec jupyter jupytext --to notebook /app/ex00/pie.py
	@docker exec jupyter jupytext --to notebook /app/ex01/chart.py
	@docker logs jupyter 2>&1 | grep -Eo 'http://127\.0\.0\.1:8888/\S+token=\S+' | tail -n 1

run-ex01:
	@docker-compose run --rm python python /app/ex01/chart.py
	@echo "Press any key to continue..."
	@read key

run-ex02:
	@docker-compose run --rm python python /app/ex02/remove_duplicates.py
	@echo "Press any key to continue..."
	@read key

run-ex03:
	@docker-compose run --rm python python /app/ex03/fusion.py

run-all:run-ex00 run-ex01 run-ex02 run-ex03
	@echo "Todos los archivos se han ejecutado correctamente."

down:
	@docker compose -f docker-compose.yml down --rmi all --remove-orphans -v;

clean: down 
	@yes | docker system prune -a -f
	@docker network prune -f

log:
	@docker logs -f postgres


.PHONY: all up down clean log postgres run-ex00 run-ex01 run-ex02 run-ex03 run-all warehouse