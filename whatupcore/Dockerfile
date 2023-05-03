FROM node:19-alpine

ENV NODE_ENV production

RUN apk add --update --no-cache make git
WORKDIR /usr/src/whatupcore/
COPY package*.json yarn.lock .
RUN yarn install --dev; mkdir /usr/src/whatupcore-data/
COPY . /usr/src/whatupcore
RUN make build

EXPOSE 3000
CMD make run
