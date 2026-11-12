# Literal historical course rubric. This tag contains Python 3.7.4 on Debian Stretch.
# Use for this compatibility exercise; the OS and Python runtime are end-of-life.
FROM python:stretch

# Disable bytecode files and stream logs immediately.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
# pip 24.0 supports Python 3.7; requirements.txt pins compatible application dependencies.
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir pip==24.0 \
    && python -m pip install --no-cache-dir -r requirements.txt
COPY main.py .

# Keep the rubric's exact Gunicorn entry point.
ENTRYPOINT ["gunicorn", "-b", ":8080", "main:APP"]
