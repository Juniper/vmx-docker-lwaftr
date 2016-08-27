qemu: docker
	docker run -ti --rm -v $$PWD/build:/u buildqemu
	cp build/qemu-*-snabb.tgz .

docker:	build/Makefile
	docker build -t buildqemu .

build/Makefile:
	git clone -b v2.4.1 https://github.com/qemu/qemu.git build
#	git clone -b v2.5.1.1 https://github.com/qemu/qemu.git build
	cd build && patch -p1 < ../qemu-snabb.diff

clean:
	docker rmi buildqemu 2>/dev/null || true 
	docker rmi `docker images | grep "^<none>" | awk '{print $3}'` 2>/dev/null || true 

distclean: clean
	echo "WARNING: this deletes the cloned qemu source directory build..."
	sleep 5
	rm -rf build
