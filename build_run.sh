#!/usr/bin/fish
set USER nextjs
set DIR /home/max/Documents/nextjs_tutorial
docker build \
  --pull \
  -t {$USER} \
  --build-arg USER={$USER} \
  # --no-cache \
  # --file Dockerfile.slim \
  {$DIR}
docker run -it \
  -v {$DIR}/src/components/:/run/{$USER}/components/ \
  -v {$DIR}/src/lib/:/run/{$USER}/lib/ \
  -v {$DIR}/src/pages/:/run/{$USER}/pages/ \
  -v {$DIR}/src/posts/:/run/{$USER}/posts/ \
  -v {$DIR}/src/public/:/run/{$USER}/public/ \
  -v {$DIR}/src/styles/:/run/{$USER}/styles/ \
  -v {$DIR}/src/postcss.config.js:/run/{$USER}/postcss.config.js \
  -v {$DIR}/src/tailwind.config.js:/run/{$USER}/tailwind.config.js \
  -p 3000:3000 \
  {$USER}
