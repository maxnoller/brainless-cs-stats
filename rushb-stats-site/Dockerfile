FROM node:lts-alpine3.18 

WORKDIR /app
COPY rushb-stats-site/package.json rushb-stats-site/package-lock.json ./
RUN npm install

COPY ./rushb-stats-site/. .

RUN npm run-script build
RUN rm -rf src/ static/ emailTemplates/
USER node:node

EXPOSE 3000
CMD ["node", "build/index.js"]

