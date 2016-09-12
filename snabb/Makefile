snabb: docker build
	docker run -ti --rm -v $$PWD/build:/u buildsnabb
	cp build/src/snabb .
	md5sum snabb

build:
	mkdir build

docker:	build/Makefile
	docker build -t buildsnabb .

build/Makefile:	
	git clone -b lwaftr https://github.com/igalia/snabb.git build

clean:
	docker rmi buildsnabb 2>/dev/null || true 

distclean: clean
	echo "WARNING: this deletes the cloned snabb source directory build..."
	sleep 5
	rm -rf build
