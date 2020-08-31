#!/usr/bin/env python3
# -*- coding:utf-8 -*- 
# author：yuanlang 
# creat_time: 2020/8/31 下午1:56
# file: SekiroNatMessage.py

"""
// 消息体
- (NSData *)makeDataWithExt:(NSString *)ext msg:(NSString *)dicStr msgType:(int8_t)msgType serial_number_data:(NSData *)serial_number_data{

    // 类似于byte数组
    NSData *dext = [ext dataUsingEncoding:NSUTF8StringEncoding];
    // 类似于bytebuffer
    NSMutableData * cmdData = [[NSMutableData alloc] init];
    // 字符串转byte数组
    NSData *cmd = [dicStr dataUsingEncoding:NSUTF8StringEncoding];

    // 申请 1 + 8 + 1 + ext实际内容length + dicStr实际内容length
    __int32_t packet_length = sizeof(int8_t) + sizeof(int64_t) + sizeof(int8_t) + (int)[dext length] + (int)cmd.length;
    // 将主机的unsigned long 转为网络字节顺序
    HTONL(packet_length);
    // bytebuffer 填充
    [cmdData appendBytes:&packet_length length:sizeof(__int32_t)];
    //消息类型
    int8_t message_type = msgType;
    [cmdData appendBytes:&message_type length:sizeof(int8_t)];
    //消息id
    if (serial_number_data) {
        [cmdData appendData:serial_number_data];
    } else {
        int64_t serial_number = 0x00;
        [cmdData appendBytes:&serial_number length:sizeof(int64_t)];
    }
    //ext扩展长度
    int8_t ext_length = [dext length];
    [cmdData appendBytes:&ext_length length:sizeof(int8_t)];//no disconnect

    [cmdData appendData:dext];
    [cmdData appendData:cmd];

    return cmdData;
}
"""
from struct import pack, unpack


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
        # packet_length = 1 + 8 + 1 + len(self.ext) + len(self.payload)
        # return pack(">I", packet_length) + self.message_type.to_bytes(length=1, byteorder="big") \
        #        + self.serial_number.to_bytes(length=8, byteorder="big") \
        #        + len(self.ext).to_bytes(length=1, byteorder="big") \
        #        + self.ext.encode("utf-8") + self.payload.encode("utf-8")
        ext_len = len(self.ext)
        payload_len = len(self.payload)
        header = 1+8+1+ext_len+payload_len
        header_pack = header.to_bytes(length=4, byteorder="big")
        result = header_pack + self.message_type.to_bytes(length=1, byteorder="big") \
                 + self.serial_number.to_bytes(length=8, byteorder="big") \
                 + len(self.ext).to_bytes(length=1, byteorder="big") \
                 + self.ext.encode("utf-8") + self.payload.encode("utf-8")

        return result