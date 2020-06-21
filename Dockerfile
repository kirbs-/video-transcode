FROM nvidia/cuda:10.2-devel-centos7 

RUN yum update -y
RUN yum groupinstall "Development Tools" -y
RUN yum install -y epel-release
RUN yum localinstall -y --nogpgcheck https://download1.rpmfusion.org/free/el/rpmfusion-free-release-7.noarch.rpm
RUN yum install -y argtable argtable-devel ffmpeg ffmpeg-devel git autoconf automake yasm


# install pyenv
# RUN git clone https://github.com/pyenv/pyenv.git ~/.pyenv

# install ffmpeg with cuda support
RUN git clone https://git.videolan.org/git/ffmpeg/nv-codec-headers.git
RUN cd nv-codec-headers && make && make install && cd ../
RUN git clone https://git.ffmpeg.org/ffmpeg.git /opt/ffmpeg
ENV PKG_CONFIG_PATH=/usr/local/lib/pkgconfig 
RUN cd /opt/ffmpeg \ 
    && ./configure --enable-cuda-sdk --enable-cuvid --enable-nvenc --enable-nonfree --enable-libnpp --extra-cflags=-I/usr/local/cuda/include --extra-ldflags=-L/usr/local/cuda/lib64 \
    && make -j 10 \ 
    && cd ../
RUN ln -s /opt/ffmpeg/ffmpeg /usr/local/bin/ffmpeg

# install comskip
RUN git clone https://github.com/erikkaashoek/Comskip.git /opt/Comskip
RUN cd /opt/Comskip && bash autogen.sh && bash configure && make && make install
# RUN rm -rf Comskip

# install comcut
RUN git clone https://github.com/BrettSheleski/comchap.git /opt/comchap
RUN cd /opt/comchap && make && make install

RUN yum install -y python3

# install video-transcode
RUN pip3 install video_transcode
# remove redis later
RUN pip3 install redis
COPY video_transcode/config /opt/video_transcode/config/.
RUN mkdir /var/run/video_transcode

COPY bootstrap.sh /usr/local/bin
ENTRYPOINT ["bash", "bootstrap.sh"]
