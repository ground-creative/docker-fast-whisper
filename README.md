# DOCKER CONTAINER FOR FAST WHISPER API

Docker environment for fast whisper api OpenAI style

## Installation

1. Clone the repository

```
git clone https://github.com/ground-creative/docker-fast-whisper.git
```

2. Change environment variables in env.sample file and rename it to .env

3. Change environment variables in env.sample file in app folder and rename it to .env

## Usage

```
docker compose --project-name=whisper up -d
```

Or

```
docker compose --project-name=whisper up -d --build
```

## Examples

View app/examples folder

### Command Environment Variables

It's possible to override environmet variable file while starting or building a container

```
TEST=true COMMAND="tail -f /dev/null" docker compose --project-name=whisper up -d
```
