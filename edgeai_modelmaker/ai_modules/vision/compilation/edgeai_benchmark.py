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
import shutil
import edgeai_benchmark
from .... import utils
from .. import constants


class ModelCompilation():
    @classmethod
    def init_params(self, *args, **kwargs):
        params = dict(
            compilation=dict(
            )
        )
        params = utils.ConfigDict(params, *args, **kwargs)
        return params

    def __init__(self, *args, quit_event=None, **kwargs):
        self.params = self.init_params(*args, **kwargs)
        self.quit_event = quit_event
        # prepare for model compilation
        self._prepare_pipeline_config()

        if self.params.common.task_type == constants.TASK_TYPE_CLASSIFICATION:
            log_summary_regex = {
                'js': [
                    {'type':'Progress', 'name':'Progress', 'description':'Progress of Compilation', 'unit':'Frame', 'value':None,
                     'regex':[{'op':'search', 'pattern':r'infer\s+\:\s+.*?\s+(?<infer>\d+)', 'group':1}],
                    },
                    {'type':'Validation Accuracy', 'name':'Accuracy', 'description':'Accuracy of Compilation', 'unit':'Accuracy Top-1%', 'value':None,
                     'regex':[{'op':'search', 'pattern':r'benchmark results.*?accuracy_top1.*?\:\s+(?<accuracy>\d+\.\d+)', 'group':1, 'dtype':'float'}],
                     },
                    {'type':'Completed', 'name':'Completed', 'description':'Completion of Compilation', 'unit':None, 'value':None,
                     'regex':[{'op':'search', 'pattern':r'success\:.*compilation\s+completed', 'group':1, 'dtype':'str', 'case_sensitive':False}],
                     },
                ]
            }
        elif self.params.common.task_type == constants.TASK_TYPE_DETECTION:
            log_summary_regex = {
                'js': [
                    {'type':'Progress', 'name':'Progress', 'description':'Progress of Compilation', 'unit':'Frame', 'value':None,
                     'regex':[{'op':'search', 'pattern':r'infer\s+\:\s+.*?\s+(?<infer>\d+)', 'group':1}],
                    },
                    {'type':'Validation Accuracy', 'name':'Accuracy', 'description':'Accuracy of Compilation', 'unit':'mAP[.5:.95]%', 'value':None,
                     'regex':[{'op':'search', 'pattern':r'benchmark results.*?accuracy_ap[.5:.95]\%.*?\:\s+(?<accuracy>\d+\.\d+)', 'group':1, 'dtype':'float', 'case_sensitive':False}],
                     },
                    {'type':'Completed', 'name':'Completed', 'description':'Completion of Compilation', 'unit':None, 'value':None,
                     'regex':[{'op':'search', 'pattern':r'success\:.*compilation\s+completed', 'group':1, 'dtype':'str', 'case_sensitive':False}],
                     },
                ]
            }
        else:
            log_summary_regex = None
        #

        model_compiled_path = self._get_compiled_artifact_dir()
        packaged_artifact_path = self._get_packaged_artifact_path() # actual, internal, short path
        model_packaged_path = self._replace_artifact_name(packaged_artifact_path) # a more descriptive symlink

        self.params.update(
            compilation=utils.ConfigDict(
                model_compiled_path=model_compiled_path,
                log_file_path=os.path.join(model_compiled_path, 'run.log'),
                log_summary_regex=log_summary_regex,
                summary_file_path=os.path.join(model_compiled_path, 'summary.yaml'),
                output_tensors_path=os.path.join(model_compiled_path, 'outputs'),
                model_packaged_path=model_packaged_path, # final compiled package
                model_visualization_path=os.path.join(model_compiled_path, 'artifacts', 'tempDir', 'runtimes_visualization.svg'),
            )
        )

    def clear(self):
        # clear the dirs
        shutil.rmtree(self.params.compilation.compilation_path, ignore_errors=True)

    def _prepare_pipeline_config(self):
        '''
        prepare for model compilation
        '''
        self.settings_file = edgeai_benchmark.get_settings_file(target_machine=self.params.common.target_machine, with_model_import=True)
        self.settings = self._get_settings(model_selection=self.params.compilation.model_compilation_id)
        self.work_dir, self.package_dir = self._get_base_dirs()

        if self.params.common.task_type == 'detection':
            dataset_loader = edgeai_benchmark.datasets.ModelMakerDetectionDataset
        elif self.params.common.task_type == 'classification':
            dataset_loader = edgeai_benchmark.datasets.ModelMakerClassificationDataset
        else:
            dataset_loader = None
        #

        # can use any suitable data loader provided in datasets folder of edgeai-benchmark or write another
        calib_dataset = dataset_loader(
            path=self.params.dataset.dataset_path,
            split='train',
            shuffle=True,
            num_frames=self.params.compilation.calibration_frames, # num_frames is not critical here,
            annotation_prefix=self.params.dataset.annotation_prefix
        )
        val_dataset = dataset_loader(
            path=self.params.dataset.dataset_path,
            split='val',
            shuffle=False, # can be set to True as well, if needed
            num_frames=self.params.compilation.num_frames, # this num_frames is important for accuracy calculation
            annotation_prefix=self.params.dataset.annotation_prefix
        )

        # it may be easier to get the existing config and modify the aspects that need to be changed
        pipeline_configs = edgeai_benchmark.tools.select_configs(self.settings, self.work_dir)
        num_pipeline_configs = len(pipeline_configs)
        assert num_pipeline_configs == 1, f'specify a unique model name in edgeai-benchmark. found {num_pipeline_configs} configs'
        pipeline_config = list(pipeline_configs.values())[0]

        # dataset settings
        pipeline_config['calibration_dataset'] = calib_dataset
        pipeline_config['input_dataset'] = val_dataset

        # preprocess
        preprocess = pipeline_config['preprocess']
        preprocess.set_input_size(resize=self.params.training.input_resize, crop=self.params.training.input_cropsize)

        # session
        pipeline_config['session'].set_param('work_dir', self.work_dir)
        pipeline_config['session'].set_param('target_device', self.settings.target_device)
        pipeline_config['session'].set_param('model_path', self.params.training.model_export_path)

        # use a short path for the compiled artifacts dir
        compiled_artifact_dir = self._get_compiled_artifact_dir()
        pipeline_config['session'].set_param('run_dir', compiled_artifact_dir)

        runtime_options = pipeline_config['session'].get_param('runtime_options')
        self.meta_layers_names_list = 'object_detection:meta_layers_names_list'
        if self.meta_layers_names_list in runtime_options:
            runtime_options[self.meta_layers_names_list] = self.params.training.model_proto_path
        #
        runtime_options.update(self.params.compilation.get('runtime_options', {}))

        # model_info:metric_reference defined in benchmark code is for the pretrained model - remove it.
        metric_reference = pipeline_config['model_info']['metric_reference']
        for k, v in metric_reference.items():
            metric_reference[k] = None # TODO: get from training
        #

        # metric
        if 'metric' in pipeline_config:
            pipeline_config['metric'].update(self.params.compilation.get('metric', {}))
        elif 'metric' in self.params.compilation:
            pipeline_config['metric'] = self.params.compilation.metric
        #
        if isinstance(pipeline_config['metric'], dict) and 'label_offset_pred' in pipeline_config['metric']:
            dataset_info = val_dataset.get_dataset_info()
            categories = dataset_info['categories']
            min_cat_id = min([cat['id'] for cat in categories])
            pipeline_config['metric']['label_offset_pred'] = min_cat_id
        #
        self.pipeline_configs = pipeline_configs

    def run(self):
        ''''
        The actual compilation function. Move this to a worker process, if this function is called from a GUI.
        '''
        # run the accuracy pipeline
        edgeai_benchmark.tools.run_accuracy(self.settings, self.work_dir, self.pipeline_configs)
        # package artifacts
        edgeai_benchmark.tools.package_artifacts(self.settings, self.work_dir, out_dir=self.package_dir, custom_model=True)
        # make a symlink to the packaged artifacts
        # internally we use a short path as tidl has file path length restrictions
        # for use outside, create symlink to a more descriptive file
        packaged_artifact_path = self._get_packaged_artifact_path()
        utils.make_symlink(packaged_artifact_path, self.params.compilation.model_packaged_path)
        return self.params

    def _get_settings(self, model_selection=None):
        settings = edgeai_benchmark.config_settings.ConfigSettings(
                        self.settings_file,
                        target_device=self.params.common.target_device,
                        model_selection=model_selection,
                        modelartifacts_path=self.params.compilation.compilation_path,
                        tensor_bits=self.params.compilation.tensor_bits,
                        calibration_frames=self.params.compilation.calibration_frames,
                        calibration_iterations=self.params.compilation.calibration_iterations,
                        num_frames=self.params.compilation.num_frames,
                        runtime_options=None,
                        detection_threshold=self.params.compilation.detection_threshold,
                        parallel_devices=None,
                        dataset_loading=False,
                        save_output=self.params.compilation.save_output,
                        input_optimization=False,
                        tidl_offload=self.params.compilation.tidl_offload
        )
        return settings

    def _get_compiled_artifact_dir(self):
        compiled_artifact_dir = os.path.join(self.work_dir, 'modelartifacts')
        return compiled_artifact_dir

    def _get_packaged_artifact_path(self):
        compiled_artifact_dir = self._get_compiled_artifact_dir()
        compiled_package_file = compiled_artifact_dir.replace(self.work_dir, self.package_dir) + '.tar.gz'
        return compiled_package_file

    def _get_final_artifact_name(self):
        pipeline_config = list(self.pipeline_configs.values())[0]
        session_name = pipeline_config['session'].get_param('session_name')
        target_device_suffix = self.params.common.target_device.lower()
        run_name_splits = list(os.path.split(self.params.common.run_name))
        final_artifact_name = '_'.join(run_name_splits + [session_name, target_device_suffix])
        return final_artifact_name

    def _replace_artifact_name(self, artifact_name):
        artifact_basename = os.path.splitext(os.path.basename(artifact_name))[0]
        artifact_basename = os.path.splitext(artifact_basename)[0]
        final_artifact_name = self._get_final_artifact_name()
        artifact_name = artifact_name.replace(artifact_basename, final_artifact_name)
        return artifact_name

    def _has_logs(self):
        log_dir = self._get_compiled_artifact_dir()
        if (log_dir is None) or (not os.path.exists(log_dir)):
            return False
        #
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        if len(log_files) == 0:
            return False
        #
        return True

    def _get_base_dirs(self):
        work_dir = os.path.join(self.settings.modelartifacts_path, 'work')
        package_dir = os.path.join(self.settings.modelartifacts_path, 'pkg')
        return work_dir, package_dir

    def get_params(self):
        return self.params
