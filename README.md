# 美版白2文本汉化(仅文本汉化)

## Setup
- make
- Python 3.4+
- [ndstool (2.2.0)](https://github.com/devkitPro/ndstool)
- Linux 环境 (native or Windows Subsystem for Linux)

## Creators
- 字库文件来自黑白重译版
- [PlatinumMaster](https://github.com/PlatinumMaster)
- [文本读取/写入代码 by hzla](https://github.com/hzla/Pokeweb-Live)

## Bug
- VAR无法作为文本使用
- 头数据地址0x4的字节有时候可能会和别的软件得到的结果不一样，待修复（a003/651，a003/662）
- 空文本不会有任何数据，而有的软件会有数据，暂时不知道会不会有事
