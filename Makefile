.PHONY: install run test clean
install:
	python -m pip install -r requirements.txt
run:
	streamlit run app.py
test:
	python -m pytest -q
clean:
	rm -rf __pycache__ .pytest_cache nexus/__pycache__ nexus/ui/__pycache__
