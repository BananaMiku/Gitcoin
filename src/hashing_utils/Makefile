mine_cpu: mine_cpu.o sha1.o
	gcc -o mine_cpu mine_cpu.o sha1.o -lpython3.12

mine_cpu.o: mine_cpu.c sha1.h
	gcc \
		-c \
		-I/usr/include/python3.12 \
		-o mine_cpu.o \
		mine_cpu.c \

sha1.o: sha1.c sha1.h
	gcc -c -o sha1.o sha1.c

