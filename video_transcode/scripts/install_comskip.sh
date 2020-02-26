#!/usr/bin/env bash
set -e
set -u

git clone https://github.com/erikkaashoek/Comskip.git
cd Comskip && bash autogen.sh && bash configure && make && make install
rm -rf Comskip

git clone https://github.com/BrettSheleski/comchap.git
cd comchap && make && make install

#cd Comskip && bash ./configure && make
