FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY lembramed ./lembramed
COPY scripts ./scripts
RUN python lembramed/manage.py collectstatic --noinput --settings=lembramed.build_settings
ENV DJANGO_SETTINGS_MODULE=lembramed.production_settings
CMD ["sh", "scripts/start.sh"]
