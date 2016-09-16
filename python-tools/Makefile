snabb: docker
	docker run -ti --rm -v $$PWD:/u build-python-tools

docker:	
	docker build -t build-python-tools .

clean:
	docker rmi build-python-tools 2>/dev/null || true 

distclean: clean
	rm -f python-tools.tgz
	echo "done"
