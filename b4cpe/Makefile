generator: 
#	cp ../snabb/build/src/snabb .
#	cp ../dumb-init/dumb-init .
	docker build -t $$(cat VERSION) .

clean:
	docker rmi `docker images | grep "^<none>" | awk '{print $$3}'` 2>/dev/null || true
