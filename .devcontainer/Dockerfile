FROM ubuntu

RUN apt update
RUN apt -y dist-upgrade
RUN apt -y install git software-properties-common
RUN add-apt-repository ppa:mcrl2/release-ppa
RUN apt update
RUN apt -y install mcrl2

RUN useradd -ms /bin/bash -u 1000 etamin
USER etamin
WORKDIR /workspaces/case-study-eta-minimization

