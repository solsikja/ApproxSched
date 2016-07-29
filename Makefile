
SLN_PATH	:= dat/simple
GENLP_PATH	:= src/genlp.py
GENSVG_PATH	:= src/genoffline.py


all: $(SLN_PATH).svg

$(SLN_PATH).svg: $(SLN_PATH).res
	python3.5 $(GENSVG_PATH) $(SLN_PATH)

$(SLN_PATH).res: $(SLN_PATH).lp
	bin/glpsol --lp $(SLN_PATH).lp -o $(SLN_PATH).res

$(SLN_PATH).lp: $(SLN_PATH).tgff
	python3.5 $(GENLP_PATH) $(SLN_PATH)

$(SLN_PATH).tgff: $(SLN_PATH).tgffopt
	bin/tgff $(SLN_PATH)


clean:
	rm -rf dat/*.tgff dat/*.eps dat/*.vcg dat/*.lp dat/*.res dat/*.svg
