FROM ubuntu

RUN apt update
RUN apt -y dist-upgrade
RUN apt -y install git software-properties-common
RUN add-apt-repository ppa:mcrl2/release-ppa
RUN apt update
RUN apt -y install mcrl2
RUN apt -y install cmake make build-essential
RUN apt -y install qt6-base-dev libboost-dev
RUN apt -y install python3 pip
RUN apt -y install wget 

WORKDIR /root 
RUN wget https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
RUN dpkg -i packages-microsoft-prod.deb
RUN apt -y update
RUN apt -y dist-upgrade
RUN apt -y install dotnet-sdk-8.0



RUN useradd -ms /bin/bash -u 999 etamin
USER etamin
RUN pip install pandas
#WORKDIR /workspaces/case-study-eta-minimization
WORKDIR /biggie/home/vincenzo/data/local/repos/ImageMinimizationTests

