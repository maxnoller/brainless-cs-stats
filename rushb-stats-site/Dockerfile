FROM node:lts-alpine3.18 

WORKDIR /app
COPY package.json yarn.lock ./
RUN yarn install

COPY . .

RUN yarn build
RUN rm -rf src/ static/ emailTemplates/
USER node:node

EXPOSE 3000
CMD ["node", "build/index.js"]

