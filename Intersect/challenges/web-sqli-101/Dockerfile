FROM python:3.12-slim

RUN pip install --no-cache-dir flask==3.0.3

WORKDIR /app
COPY app.py .

# Drop root as early as possible
RUN useradd -m chaluser
USER chaluser

EXPOSE 5000
CMD ["python", "app.py"]
