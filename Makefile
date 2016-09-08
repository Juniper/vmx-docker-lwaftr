vmxlwaftr: build/snabb build/qemu-v2.4.1-snabb.tgz
	mkdir build || true
	docker build -t $$(cat VERSION) .

build/snabb:
	$(MAKE) -C snabb
	cp snabb/build/src/snabb build/


build/qemu-v2.4.1-snabb.tgz:
	$(MAKE) -C qemu
	cp qemu/qemu-v2.4.1-snabb.tgz build/

clean:
	docker rmi `docker images | grep "^<none>" | awk '{print $$3}'` 2>/dev/null || true
	rm -rf build/snabb build/qemu-v2.4.1-snabb.tgz qemu/build snabb/build
