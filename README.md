# SekiroPython

## General
SekiroPython是Sekiro集群下主动hook python加解密函数的
本项目是和frida-rpc一同结合，无需使用usb连接手机，也可以使用frida-rpc

## frida-rpc
当你想hook某个so文件可以通过frida来主动hook实现，借助Sekiro实现远程主动Hook

## Qpython
在手机端运行python文件

## 问题
* 本想用qpyton安装frida-tools 摆脱usb连接，直接远程调用。但是frida无法
在qpython中安装，没有对应的编译版本
