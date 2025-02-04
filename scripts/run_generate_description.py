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
import os
import datetime
import sys
import copy
import argparse
import yaml
import json


def main(args):
    import edgeai_modelmaker

    # get the ai backend module
    ai_target_module = edgeai_modelmaker.ai_modules.get_target_module(args.target_module)

    # get params for the given config
    params = ai_target_module.runner.ModelRunner.init_params()

    # get_training_module_descriptions
    training_module_descriptions = ai_target_module.runner.ModelRunner.get_training_module_descriptions(params)

    # get supported pretrained models for the given params
    model_descriptions = ai_target_module.runner.ModelRunner.get_model_descriptions(params)

    # update descriptions
    model_descriptions_desc = dict()
    for k, v in model_descriptions.items():
        s = copy.deepcopy(params)
        s.update(copy.deepcopy(v))
        model_descriptions_desc[k] = s
    #

    # get presets
    preset_descriptions = ai_target_module.runner.ModelRunner.get_preset_descriptions(params)

    # get target device descriptions
    target_device_descriptions = ai_target_module.runner.ModelRunner.get_target_device_descriptions(params)

    # task descriptions
    task_descriptions = ai_target_module.runner.ModelRunner.get_task_descriptions(params)

    # sample dataset descriptions
    sample_dataset_descriptions = ai_target_module.runner.ModelRunner.get_sample_dataset_descriptions(params)

    description = dict(training_module_descriptions=training_module_descriptions,
                       model_descriptions=model_descriptions_desc,
                       preset_descriptions=preset_descriptions,
                       target_device_descriptions=target_device_descriptions,
                       task_descriptions=task_descriptions,
                       sample_dataset_descriptions=sample_dataset_descriptions)

    # write description
    description_file = os.path.join(args.description_path, f'description_{args.target_module}' + '.yaml')
    edgeai_modelmaker.utils.write_dict(description, description_file)
    print(f'description is written at: {description_file}')


if __name__ == '__main__':
    print(f'argv: {sys.argv}')
    # the cwd must be the root of the repository
    if os.path.split(os.getcwd())[-1] == 'scripts':
        os.chdir('../')
    #

    parser = argparse.ArgumentParser()
    parser.add_argument('--target_module', type=str, default='vision')
    parser.add_argument('--description_path', type=str, default='./data/descriptions')
    args = parser.parse_args()

    main(args)
