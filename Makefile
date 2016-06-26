vmxlwaftr: qemu/qemu-v2.4.1-snabb.tgz snabb/snabb jet-1.tar.gz 
	mkdir build || true
	cp qemu/qemu-v2.4.1-snabb.tgz build
	cp snabb/snabb build
	tar zcf jetapp.tgz --exclude ".git" jetapp
	docker build -t $$(cat VERSION) .

jet-1.tar.gz:
	scp svpod1-vmm.englab.juniper.net:/volume/build/junos/16.1/release/16.1R1.6/ship/jet-1.tar.gz .

clean:
	docker rmi `docker images | grep "^<none>" | awk '{print $$3}'` 2>/dev/null || true
