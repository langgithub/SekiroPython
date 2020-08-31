#!/usr/bin/env python3
# -*- coding:utf-8 -*- 
# author：yuanlang 
# creat_time: 2020/8/31 下午6:04
# file: all_script.py

#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# author：yuanlang
# creat_time: 2020/8/31 下午4:54
# file: frida_interface.py

import frida


def on_message(message, data):
    if message['type'] == 'send':
        print("[*] {0}".format(message['payload']))
    else:
        print(message)


jscode = """
function soHook(){
    var base_address=Module.findBaseAddress('libumejni.so');
    if (base_address!=null){
        console.log("soHook start");
        var str;
        Java.perform(function () {
            str = Java.use("java.lang.String");
        });

    }

    rpc.exports = {
        add: function (body) {
            return new Promise(function(resolve, reject) {
                Java.perform(function () {
                    var application = Java.use("android.app.ActivityThread").currentApplication();
                    var context = application.getApplicationContext();
                    var UmeJni = Java.use('com.umetrip.android.umehttp.security.UmeJni');
                    var result =  UmeJni.sub_0515(context,body);
                    resolve(result)
                });
            });
        }
    };

}
soHook();
"""

process = frida.get_usb_device().attach('com.umetrip.android.msky.app')
script = process.create_script(jscode)
script.on('message', on_message)
script.load()



class SekiroNatMessage(object):
    message_type = 0
    serial_number = 0
    ext = ""
    payload = ""

    def __init__(self, message_type, serial_number, ext, payload):
        self.message_type = message_type
        self.serial_number = serial_number
        self.ext = ext
        self.payload = payload

    def makeMessage(self):
        ext_len = len(self.ext)
        payload_len = len(self.payload)
        header = 1+8+1+ext_len+payload_len
        header_pack = header.to_bytes(length=4, byteorder="big")
        result = header_pack + self.message_type.to_bytes(length=1, byteorder="big") \
                 + self.serial_number.to_bytes(length=8, byteorder="big") \
                 + len(self.ext).to_bytes(length=1, byteorder="big") \
                 + self.ext.encode("utf-8") + self.payload.encode("utf-8")

        return result



import json
from twisted.internet import reactor, protocol, task
from twisted.internet.protocol import ReconnectingClientFactory


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


