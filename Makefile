all: build b4cpe
	docker build -t $$(cat VERSION) .

build:	Dockerfile.build
	docker build -f Dockerfile.build -t build .
	docker run -ti --rm -v $$PWD:/u build

b4cpe: b4cpe/Dockerfile
	$(MAKE) -C b4cpe

clean:
	docker rmi build
	docker rmi `docker images | grep "^<none>" | awk '{print $$3}'` 2>/dev/null || true

