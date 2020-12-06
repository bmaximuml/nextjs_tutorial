#!/usr/bin/fish
set USER thoughts
docker build \
  -t {$USER} \
  --build-arg USER={$USER} \
  . 
docker run -it \
  -v /home/max/Documents/hour/:/run/{$USER}/ \
  -p 3000:3000 \
  {$USER}
