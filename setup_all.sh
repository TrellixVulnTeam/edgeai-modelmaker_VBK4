#!/usr/bin/env bash

#################################################################################
# Copyright (c) 2018-2022, Texas Instruments Incorporated - http://www.ti.com
# All Rights Reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#################################################################################

#################################################################################
# internal or external repositories
USE_INTERNAL_REPO=0

if [[ ${USE_INTERNAL_REPO} -eq 0 ]]; then
    SOURCE_LOCATION="https://github.com/TexasInstruments/"
    FAST_CLONE_MODELZOO=""
else
    SOURCE_LOCATION="ssh://git@bitbucket.itg.ti.com/edgeai-algo/"
    FAST_CLONE_MODELZOO="--single-branch -b release"
fi
# print
echo "SOURCE_LOCATION="${SOURCE_LOCATION}

#################################################################################
# clone
echo "cloning git repositories. this may take some time..."
if [ ! -d ../edgeai-benchmark ]; then git clone ${SOURCE_LOCATION}edgeai-benchmark.git ../edgeai-benchmark; fi
if [ ! -d ../edgeai-mmdetection ]; then git clone ${SOURCE_LOCATION}edgeai-mmdetection.git ../edgeai-mmdetection; fi
if [ ! -d ../edgeai-torchvision ]; then git clone ${SOURCE_LOCATION}edgeai-torchvision.git ../edgeai-torchvision; fi
if [ ! -d ../edgeai-modelzoo ]; then git clone ${SOURCE_LOCATION}edgeai-modelzoo.git ${FAST_CLONE_MODELZOO} ../edgeai-modelzoo; fi
# this is optional - (GPLv3 licensed)
if [ ! -d ../edgeai-yolov5 ]; then git clone ${SOURCE_LOCATION}edgeai-yolov5.git ../edgeai-yolov5; fi


echo "cloning done."

#################################################################################
echo "installing repositories..."

echo "installing: https://github.com/TexasInstruments/edgeai-torchvision"
cd ../edgeai-torchvision
./setup.sh

echo "installing: https://github.com/TexasInstruments/edgeai-mmdetection"
cd ../edgeai-mmdetection
./setup.sh

echo "installing: https://github.com/TexasInstruments/edgeai-yolov5 (GPLv3 Licensed)"
cd ../edgeai-yolov5
./setup_for_modelmaker.sh

echo "installing: https://github.com/TexasInstruments/edgeai-benchmark"
cd ../edgeai-benchmark
# for setup.py develop mode to work inside docker environment, this is required
git config --global --add safe.directory $(pwd)
./setup_pc.sh

echo "installing edgeai-modelmaker"
cd ../edgeai-modelmaker
./setup.sh

ls -d ../edgeai-*

echo "installation done."
