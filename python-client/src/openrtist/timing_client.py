import time
import os

import websockets
from gabriel_protocol import gabriel_pb2
from gabriel_client.websocket_client import WebsocketClient

BASEDIR = os.path.dirname(os.path.abspath(__file__))


class TimingClient(WebsocketClient):
    def __init__(self, host, port, producer_wrappers, consumer):
        super().__init__(host, port, producer_wrappers, consumer)
        self._count = 0
        self._max_count = 500
        self._pre_process_time = 0
        self._send_time = 0
        self._response_time = 0
        self._post_process_time = 0
        self._logfile = os.path.join(BASEDIR, "Client-Timing.txt")
        self._logtext = ""

    def _process_response(self, response):
        self._response_time = round(time.time() * 1000.)
        super()._process_response(response)
        if response.return_token:
            self._post_process_time = round(time.time() * 1000.)
            self._logtext += "{}\tClient Recv {}\n{}\tClient Done {}\n".format(
                response.frame_id + 1, self._response_time,
                response.frame_id + 1, self._post_process_time)
            if response.frame_id + 1 == self._max_count:
                with open(self._logfile, "w") as logfile:
                    logfile.write(self._logtext)
                print("Log written to file.")
                self._logtext = ""

    async def _producer_handler(self, producer, source_name):
        await self._welcome_event.wait()
        source = self._sources.get(source_name)
        assert source is not None, (
            "No engines consume frames from source: {}".format(source_name))

        while self._running:
            await source.get_token()

            input_frame, self._pre_process_time = await producer()
            if input_frame is None:
                source.return_token()
                continue

            from_client = gabriel_pb2.FromClient()
            from_client.frame_id = source.get_frame_id()
            from_client.source_name = source_name
            from_client.input_frame.CopyFrom(input_frame)

            try:
                await self._send_from_client(from_client)
            except websockets.exceptions.ConnectionClosed:
                return  # stop the handler

            source.next_frame()

    async def _send_from_client(self, from_client):
        await super()._send_from_client(from_client)
        self._send_time = round(time.time() * 1000.)
        self._logtext += "{}\tClient Gen {}\n{}\tClient Send {}\n".format(
            from_client.frame_id + 1, self._pre_process_time,
            from_client.frame_id + 1, self._send_time)
