#!/usr/bin/env python3
# -*- coding:utf-8 -*- 
# author：yuanlang 
# creat_time: 2020/8/31 下午4:54
# file: frida_interface.py

import frida, sys


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

__all__ = [script]
