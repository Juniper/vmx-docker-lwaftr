vmxlwaftr: build build/snabb build/qemu-v2.4.1-snabb.tgz build/dumb-init build/b4cpe
	cp -p snabb/build/src/snabb build/
	cp -p dumb-init/dumb-init build/
	cp -p qemu/qemu-v2.4.1-snabb.tgz build/
	docker build -t $$(cat VERSION) .

build:
	mkdir build

build/snabb:
	$(MAKE) -C snabb

build/dumb-init:
	$(MAKE) -C dumb-init

build/qemu-v2.4.1-snabb.tgz:
	$(MAKE) -C qemu

build/b4cpe:
	$(MAKE) -C b4cpe
	touch build/b4cpe

clean:
	$(MAKE) -C snabb clean
	$(MAKE) -C dumb-init clean
	$(MAKE) -C qemu clean
	docker rmi `docker images | grep "^<none>" | awk '{print $$3}'` 2>/dev/null || true

distclean: clean
	rm -rf build/* dumb-init/build qemu/build snabb/build
