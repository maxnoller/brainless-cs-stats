FROM node:lts-alpine3.18 

WORKDIR /app
COPY rushb-stats-site/package.json rusb-stats-site/yarn.lock ./
RUN yarn install

COPY ./rushb-stats-site/. .

RUN yarn build
RUN rm -rf src/ static/ emailTemplates/
USER node:node

EXPOSE 3000
CMD ["node", "build/index.js"]

