#Inspired by derhuest's BVG-API, details here https://github.com/derhuerst/bvg-rest/blob/6/Dockerfile
FROM node:18-alpine

RUN apk add --update git bash
# Get data from repo
RUN git clone https://github.com/derhuerst/db-rest.git /app
WORKDIR /app
RUN git reset --hard 1eff75e491b7d38c146c71f248779f08305255fa

RUN npm install --production && npm cache clean --force

EXPOSE 3000

ENV HOSTNAME v6.db.transport.rest
ENV PORT 3000

CMD ["node", "index.js"]