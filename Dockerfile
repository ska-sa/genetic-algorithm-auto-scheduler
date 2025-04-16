FROM python:3.10.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Start your script in the background and keep the container alive
CMD ["sh", "-c", "python main-v2.py & tail -f /dev/null"]


# Docker build command example
# docker build -t genetic-algorithm-scheduler .

# Docker run command example
# docker run -d genetic-algorithm-sheduler