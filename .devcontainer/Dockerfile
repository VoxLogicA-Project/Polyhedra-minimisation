FROM ubuntu:mantic-20240122

RUN apt update
RUN apt -y dist-upgrade
RUN apt -y install git software-properties-common
RUN apt -y install cmake make build-essential
RUN apt -y install qt6-base-dev libboost-dev
RUN apt -y install python3 pip
RUN apt -y install wget
RUN apt -y install qtbase5-dev

RUN rm -f /usr/lib/python3*/EXTERNALLY-MANAGED

# RUN add-apt-repository ppa:mcrl2/release-ppa
# RUN apt -y update
# RUN apt -y install mcrl2

RUN pip install pandas networkx 

RUN adduser etamin
WORKDIR /home/etamin
RUN git clone --depth 1 https://github.com/mCRL2org/mCRL2.git
RUN pip install -r ./mCRL2/requirements.txt

RUN cd mCRL2 && cmake .
RUN cd mCRL2 && make -j 8 
RUN cd mCRL2 && make install

RUN wget https://packages.microsoft.com/config/ubuntu/23.10/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
RUN dpkg -i packages-microsoft-prod.deb
RUN apt -y update
RUN apt -y dist-upgrade
RUN apt -y install dotnet-sdk-8.0
RUN apt -y install htop nano 
RUN apt -y install screen
RUN apt install -y graphviz
RUN apt install -y zip
RUN pip install ipykernel
RUN cd ..
RUN git clone -b Posets --single-branch https://github.com/vincenzoml/VoxLogicA.git
RUN cd VoxLogicA/src && make

RUN echo "* soft stack 8388608" >> /etc/security/limits.conf
RUN echo "* hard stack 8388608" >> /etc/security/limits.conf

RUN chown -R etamin mCRL2
USER etamin
 
 # RUN echo root:root | chpasswd 