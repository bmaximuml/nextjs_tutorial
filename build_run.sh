#!/usr/bin/fish
set USER nextjs
docker build \
  -t {$USER} \
  --build-arg USER={$USER} \
  . 
docker run -it \
  -v /home/max/Documents/nextjs_tutorial/src/pages/index.js:/run/{$USER}/pages/index.js \
  -p 3000:3000 \
  {$USER}
