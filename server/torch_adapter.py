# OpenRTiST
#   - Real-time Style Transfer
#
#   Author: Zhuo Chen <zhuoc@cs.cmu.edu>
#           Shilpa George <shilpag@andrew.cmu.edu>
#           Thomas Eiszler <teiszler@andrew.cmu.edu>
#           Padmanabhan Pillai <padmanabhan.s.pillai@intel.com>
#           Roger Iyengar <iyengar@cmu.edu>
#
#   Copyright (C) 2011-2019 Carnegie Mellon University
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#
# Portions of this code borrow from sample code distributed as part of
# Intel OpenVino, which is also distributed under the Apache License.
#
# Portions of this code were modified from sampled code distributed as part of
# the fast_neural_style example that is part of the pytorch repository and is
# distributed under the BSD 3-Clause License.
# https://github.com/pytorch/examples/blob/master/LICENSE

from openrtist_adapter import OpenrtistAdapter
from torch.autograd import Variable
from transformer_net import TransformerNet
from torchvision import transforms
from distutils.version import LooseVersion
import numpy as np
import torch
import os
import logging

from torch.profiler import profile, record_function, ProfilerActivity

logger = logging.getLogger(__name__)
BASEDIR = os.path.dirname(os.path.abspath(__file__))

STARTUP_ONES_SIZE = (240, 320, 3)


class TorchAdapter(OpenrtistAdapter):
    def __init__(self, cpu_only, default_style):
        super().__init__(default_style)

        self.cpu_only = cpu_only

        # We do not need to compute gradients. This saves memory.
        torch.set_grad_enabled(False)

        self.style_model = TransformerNet()

        self._g = None
        self._graph_captured = False
        self._init_styles = True
        self.img_resolution = STARTUP_ONES_SIZE  # TODO: update according to first image;
        self._static_input = None
        self._static_output = None

        models_dir = "models"
        self.path = os.path.join(os.getcwd(), "..", models_dir)
        # self._update_model_style(default_style)

        self.content_transform = transforms.Compose([transforms.ToTensor()])

        for name in os.listdir(self.path):
            if name.endswith(".model"):
                self.add_supported_style(name[:-6])

        self._init_styles = False

        # # Feed network an array of all ones. This makes it run faster on the
        # # first real image.
        # ones = np.ones(STARTUP_ONES_SIZE, np.uint8)
        # preprocessed = self.preprocessing(ones)
        # _ = self.inference(preprocessed)

    def set_style(self, new_style):
        if super().set_style(new_style):
            self._update_model_style(new_style)

    def preprocessing(self, img):
        content_image = self.content_transform(img)
        if not self.cpu_only:
            content_image = content_image.cuda()
        content_image = content_image.unsqueeze(0)
        res = Variable(content_image)
        if self._graph_captured:
            self._static_input.copy_(res)
            return
        return res

    def inference(self, preprocessed):
        if self._graph_captured:
            self._g.replay()
            return
            # with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]) as prof:
            #     self._g.replay()
            # return prof
        return self.style_model(preprocessed)

    def postprocessing(self, post_inference):
        if self._graph_captured:
            # post_inference.export_chrome_trace(os.path.join(BASEDIR, "logs", "trace.json"))
            post_inference = self._static_output
        return post_inference.data[0].clamp(0, 255).cpu().numpy().transpose(1, 2, 0)

    def _update_model_style(self, new_style):
        model = os.path.join(self.path, "{}.model".format(new_style))
        self.style_model.load_state_dict(torch.load(model))
        if not self.cpu_only:
            if self._init_styles:
                self.style_model.cuda()
                return
            # Warm-up again
            self._g = None
            self._graph_captured = False
            self._static_input = self.preprocessing(np.ones(self.img_resolution, np.uint8))
            s = torch.cuda.Stream()
            s.wait_stream(torch.cuda.current_stream())
            with torch.cuda.stream(s):
                for _ in range(3):
                    self._static_output = self.inference(self._static_input)
            torch.cuda.current_stream().wait_stream(s)
            # Capture cuda graph
            self._g = torch.cuda.CUDAGraph()
            with torch.cuda.graph(self._g):
                self._static_output = self.inference(self._static_input)
            self._graph_captured = True
