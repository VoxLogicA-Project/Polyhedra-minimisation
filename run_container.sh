#!/bin/bash
(cd .devcontainer && docker build . -t "csem-devcontainer")
docker run -w /home/$(whoami) --userns=keep-id -v $(pwd):/workspaces/case-study-eta-minimization -v "$HOME":/home/$(whoami) -it csem-devcontainer


