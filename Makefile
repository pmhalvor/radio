run:
	python app.py & streamlit run app_streamli.py

run-flask:
	python app.py

docker-flask:
	docker build -t radio_flask:alpha -f Dockerfile.flask .
	docker run radio_flask:alpha

docker-flask-stop:
	docker ps | grep radio_flask | xargs docker stop
	# docker stop $(docker ps -a -q --filter ancestor=radio_flask:alpha)