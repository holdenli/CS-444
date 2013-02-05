TARGET=joosc
SOURCE=joosc.py

all:
	cp ${SOURCE} ${TARGET}
	chmod +x ${TARGET}

test:
	./scanner.py

clean:
	rm -f ${TARGET} *.pyc

