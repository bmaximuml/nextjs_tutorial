FROM node:alpine

ARG USER=nextjs
ARG WORKDIR=/run/
ARG SHELL=/bin/sh

RUN set -x; \
    adduser \
        --home ${WORKDIR} \
        --shell ${SHELL} \
        --disabled-password \
        ${USER}

RUN touch /var/log/npm && chown ${USER} /var/log/npm

USER ${USER}

WORKDIR ${WORKDIR}

RUN set -x; \
    npx create-next-app \
    ${USER} \
    --use-npm \
    --example "https://github.com/vercel/next-learn-starter/tree/master/learn-starter"

WORKDIR ${WORKDIR}/${USER}

RUN rm -rf src/*

CMD set -x ; \
    /usr/local/bin/npm run dev > /var/log/npm 2&>1 & /bin/sh
