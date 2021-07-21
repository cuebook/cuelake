# build environment
FROM node:12-alpine as builder
WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY ui/package.json /app/package.json
RUN npm install
COPY ui /app

RUN npm run build

# production environment
FROM python:3.7-slim
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install nginx vim -y --no-install-recommends
WORKDIR /code
COPY api/requirements.txt /code/
RUN pip install -r requirements.txt --no-cache-dir
COPY api /code/
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log
RUN chmod +x /code/start_server.sh
RUN chown -R www-data:www-data /code
EXPOSE 80
STOPSIGNAL SIGTERM
CMD ["/code/start_server.sh"]
