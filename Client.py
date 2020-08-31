#!/usr/bin/env python3
# -*- coding:utf-8 -*- 
# author：yuanlang 
# creat_time: 2020/8/31 下午1:50
# file: Client.py

from __future__ import print_function

import json
from SekiroNatMessage import SekiroNatMessage
from twisted.internet import reactor, protocol, task
from twisted.internet.protocol import ReconnectingClientFactory
from frida_interface import script


class EchoClient(protocol.Protocol):
    """Once connected, send a message, then print the result."""
    # 用于暂时存放接收到的数据
    _buffer = b""

    def connectionMade(self):
        # 注册client
        print("conneted")
        msg = SekiroNatMessage(message_type=1, serial_number=0, ext="yuanlang@wechat", payload="")
        self.transport.write(msg.makeMessage())
        task_send_heartbeat = task.LoopingCall(self.send_heartbeat)
        task_send_heartbeat.start(3)

    def dataReceived(self, data):
        "As soon as any data is received, write it back."
        self._buffer = data
        packet_length = int().from_bytes(self._buffer[:4], byteorder='big', signed=True)
        msg_type = int().from_bytes(self._buffer[4:5], byteorder='big', signed=True)
        serial_number = int().from_bytes(self._buffer[5:13], byteorder='big', signed=True)
        ext_len = int().from_bytes(self._buffer[13:14], byteorder='big', signed=True)
        ext = self._buffer[15:15+ext_len].decode("utf-8")
        bodyLength = packet_length - 1 - 8 - 1 - len(ext)
        receive = self._buffer[14+ext_len: 14+ext_len+bodyLength].decode("utf-8")
        ###################以上代码不要动################################
        # 代表主动hook
        if msg_type == 2:
            print(receive)
            receive_body = json.loads(receive)
            # 参数解析
            if "data" not in receive_body:
                result = {"ok": False, "status": -1, "data": "缺失参数data"}
                msg = SekiroNatMessage(message_type=2, serial_number=serial_number,
                                       ext="application/json;charset=utf-8", payload=json.dumps(result))
                self.transport.write(msg.makeMessage())
            else:
                print("执行frida so调用")
                # 主动调用Frida获取sign加密
                sign = script.exports.add(receive_body["data"])
                result = {"ok": True, "status": 1, "data": sign}
                print("sekiro返回{}".format(result))
                msg = SekiroNatMessage(message_type=2, serial_number=serial_number, ext="application/json;charset=utf-8", payload=json.dumps(result))
                self.transport.write(msg.makeMessage())
        else:
            print("heart")
            # 提供一个接口调用，并会写数据

    def connectionLost(self, reason):
        print("connection lost")
        # self.makeConnection()

    def send_heartbeat(self):
        msg = SekiroNatMessage(message_type=7, serial_number=0, ext="", payload="")
        self.transport.write(msg.makeMessage())


class EchoFactory(ReconnectingClientFactory):

    def buildProtocol(self, addr):
        self.resetDelay()
        return EchoClient()

    def clientConnectionFailed(self, connector, reason):
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)


# this connects the protocol to a server running on port 8000
def main():
    f = EchoFactory()
    reactor.connectTCP("172.20.20.85", 11000, f)
    reactor.run()


if __name__ == '__main__':
    main()
