#!/usr/bin/fish
set USER nextjs
docker build \
  -t {$USER} \
  --build-arg USER={$USER} \
  . 
docker run -it \
  # -v /home/max/Documents/nextjs/:/run/{$USER}/ \
  -p 3000:3000 \
  {$USER}
