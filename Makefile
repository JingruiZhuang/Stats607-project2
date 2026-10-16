PYTHON := python3

RAW     := results/raw/estimates.csv
SUMMARY := results/raw/summary.csv
FIGURES := results/figures/.stamp

.PHONY: all simulate analyze figures test clean

all: figures

simulate: $(RAW)

$(RAW): src/simulation.py src/dgps.py src/methods.py src/config.py
	$(PYTHON) -m src.simulation --out $@

analyze: $(SUMMARY)

$(SUMMARY): $(RAW) src/analyze.py src/metrics.py
	$(PYTHON) -m src.analyze --raw $(RAW) --out $@

figures: $(FIGURES)

$(FIGURES): $(RAW) $(SUMMARY) src/figures.py
	$(PYTHON) -m src.figures --raw $(RAW) --summary $(SUMMARY) --outdir results/figures
	touch $@

test:
	$(PYTHON) -m pytest -q tests

clean:
	rm -f results/raw/*.csv results/raw/*.pkl
	rm -f results/figures/*.png results/figures/*.pdf results/figures/.stamp
	rm -rf __pycache__ src/__pycache__ tests/__pycache__ .pytest_cache
