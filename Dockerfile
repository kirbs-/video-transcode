FROM nvidia/cuda:11.2.0-devel-centos7 AS build

RUN yum update -y
RUN yum groupinstall "Development Tools" -y
RUN yum install -y epel-release
RUN yum localinstall -y --nogpgcheck https://download1.rpmfusion.org/free/el/rpmfusion-free-release-7.noarch.rpm
RUN yum install -y argtable argtable-devel git autoconf automake yasm python3 pkgconfig zlib-devel libjpeg-turbo-devel python3-devel
RUN yum clean all

# build ffmpeg with cuda support
RUN git clone https://git.videolan.org/git/ffmpeg/nv-codec-headers.git
RUN cd nv-codec-headers && make && make install && cd ../
RUN git clone --depth 1 --branch n4.4.2 https://git.ffmpeg.org/ffmpeg.git /opt/ffmpeg
RUN mkdir /opt/build
ENV PKG_CONFIG_PATH=/usr/local/lib/pkgconfig 
RUN cd /opt/ffmpeg \ 
    && ./configure --prefix="/opt/build" --enable-cuda --enable-cuvid --enable-nvenc --enable-nonfree --enable-libnpp --extra-cflags=-I/usr/local/cuda/include --extra-ldflags=-L/usr/local/cuda/lib64 \
    && make -j 10 \ 
    && make install 


FROM nvidia/cuda:11.2.0-runtime-centos7
RUN yum update -y
RUN yum groupinstall "Development Tools" -y
RUN yum install -y epel-release
RUN yum localinstall -y --nogpgcheck https://download1.rpmfusion.org/free/el/rpmfusion-free-release-7.noarch.rpm
RUN yum install -y argtable argtable-devel git autoconf automake yasm pkgconfig zlib-devel libjpeg-turbo-devel openssl-devel bizip2-devel wget libffi-devel

# install python 3.9
RUN wget https://www.python.org/ftp/python/3.9.10/Python-3.9.10.tgz
RUN tar xvf Python-3.9.10.tgz
RUN cd Python-3.9*/ \ 
    && bash configure \ 
    && make altinstall
# RUN rm -rf Python-3.9*

# copy ffmpeg built with NVENC
RUN mkdir /opt/build
COPY --from=build /usr/local/bin /usr/local/bin/
COPY --from=build /opt/build /opt/build/
RUN ln -s /opt/build/bin/ffmpeg /usr/local/bin/ffmpeg

# install comskip
ENV PKG_CONFIG_PATH=/opt/build/lib/pkgconfig
RUN git clone --depth 1 https://github.com/erikkaashoek/Comskip.git /opt/Comskip
RUN cd /opt/Comskip && bash autogen.sh && bash configure && make && make install

# install comcut
RUN git clone https://github.com/BrettSheleski/comchap.git /opt/comchap
RUN cd /opt/comchap && make && make install

# set Python encoding default
ENV LC_ALL=en_US.utf-8
ENV LANG=en_US.utf-8

# install and configure video-transcode
RUN pip3.9 install git+https://github.com/kirbs-/video-transcode.git --no-cache
# RUN echo stuff
COPY video_transcode/config /opt/video_transcode/config/.
RUN mkdir /var/run/video_transcode
ENV VIDEO_TRANSCODE_CONFIG=/opt/video_transcode/config/config.yaml
ENV VIDEO_TRANSCODE_MODE=CONTAINER
ENV NVIDIA_DRIVER_CAPABILITIES=video,compute,utility

RUN rm -rf Python-3.9*
RUN cd /usr/local/cuda/lib64 && find . ! -name 'libnpp*' -type l -exec rm -f {} + && find . ! -name 'libnpp*' -type f -exec rm -f {} +

COPY bootstrap.sh /usr/local/bin
ENTRYPOINT ["bash", "bootstrap.sh"]
