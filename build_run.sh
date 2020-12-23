#!/usr/bin/fish

switch $argv[1]
  case prod
    set USER nextjs
    set DIR /home/max/Documents/nextjs_tutorial
    set DOCKERFILE Dockerfile.prod
    set TAG prod
    set NAME {$USER}_{$TAG}

    docker build \
      --pull \
      -t {$USER}:{$TAG} \
      --build-arg USER={$USER} \
      # --no-cache \
      --file {$DOCKERFILE} \
      {$DIR}

    docker stop (docker ps -q --filter "name=$NAME")
    docker rm {$NAME}

    docker run -d \
      --name {$NAME} \
      -p 5000:3000 \
      {$USER}:{$TAG}
  case test
    set USER nextjs
    set DIR /home/max/Documents/nextjs_tutorial
    set DOCKERFILE Dockerfile.test
    set TAG test
    set NAME {$USER}_{$TAG}

    docker build \
      --pull \
      -t {$USER}:{$TAG} \
      --build-arg USER={$USER} \
      # --no-cache \
      --file {$DOCKERFILE} \
      {$DIR}

    docker stop (docker ps -q --filter "name=$NAME")
    docker rm {$NAME}

    docker run -d \
      --name {$NAME} \
      -p 4000:3000 \
      {$USER}:{$TAG}
  case *
    set USER nextjs
    set DIR /home/max/Documents/nextjs_tutorial
    set DOCKERFILE Dockerfile
    set TAG dev
    set NAME {$USER}_{$TAG}

    echo {$NAME}

    docker build \
      --pull \
      -t {$USER}:{$TAG} \
      --build-arg USER={$USER} \
      # --no-cache \
      --file {$DOCKERFILE} \
      {$DIR}

    docker stop (docker ps -q --filter "name=$NAME")
    docker rm {$NAME}

    docker run -it \
      --name {$NAME} \
      -v {$DIR}/src/components/:/run/{$USER}/components/ \
      -v {$DIR}/src/lib/:/run/{$USER}/lib/ \
      -v {$DIR}/src/pages/:/run/{$USER}/pages/ \
      -v {$DIR}/src/posts/:/run/{$USER}/posts/ \
      -v {$DIR}/src/public/:/run/{$USER}/public/ \
      -v {$DIR}/src/styles/:/run/{$USER}/styles/ \
      -v {$DIR}/src/postcss.config.js:/run/{$USER}/postcss.config.js \
      -v {$DIR}/src/tailwind.config.js:/run/{$USER}/tailwind.config.js \
      # -v {$DIR}/src/tsconfig.json:/run/{$USER}/tsconfig.json \
      -p 3000:3000 \
      {$USER}
end