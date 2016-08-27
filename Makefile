vmxlwaftr: 
	mkdir build || true
	cp qemu/qemu-v2.4.1-snabb.tgz build
#	cp snabb/build/src/snabb build
	cp snabb-marcel/snabb/src/snabb build/
	docker build -t $$(cat VERSION) .

clean:
	docker rmi `docker images | grep "^<none>" | awk '{print $$3}'` 2>/dev/null || true
