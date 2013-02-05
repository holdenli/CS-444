TARGET=joosc
SOURCE=joosc.py

all: ${TARGET}

${TARGET}: ${SOURCE} 
	cp ${SOURCE} ${TARGET}
	chmod +x ${TARGET}

test: ${TARGET}
	./${TARGET} -t

jlalr/:
	javac -d `pwd` Jlalr1.java

parsetable: jlalr/

clean:
	rm -rf ${TARGET} *.pyc jlalr/ __pycache__
