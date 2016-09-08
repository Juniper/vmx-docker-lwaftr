vmxlwaftr: build build/snabb build/qemu-v2.4.1-snabb.tgz build/dumb-init build/b4cpe
	docker build -t $$(cat VERSION) .

build:
	mkdir build

build/snabb:
	$(MAKE) -C snabb
	cp snabb/build/src/snabb build/

build/dumb-init:
	$(MAKE) -C dumb-init
	cp dumb-init/dumb-init build/

build/qemu-v2.4.1-snabb.tgz:
	$(MAKE) -C qemu
	cp qemu/qemu-v2.4.1-snabb.tgz build/

build/b4cpe:
	$(MAKE) -C b4cpe
	touch build/b4cpe

clean:
	docker rmi `docker images | grep "^<none>" | awk '{print $$3}'` 2>/dev/null || true
	rm -rf build/* dumb-init/build qemu/build snabb/build
