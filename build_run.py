#!/usr/bin/env python3

import re
import click
import docker
import os

from datetime import datetime
from docker import APIClient
from time import sleep

class BuildRunError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return f'BuildRunError: {self.code} - {self.message}'


class BuildRun(object):
    def main(self, user, dir, cache, pull, rm, detach, env, wait, push, run, build, repo_name, verbose):
        client = docker.from_env()
        api_client = APIClient(base_url='unix://var/run/docker.sock')
        name = f'{user}_{env}'
        tag = f'{user}:{env}'

        if build:
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

            build_success = False
            if verbose >= 1:
                print('\nBuild Log:')
                for i in image:
                    if 'stream' in i:
                        if 'Successfully built' in i['stream']:
                            build_success = True
                        [print(f'\t{line.strip()}') for line in i['stream'].splitlines() if line.strip().strip('\n') != '']

            if not build_success:
                raise BuildRunError(101, 'Build Failed')

        if run:
            if env.lower() == 'prod':
                run_kwargs = {
                    'image': tag,
                    'name': name,
                    'user': user,
                    'ports': {
                        '3000/tcp': 5000,
                    },
                    'detach': detach,
                }
            elif env.lower() == 'test':
                run_kwargs = {
                    'image': tag,
                    'name': name,
                    'user': user,
                    'ports': {
                        '3000/tcp': 4000,
                    },
                    'detach': detach,
                }
            else:
                run_kwargs = {
                    'image': tag,
                    'name': name,
                    'user': user,
                    'ports': {
                        '3000/tcp': 3000,
                    },
                    'volumes': {
                        os.path.join(dir, "src"): {'mode': 'rw', 'bind': os.path.join("/", "run", user)},
                        # os.path.join(dir, "src", "components"): {'mode': 'ro', 'bind': os.path.join("/", "run", user, "components")},
                        # os.path.join(dir, "src", "lib"): {'mode': 'ro', 'bind': os.path.join("/", "run", user, "lib")},
                        # os.path.join(dir, "src", "pages"): {'mode': 'ro', 'bind': os.path.join("/", "run", user, "pages")},
                        # os.path.join(dir, "src", "posts"): {'mode': 'ro', 'bind': os.path.join("/", "run", user, "posts")},
                        # os.path.join(dir, "src", "public"): {'mode': 'ro', 'bind': os.path.join("/", "run", user, "public")},
                        # os.path.join(dir, "src", "styles"): {'mode': 'ro', 'bind': os.path.join("/", "run", user, "styles")},
                        # os.path.join(dir, "src", "postcss.config.js"): {'mode': 'ro', 'bind': os.path.join("/", "run", user, "postcss.config.js")},
                        # os.path.join(dir, "src", "tailwind.config.js"): {'mode': 'ro', 'bind': os.path.join("/", "run", user, "tailwind.config.js")},
                        # os.path.join(dir, "src", "tsconfig.json"): {'mode': 'ro', 'bind': os.path.join("/", "run", user, "tsconfig.json")},
                        # os.path.join(dir, "src", "package.json"): {'mode': 'ro', 'bind': os.path.join("/", "run", user, "package.json")},
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

                print(f'Waiting {str(wait)} seconds to ensure container stays up...')
                run_success = True
                while wait >= 0:
                    if api_client.containers(filters={'name': f'^{name}$'}):
                        print(f'\r\t{wait}: Running', end='', flush=True)
                        wait -= 1
                        sleep(1)
                    else:
                        print(f'\r\t{wait}: Died    ', flush=True)
                        run_success = False
                        break
                if run_success:
                    print(f'\r\tSuccess: http://localhost:{run_kwargs["ports"]["3000/tcp"]}/', flush=True)

        if push:
            if api_client.tag(tag, f'{repo_name}/{name}', tag=env):
                if verbose >= 1:
                    print(f'Tagged image as {repo_name}/{name}:{env}')
            else:
                raise BuildRunError(102, f'Failed to tag image as {repo_name}/{name}:{env}')
            try:
                [print(f'\t{line["status"]}: {line["progressDetail"]}') for line in api_client.push(f'{repo_name}/{name}', tag=env, stream=True, decode=True) if verbose >= 2 and 'status' in line and 'progressDetail' in line]
            except docker.errors.APIError:
                raise BuildRunError(103, f'Failed to push {repo_name}/{name}:{env}')


@click.command()
@click.option('-u', '--user', type=str, default='nextjs', show_default=True, help='User and project name')
@click.option('-d', '--dir', type=click.Path(exists=True, readable=True, file_okay=False), default='/home/max/Documents/nextjs_tutorial', show_default=True, help='Docker build context')
@click.option('-c/-C', '--cache/--no-cache', default=True, show_default=True, help='Use docker image cache')
@click.option('-p/-P', '--pull/--no-pull', default=True, show_default=True, help='Pull base images before build')
@click.option('-n/-N', '--rm/--no-rm', default=False, show_default=True, help='Delete containers on exit')
@click.option('--detach/--no-detach', default=True, show_default=True, help='Pull base images before build')
@click.option('-e', '--env', type=click.Choice(['dev', 'test', 'prod'], case_sensitive=False), default='dev', show_default=True, help='Specify environment')
@click.option('-w', '--wait', type=int, default=5, help='Seconds to wait after starting container to check if it stays up')
@click.option('-s/-S', '--push/--no-push', default=False, show_default=True, help='Push image to Docker Hub after build')
@click.option('-r/-R', '--run/--no-run', default=True, show_default=True, help='Start a container from the image')
@click.option('-b/-B', '--build/--no-build', default=True, show_default=True, help='Build the image')
@click.option('-o', '--repo-name', type=str, default='benjilev08', show_default=True, help='Docker repository name')
@click.option('-v', '--verbose', count=True)
def main(user, dir, cache, pull, rm, detach, env, wait, push, run, build, repo_name, verbose):
    b = BuildRun()
    try:
        b.main(user, dir, cache, pull, rm, detach, env, wait, push, run, build, repo_name, verbose)
    except BuildRunError as e:
        print(e)

if __name__ == '__main__':
    main()