.PHONY: clean install run test docker-build docker-run

clean:
	rm -rf venv

install:
	virtualenv venv
	. venv/bin/activate && pip install -r requirements.txt

run:
	. venv/bin/activate && python main.py

test:
	. venv/bin/activate && venv/bin/python test_with_manual_data.py
	. venv/bin/activate && venv/bin/python test_with_random_data.py
	. venv/bin/activate && venv/bin/python test_with_real_data.py

test-manual:
	. venv/bin/activate && venv/bin/python test_with_manual_data.py

test-random:
	. venv/bin/activate && venv/bin/python test_with_random_data.py

docker-build:
	docker build -t auto-scheduler .

docker-run:
	docker run -it auto-scheduler
