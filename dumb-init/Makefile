dumb-init: docker
	docker run -ti --rm -v $$PWD:/u build-dumb-init

docker:
	docker build -t build-dumb-init .

clean:
	docker rmi build-dumb-init 2>/dev/null || true 

distclean: clean
	echo "WARNING: this deletes the cloned snabb source directory build..."
	sleep 5
	rm -rf build
