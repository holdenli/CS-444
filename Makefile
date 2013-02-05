TARGET=joosc
SOURCE=joosc.py

all: ${TARGET}

${TARGET}: ${SOURCE} 
	cp ${SOURCE} ${TARGET}
	chmod +x ${TARGET}

test:
	./scanner.py

jlalr/:
	javac -d `pwd` Jlalr1.java

parsetable: jlalr/

clean:
	rm -rf ${TARGET} *.pyc jlalr/ __pycache__
