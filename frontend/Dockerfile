FROM node:20-slim

WORKDIR /app

COPY package.json yarn.lock /app/
RUN yarn install --frozen-lockfile

COPY . /app

EXPOSE 3000

CMD ["yarn", "start"]
