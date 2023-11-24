#Inspired by derhuest's BVG-API, details here https://github.com/derhuerst/bvg-rest/blob/6/Dockerfile
FROM node:18-alpine

RUN apk add --update git bash
# Get data from repo
RUN git clone https://github.com/derhuerst/bvg-rest.git /app
WORKDIR /app
RUN git reset --hard 71a5dca6b470f6650c1b69ce873e0fb0fcc3269c

RUN npm install --production && npm cache clean --force

EXPOSE 3000

ENV HOSTNAME v6.bvg.transport.rest
ENV PORT 3000

CMD ["node", "index.js"]