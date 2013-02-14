TARGET=joosc
SOURCE=joosc.py

all: ${TARGET} parsetable

pkg:
	zip -r pkg * -x 'assignment_testcases/*' -x '*__pycache__*'	

${TARGET}: ${SOURCE} 
	cp ${SOURCE} ${TARGET}
	chmod +x ${TARGET}

test: ${TARGET}
	./${TARGET} -t a1

jlalr/:
	javac -d `pwd` Jlalr1.java

parsetable: jlalr/
	python3 gen_parsetable.py | java jlalr.Jlalr1 > grammar.lr1

clean:
	rm -rf ${TARGET}
	rm -rf *.pyc */*.pyc __pycache__
