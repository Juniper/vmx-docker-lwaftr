all: build b4cpe

build:	src/Dockerfile
	docker-compose build

up: build
	docker-compose up -d

ps:
	docker-compose ps

logs:
	docker logs $$(docker ps |grep _lwaftr|cut -d' ' -f1)

down:
	docker-compose down

shell:
	docker exec -ti $$(docker ps |grep _lwaftr|cut -d' ' -f1) bash

attach:
	./getpass.sh | grep lwaftr
	docker attach $$(docker ps |grep _lwaftr|cut -d' ' -f1) 

clean:
	docker system prune -f

