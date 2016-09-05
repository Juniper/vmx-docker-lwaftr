snabb: docker
	docker run -ti --rm -v $$PWD/build:/u buildsnabb
	cp build/src/snabb .
	md5sum snabb

docker:	build/Makefile
	docker build -t buildsnabb .

build/Makefile:	
	git clone -b igalia https://github.com/mwiget/snabb.git build
	#git clone -b lwaftr https://github.com/igalia/snabb.git build

clean:
	docker rmi buildsnabb 2>/dev/null || true 
	docker rmi `docker images | grep "^<none>" | awk '{print $3}'` 2>/dev/null || true 

distclean: clean
	echo "WARNING: this deletes the cloned snabb source directory build..."
	sleep 5
	rm -rf build
