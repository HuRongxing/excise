#!phthon3
#下载网页

from selenium import webdriver
import os
import logging

#logging.basicConfig(level=logging.DEBUG,format="%(asctime)s - %(levelname)s - %(message)s")

def get_classes(driver,class_name):
    """查找所需的类元素标签"""
    return driver.find_elements_by_class_name(class_name)

def get_text(slm_clt,text_tag='td'):
    """获取指定标签的文本"""
    texts = []
    contents = slm_clt.find_elements_by_tag_name("td")
    for content in contents:
        print(content.text)
        texts.append(content.text)
    return texts

def get_link(slm_clt,text_tag = 'a',atb = 'href'):
    """查找链接地址"""
    try:
        return slm_clt.find_element_by_tag_name(text_tag).get_attribute(atb)
    except:
        return ''

def read_to_next(driver,county,class_tag):
    """抓取文本保存到变量"""
    county['next']=[]
    url=county['link']
    if county['link'] == '':
           pass
    else:
        driver.get(url)
        countys = get_classes(driver,class_tag)
        for slm_clt in countys:
            cap_cnt = {}
            cap_cnt['link'] = get_link(slm_clt)
            cap_cnt['text'] = get_text(slm_clt)
            county['next'].append(cap_cnt)
    return county

if __name__ == '__main__':
    #网页驱动
    driver=webdriver.Firefox()
    #driver=webdriver.Ie()
    #不同层级的HTML类名称
    class_tag = ['citytr','countytr','towntr','villagetr','a']
    #记录当前所在层级，用于获取当前层级HTML类名称
    i_f = 0
    #初始化四川省的数据
    sc_areacode = [{'text':['510000000000','四川省'],
                   'link':'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/51.html'
                  }]
    #定义迭代函数，进入不同层级抓取信息
    def read_contents(driver,contents):
        global i_f
        global class_tag

        for county in contents:
            i_f = i_f + 1
            logging.debug('层级+:%s' %(i_f))
            county = read_to_next(driver,county,class_tag[i_f-1])
            read_contents(driver,county['next'])
            i_f = i_f - 1
            logging.debug('层级-:%s' % (i_f))
        return contents

    #运行函数抓取数据
    sc_areacode = read_contents(driver,sc_areacode)

    def write(sssss,text_file):
        if isinstance(sssss, (list)):
            ssssss = ','.join(sssss)
        else:
            ssssss = sssss
        print(ssssss)
        text_file.write(ssssss)
        text_file.write('\n')
    #保存数据到文本文件
    #模拟数据堆栈，保存上级文本信息
    texts = [[]]
    def save_to_text(contents,text_file):
        global texts
        for content in contents:
            ss = texts[-1] + content['text']
            texts.append(ss)
            if content['next'] == []:
                write(ss,text_file)
            else:
                save_to_text(content['next'],text_file)
            texts.pop()

    text_file = open('area_file.txt','w')

    save_to_text(sc_areacode,text_file)
    #保存数据
    print("恭喜，抓取任务已完成！")

"""To do:
1.用OPP实现本文的功能。
2.运行多线程任务进行抓取。
"""

