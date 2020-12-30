# SekiroPython

## General
SekiroPython是Sekiro集群下主动hook python加解密函数的
本项目是和frida-rpc一同结合，无需使用usb连接手机，也可以使用frida-rpc

## frida-rpc
当你想hook某个so文件可以通过frida来主动hook实现，借助Sekiro实现远程主动Hook

## Termux 上安装 frida-tools
https://bbs.pediy.com/thread-263852.htm

### 安装termux
### 切换源,安装插件
1. adb push yuan.sh /data/local/tmp
2. 打开termux su | cd /data/local/tmp | chmod +x yuan.sh | ./yuan.sh
3. 切换到$用户 exit | pkg install ...
```
sed -i 's@^\(deb.*stable main\)$@#\1\ndeb https://mirrors.tuna.tsinghua.edu.cn/termux/termux-packages-24 stable main@' $PREFIX/etc/apt/sources.list
sed -i 's@^\(deb.*games stable\)$@#\1\ndeb https://mirrors.tuna.tsinghua.edu.cn/termux/game-packages-24 games stable@' $PREFIX/etc/apt/sources.list.d/game.list
sed -i 's@^\(deb.*science stable\)$@#\1\ndeb https://mirrors.tuna.tsinghua.edu.cn/termux/science-packages-24 science stable@' $PREFIX/etc/apt/sources.list.d/science.list
pkg update -y
pkg install -y python
pkg install -y tsu
pkg install -y root-repo
pkg install -y frida-tools
```
### 愉快使用frida-rpc + sekiro + 脱离数据线使用
