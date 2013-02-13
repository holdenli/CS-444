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

rules/generated.py:
	python3 rules/gen_rules.py < rules/generate.rules > rules/generated.py

parsetable: jlalr/ rules/generated.py
	python3 gen_parsetable.py | java jlalr.Jlalr1 > grammar.lr1

clean:
	rm -rf ${TARGET}
	rm -rf *.pyc */*.pyc __pycache__
	rm -rf jlalr/ rules/generated.py
