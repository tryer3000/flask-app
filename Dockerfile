# docker build -t clweb .
FROM python:3-onbuild
CMD gunicorn manage:app -b 0.0.0.0:5000 --capture-output
