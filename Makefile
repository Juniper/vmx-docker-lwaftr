all: build b4cpe

build:	src/Dockerfile
	docker-compose build

buildclean: src/Dockerfile
	docker-compose build --no-cache

up: build
	docker-compose up -d

ps:
	docker-compose ps

query:
	@echo 
	@echo -n "xe0: "
	@docker exec -ti $$(docker ps |grep _lwaftr|cut -d' ' -f1) snabb lwaftr query xe0
	@echo 
	@echo -n "xe1: "
	@docker exec -ti $$(docker ps |grep _lwaftr|cut -d' ' -f1) snabb lwaftr query xe1


logs:
	docker logs -f $$(docker ps |grep _lwaftr|cut -d' ' -f1)

down:
	docker-compose down

shell:
	docker exec -ti $$(docker ps |grep _lwaftr|cut -d' ' -f1) bash

attach:
	./getpass.sh | grep lwaftr
	docker attach $$(docker ps |grep _lwaftr|cut -d' ' -f1) 

clean:
	docker system prune -f

