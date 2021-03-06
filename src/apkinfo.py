#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import sys

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


# 打印对象
def prn_obj(obj):
    print ', '.join(['%s:%s' % item for item in obj.__dict__.items()])


# 换行打印对象
def prn_obj2(obj):
    print '\n'.join(
        [(prn_obj2(item) if isinstance(item, List) else ('%s\t%s' % item)) for item in obj.__dict__.items()])


# 解析存在兼职对的字符串
def analyze_key_value(xml_str):
    key_dict = {}
    package_array = xml_str.split(' ')
    for package_item in package_array:
        item_array = package_item.split('=')
        if len(item_array) != 2:
            continue
        key_dict[item_array[0]] = item_array[1].replace('\'', '').replace('\n', '')
    return key_dict


# apk的信息
class ApkInfo(object):
    packageName = None
    versionCode = 0
    versionName = None

    appName = None
    icLauncher = None

    meta = {}

    # 构造方法
    def __init__(self, apk_path=None):
        if apk_path:
            infosList = os.popen("aapt d badging " + apk_path).readlines()
            self.loadInfo(infosList)

            self.loadMetas(os.popen("aapt dump xmltree " + apk_path + " AndroidManifest.xml").readlines())

    # 获取应用基本信息
    def loadInfo(self, infolist):
        global packageName
        for info in infolist:
            key_dict = analyze_key_value(info)
            if 'package' in info and 'versionCode=' in info:
                self.packageName = key_dict['name']
                self.versionCode = key_dict['versionCode']
                self.versionName = key_dict['versionName']
                continue

            if 'application' in info and 'label=' in info and 'icon=' in info:
                self.appName = key_dict['label']
                self.icLauncher = key_dict['icon']

    # 获取应用meta信息
    def loadMetas(self, xml_tree):
        self.meta = {}
        for i in range(0, len(xml_tree)):
            info = xml_tree[i].replace('\n', '')
            if 'E: meta-data' in info:
                name = xml_tree[i + 1].replace('\n', '').split("=\"")[1].split("\"")[0]
                value = ''
                if 'type 0x' in xml_tree[i + 2]:
                    value = xml_tree[i + 2].replace('\n', '').split('type 0x')[1].split(')')[1]
                elif 'android:resource' in xml_tree[i + 2]:
                    value = xml_tree[i + 2].replace('\n', '').split(')=')[1]
                elif '=@0x' in xml_tree[i + 2]:
                    value = "@" + xml_tree[i + 2].replace("\n", '').split("=@")[1]
                else:
                    value = xml_tree[i + 2].replace('\n', '').split("=\"")[1].split("\"")[0]
                self.meta[name] = value

    def contact_obj2(self, obj):
        array = []
        for item in sorted(obj.__dict__.items(), key=lambda tup: tup[0]):
            if type(item[1]) == dict:
                for key in item[1].keys():
                    array.append('%s:%s\t%s' % (item[0], key, item[1][key]))
            else:
                array.append(('%s\t%s' % item))
        return '\n'.join(array)
