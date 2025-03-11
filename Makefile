run:
	streamlit run app_streamlit.py

test:
	python3 -m pytest tests/

latest:
	docker pull ghcr.io/pmhalvor/radio_streamlit:latest
	docker compose up -d 
