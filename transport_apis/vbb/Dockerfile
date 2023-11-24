#Inspired by derhuest's BVG-API, details here https://github.com/derhuerst/bvg-rest/blob/6/Dockerfile
FROM node:18-alpine

RUN apk add --update git bash
# Get data from repo
RUN git clone https://github.com/derhuerst/vbb-rest.git /app
WORKDIR /app
RUN git reset --hard e84abb37ccec3d01b60033974d730e3f5429484e

RUN npm install --production && npm cache clean --force

EXPOSE 3000

ENV HOSTNAME v6.vbb.transport.rest
ENV PORT 3000

CMD ["node", "index.js"]