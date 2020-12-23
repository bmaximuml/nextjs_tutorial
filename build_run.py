#!/usr/bin/env python3

import re
import click
import docker
import json
import os

from datetime import datetime
from io import BytesIO
from docker import APIClient
from docker import api

@click.command()
@click.option('-u', '--user', type=str, default='nextjs', show_default=True, help='User and project name')
@click.option('-d', '--dir', type=click.Path(exists=True, readable=True, file_okay=False), default='/home/max/Documents/nextjs_tutorial', show_default=True, help='Docker build context')
@click.option('-c/-C', '--cache/--no-cache', default=True, show_default=True, help='Use docker image cache')
@click.option('-p/-P', '--pull/--no-pull', default=True, show_default=True, help='Pull base images before build')
@click.option('-r/-R', '--rm/--no-rm', default=False, show_default=True, help='Delete containers on exit')
@click.option('--detach/--no-detach', default=True, show_default=True, help='Pull base images before build')
@click.option('-v', '--verbose', count=True)
@click.option('-e', '--env', type=click.Choice(['dev', 'test', 'prod'], case_sensitive=False), default='dev', show_default=True, help='Specify environment')
def main(user, dir, cache, pull, rm, detach, env, verbose):
    client = docker.from_env()
    api_client = APIClient(base_url='unix://var/run/docker.sock')
    name = f'{user}_{env}'
    tag = f'{user}:{env}'
    dockerfile = f'Dockerfile.{env}'
    build_kwargs = {
        'path': dir,
        'tag': tag,
        'dockerfile': dockerfile,
        'buildargs': {
            'USER': user,
        },
        'nocache': not cache,
        'pull': pull,
        'rm': rm,
        'decode': True,
    }
    if verbose >= 2:
        print('Build Args:')
        [print(f'\t{key}: {build_kwargs[key]}') for key in build_kwargs.keys()]

    image = api_client.build(**build_kwargs)
    # image = client.build(**build_kwargs)

    if verbose >= 1:
        print('\nBuild Log:')
        for i in image:
            if 'stream' in i:
                [print(f'\t{line.strip()}') for line in i['stream'].splitlines() if line.strip('') != '']
    
    # while True:
    #     try:
    #         output = image.__next__
    #         output = output.strip('\r\n')
    #         json_output = json.loads(output)
    #         if 'stream' in json_output:
    #             click.echo(json_output['stream'].strip('\n'))
    #     except StopIteration:
    #         click.echo("Docker image build complete.")
    #     except ValueError:
    #         click.echo(f'Error parsing output from docker image build: {output}')
    # response = [line for line in cli.build()]
    # (print(log) for log in image[1])
    # print(f'image: {image.id}')
    
    if env.lower() == 'prod':
        run_kwargs = {
            'image': tag,
            'name': name,
            'ports': {
                '3000/tcp': 5000,
            },
            'detach': detach,
        }
    elif env.lower() == 'test':
        run_kwargs = {
            'image': tag,
            'name': name,
            'ports': {
                '3000/tcp': 4000,
            },
            'detach': detach,
        }
    else:
        run_kwargs = {
            'image': tag,
            'name': name,
            'ports': {
                '3000/tcp': 3000,
            },
            'volumes': {
                os.path.join(dir, "src", "components"): {'mode': 'ro', 'bind': os.path.join("/", "run", user, "components")},
                os.path.join(dir, "src", "lib"): {'mode': 'ro', 'bind': os.path.join("/", "run", user, "lib")},
                os.path.join(dir, "src", "pages"): {'mode': 'ro', 'bind': os.path.join("/", "run", user, "pages")},
                os.path.join(dir, "src", "posts"): {'mode': 'ro', 'bind': os.path.join("/", "run", user, "posts")},
                os.path.join(dir, "src", "public"): {'mode': 'ro', 'bind': os.path.join("/", "run", user, "public")},
                os.path.join(dir, "src", "styles"): {'mode': 'ro', 'bind': os.path.join("/", "run", user, "styles")},
                os.path.join(dir, "src", "postcss.config.js"): {'mode': 'ro', 'bind': os.path.join("/", "run", user, "postcss.config.js")},
                os.path.join(dir, "src", "tailwind.config.js"): {'mode': 'ro', 'bind': os.path.join("/", "run", user, "tailwind.config.js")},
                os.path.join(dir, "src", "tsconfig.json"): {'mode': 'ro', 'bind': os.path.join("/", "run", user, "tsconfig.json")},
            },
            'detach': detach,
        }

    if verbose >= 2:
        print('\nRun Args:')
        [print(f'\t{key}: {run_kwargs[key]}') for key in run_kwargs.keys()]

    all_containers = api_client.containers(
        all=True,
        filters={
            'name': f'^{name}$',
        },
    )
    if all_containers:
        if verbose >= 1:
            print(f'\nContainers exist for {name}...')
            # [print(f'\t{container["Names"][0].replace("/", "")} : {container["Id"]}') for container in all_containers]
        for container in all_containers:
            container_id = container['Id']
            if container['State'].lower() == 'running':
                if verbose >= 1:
                    print(f'\tStopping running container: {container_id}')
                api_client.stop(container_id)
            rename = f'{name}_{datetime.fromtimestamp(container["Created"])}'.replace(' ', '_').replace(':', '_')
            count = 1
            while api_client.containers(all=True, filters={'name': f'^{rename}$'}):
                rename = f'{name}_{datetime.fromtimestamp(container["Created"])}_{count}'.replace(' ', '_').replace(':', '_')
                count += 1
                
            if verbose >= 1:
                print(f'\tRenaming to {rename} (id: {container_id})')
            api_client.rename(container_id, rename)
        
    else:
        if verbose >= 1:
            print(f'No existing containers for {name}.')

    container = client.containers.run(**run_kwargs)
    if verbose >= 1:
        print(f'\nStarted container: {container.id}')
        print('\nConnect with:')
        print(f'\tdocker exec -it {name} bash')
        print('\nView logs with:')
        print(f'\tdocker logs {name}')

if __name__ == '__main__':
    main()