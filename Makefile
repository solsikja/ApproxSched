
SLN_PATH	:= dat/simple
PROG_PATH	:= src/main.py


all: $(SLN_PATH).res

$(SLN_PATH).tgff: $(SLN_PATH).tgffopt
	bin/tgff $(SLN_PATH)

$(SLN_PATH).lp: $(SLN_PATH).tgff
	python $(PROG_PATH) $(SLN_PATH)

$(SLN_PATH).res: $(SLN_PATH).lp
	bin/glpsol --lp $(SLN_PATH).lp -o $(SLN_PATH).res

clean:
	rm -rf dat/*.tgff dat/*.eps dat/*.vcg dat/*.lp dat/*.res
