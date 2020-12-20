FROM node:14.15.1-alpine3.12
# FROM node:15.4.0-alpine3.12
# 15.4.0 Doesn't work.

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

RUN rm -rf pages public

# Install TailwindCSS, gray-matter, remark, date-fns
RUN npm install \
    tailwindcss \
    postcss-preset-env \
    postcss-flexbugs-fixes \
    postcss \
    autoprefixer \
    gray-matter \
    remark \
    remark-html \
    date-fns

CMD set -x ; \
    /usr/local/bin/npm run dev > /var/log/npm 2&>1 & /bin/sh
