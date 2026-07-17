FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r apps/api/requirements.txt
ENV PYTHONPATH=/app/apps/api
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
