from openrtist_engine import OpenrtistEngine
import time
import os
import torch

from gabriel_server import cognitive_engine
import openrtist_pb2

BASEDIR = os.path.dirname(os.path.abspath(__file__))
MAX_COUNT = 501


class TimingEngine(OpenrtistEngine):
    def __init__(self, compression_params, adapter):
        super().__init__(compression_params, adapter)
        self.new_client_request = False
        self.count = 0
        self.last_time = time.time()
        self.t0 = None
        self.t1 = 0.
        self.t2 = 0.
        self.t3 = None
        self.gpu_time = 0.
        self.logfile = None
        self.logtext = ""

    def handle(self, input_frame):
        self.t0 = time.time()

        extras = cognitive_engine.unpack_extras(openrtist_pb2.Extras, input_frame)
        if extras.style == "?":
            if not self.new_client_request:
                self.new_client_request = True
                self.count = 0
                self.logtext = ""
                self.logfile = os.path.join(BASEDIR, "Server-Log-" + str(int(self.t0)) + ".txt")
        else:
            self.new_client_request = False

        result_wrapper = super().handle(input_frame)
        self.t3 = time.time()

        self.count += 1
        pre = (self.t1 - self.t0) * 1000
        infer = (self.t2 - self.t1) * 1000
        post = (self.t3 - self.t2) * 1000
        wait = (self.t0 - self.last_time) * 1000
        # fps = 1.0 / (self.t3 - self.last_time)
        # print("# {}\ttime = {}".format(self.count, self.t0))
        self.logtext += ("#{}, time = {}, done = {}, pre = {:.3f} ms, infer = {:.3f} ms, post = {:.3f} ms, wait = {:.3f} ms\n"
                         .format(self.count, self.t0, self.t3, pre, self.gpu_time, post, wait))

        if self.count == MAX_COUNT:
            with open(self.logfile, "a") as logfile:
                logfile.write(self.logtext)
            print("Log written to file.")
            self.count = 0
            self.logtext = ""
        # print("infer-time(): {:.2f} ms\tgpu-time: {:.2f} ms\tdiff = {:.4f}".format(infer, self.gpu_time, infer - self.gpu_time))
        self.last_time = self.t3

        return result_wrapper

    def inference(self, preprocessed):
        starter, ender = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
        torch.cuda.synchronize()
        starter.record()
        self.t1 = time.time()
        post_inference = super().inference(preprocessed)
        ender.record()
        torch.cuda.synchronize()
        self.t2 = time.time()
        self.gpu_time = starter.elapsed_time(ender)

        return post_inference
