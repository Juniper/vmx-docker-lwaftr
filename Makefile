vmxlwaftr: build 
#	cp -p snabb/src/snabb build/
#	cp -p it/dumb-init build/
#	cp -p qemu/qemu-v2.4.1-snabb.tgz build/
#	cp -p python-tools/python-tools.tgz build/
	docker build -t $$(cat VERSION) .

build:	Dockerfile.build
	docker build -f Dockerfile.build -t build .
	docker run -ti --rm -v $$PWD:/u build

python-tools/python-tools.tgz:
	$(MAKE) -C python-tools

build/b4cpe:
	$(MAKE) -C b4cpe
	touch build/b4cpe

clean:
	docker rmi build
	docker rmi `docker images | grep "^<none>" | awk '{print $$3}'` 2>/dev/null || true

