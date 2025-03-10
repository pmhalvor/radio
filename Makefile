run:
	python app_flask.py & streamlit run app_streamlit.py

run-streamlit:
	export API_HOST=0.0.0.0 && streamlit run app_streamlit.py

run-flask:
	python app_flask.py

docker-flask:
	docker build -t radio_flask:alpha -f Dockerfile.flask .
	docker run radio_flask:alpha

docker-flask-stop:
	docker ps | grep radio_flask | xargs docker stop
	# docker stop $(docker ps -a -q --filter ancestor=radio_flask:alpha)

test:
	python3 -m pytest tests/