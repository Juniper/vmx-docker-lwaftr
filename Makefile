all: build 

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
	@docker exec -ti $$(docker ps |grep _lwaftr|cut -d' ' -f1) \
	  snabb lwaftr query xe0 >/dev/null \
	  && docker exec -ti $$(docker ps |grep _lwaftr|cut -d' ' -f1) \
	  snabb lwaftr query xe0 || echo "(missing)"
	@echo 
	@echo -n "xe1: "
	@docker exec -ti $$(docker ps |grep _lwaftr|cut -d' ' -f1) \
	  snabb lwaftr query xe1 >/dev/null \
	  && docker exec -ti $$(docker ps |grep _lwaftr|cut -d' ' -f1) \
	  snabb lwaftr query xe1 || echo "(missing)"
	@echo 
	@echo -n "xe2: "
	@docker exec -ti $$(docker ps |grep _lwaftr|cut -d' ' -f1) \
	  snabb lwaftr query xe2 >/dev/null \
	  && docker exec -ti $$(docker ps |grep _lwaftr|cut -d' ' -f1) \
	  snabb lwaftr query xe2 || echo "(missing)"
	@echo 
	@echo -n "xe3: "
	@docker exec -ti $$(docker ps |grep _lwaftr|cut -d' ' -f1) \
	  snabb lwaftr query xe3 >/dev/null \
	  && docker exec -ti $$(docker ps |grep _lwaftr|cut -d' ' -f1) \
	  snabb lwaftr query xe3 || echo "(missing)"

logs:
	docker logs -f $$(docker ps -a|grep _lwaftr|cut -d' ' -f1)

down:
	docker-compose down

shell:
	docker exec -ti $$(docker ps |grep _lwaftr|cut -d' ' -f1) bash

attach:
	./getpass.sh | grep lwaftr
	docker attach $$(docker ps |grep _lwaftr|cut -d' ' -f1) 

cpe:
	docker exec -ti $$(docker ps | grep b4cpe|cut -d' ' -f1) bash

clean:
	docker system prune -f

