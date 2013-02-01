TARGET=joosc
SOURCE=joosc.py

all:
	cp ${SOURCE} ${TARGET}
	chmod +x ${TARGET}
	
clean:
	rm -f ${TARGET} *.pyc

