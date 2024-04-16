import time

import cv2

from gabriel_protocol import gabriel_pb2
from gabriel_client.websocket_client import ProducerWrapper
from gabriel_client.opencv_adapter import OpencvAdapter


class TimingOpenCVAdapter(OpencvAdapter):
    def __init__(self, preprocess, produce_extras, consume_frame,
                 video_capture, source_name):
        super().__init__(preprocess, produce_extras, consume_frame,
                         video_capture, source_name)

    def get_producer_wrappers(self):
        async def producer():
            _, frame = self._video_capture.read()
            if frame is None:
                return None

            pre_process_time = round(time.time() * 1000.)
            frame = self._preprocess(frame)
            _, jpeg_frame = cv2.imencode('.jpg', frame)

            input_frame = gabriel_pb2.InputFrame()
            input_frame.payload_type = gabriel_pb2.PayloadType.IMAGE
            input_frame.payloads.append(jpeg_frame.tobytes())

            extras = self._produce_extras()
            if extras is not None:
                input_frame.extras.Pack(extras)

            return input_frame, pre_process_time

        return [
            ProducerWrapper(producer=producer, source_name=self._source_name)
        ]
