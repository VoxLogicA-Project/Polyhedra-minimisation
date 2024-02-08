#!/bin/bash
(cd .devcontainer && docker build . -t "csem-devcontainer")
docker run -v $(pwd):/workspaces/case-study-eta-minimization -it csem-devcontainer


