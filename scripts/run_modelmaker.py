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
import argparse
import yaml
import json


def main(config):
    import edgeai_modelmaker

    # get the ai backend module
    ai_target_module = edgeai_modelmaker.ai_modules.get_target_module(config['common']['target_module'])

    # get default params
    params = ai_target_module.runner.ModelRunner.init_params()

    # get pretrained model for the given model_name
    model_name = config['training']['model_name']
    model_description = ai_target_module.runner.ModelRunner.get_model_description(model_name)
    if model_description is None:
        print(f"please check if the given model_name is a supported one: {model_name}")
        return False
    #

    # update the params with model_description and config
    params = params.update(model_description).update(config)

    # create the runner
    model_runner = ai_target_module.runner.ModelRunner(
        params
    )

    # prepare
    run_params_file = model_runner.prepare()
    print(f'Run params is at: {run_params_file}')

    # run
    model_runner.run()

    print(f'Trained model is at: {model_runner.get_params().training.training_path}')
    print(f'Compiled model is at: {model_runner.get_params().compilation.model_packaged_path}')
    return True


if __name__ == '__main__':
    print(f'argv: {sys.argv}')
    # the cwd must be the root of the repository
    if os.path.split(os.getcwd())[-1] == 'scripts':
        os.chdir('../')
    #

    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    parser.add_argument('config_file', type=str, default=None)
    parser.add_argument('--run_name', type=str)
    parser.add_argument('--task_type', type=str)
    parser.add_argument('--model_name', type=str)
    parser.add_argument('--target_device', type=str)
    parser.add_argument('--num_gpus', type=int)
    parser.add_argument('--batch_size', type=int)
    args = parser.parse_args()

    # read the config
    with open(args.config_file) as fp:
        if args.config_file.endswith('.yaml'):
            config = yaml.safe_load(fp)
        elif args.config_file.endswith('.json'):
            config = json.load(fp)
        else:
            assert False, f'unrecognized config file extension for {args.config_file}'
        #
    #

    # override with supported commandline args
    kwargs = vars(args)
    if 'run_name' in kwargs:
        config['common']['run_name'] = kwargs['run_name']
    #
    if 'task_type' in kwargs:
        config['common']['task_type'] = kwargs['task_type']
    #
    if 'target_device' in kwargs:
        config['common']['target_device'] = kwargs['target_device']
    #
    if 'model_name' in kwargs:
        config['training']['model_name'] = kwargs['model_name']
    #
    if 'num_gpus' in kwargs:
        config['training']['num_gpus'] = kwargs['num_gpus']
    #
    if 'batch_size' in kwargs:
        config['training']['batch_size'] = kwargs['batch_size']
    #
    if 'learning_rate' in kwargs:
        config['training']['learning_rate'] = kwargs['learning_rate']
    #

    main(config)
