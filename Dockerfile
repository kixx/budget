# build
FROM node:13.0.1-alpine AS build-frontend
WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend .
RUN npm run build

# production
FROM nginx:stable-alpine as production
WORKDIR /app
RUN apk update && apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [[ ! -e /usr/bin/pip ]]; then ln -s /usr/bin/pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -s /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache
RUN apk update && apk add gcc python3-dev musl-dev
COPY --from=build-frontend /app/dist/ /usr/share/nginx/html
COPY ./web/default.conf /etc/nginx/conf.d/default.conf
COPY ./backend/requirements.txt ./
RUN pip install -r requirements.txt
RUN pip install gunicorn
COPY ./backend .
ENV VUE_APP_API_URL=/api
CMD gunicorn -b 0.0.0.0:5000 app:app --daemon && \
      sed -i -e 's/$PORT/'"$PORT"'/g' /etc/nginx/conf.d/default.conf && \
      nginx -g 'daemon off;'
