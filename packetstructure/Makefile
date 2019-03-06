all: structure.md structure.h structure.py

structure.md: genmarkdown.py structure.def
	python $<

structure.h: genstruct.py structure.def
	python $<

structure.py: genpython.py structure.def
	python $<

clean:
	-rm structure.py
	-rm structure.md
	-rm structure.h