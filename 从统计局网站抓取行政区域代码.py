#!phthon3
"""从国家统计局网站抓取统计行政区域代码信息"""

from selenium import webdriver
import os,threading,queue


def get_classes(driver,class_name):
    """查找所需的类元素标签"""
    return driver.find_elements_by_class_name(class_name)

def get_text(slm_clt,text_tag='td'):
    """获取指定标签的文本"""
    texts = []
    contents = slm_clt.find_elements_by_tag_name("td")
    for content in contents:
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

#省、市、县、乡、村、文本，不同行政级别的标签
class_tag = ['citytr','countytr','towntr','villagetr','a']
#多线程数据锁
data_lock = threading.Lock()
#保存结果
areacodes = []

def read_citycodes(contents):
    """
    本代码没有用到OPP，因此需要嵌套函数来保存函数状态
    """
    if not isinstance(contents,list):contents=[contents]
    i_f = 1  #全局变量class_tag的索引，用于标示不同层级的标签
    def read_contents(driver, contents):
        """
        指定一个行政区域的链接地址后，利用该迭代函数抓取内容，直到村级。
        村级行政区域没有下级行政区，下级连接地址为空。
        """
        nonlocal i_f
        global class_tag
        for county in contents:
            i_f = i_f + 1
            county = read_to_next(driver, county, class_tag[i_f - 1])
            read_contents(driver, county['next'])
            i_f = i_f - 1
        return contents
    driver = webdriver.Firefox()
    read_contents(driver, contents)
    driver.close()
    with data_lock:
        areacodes.append(contents)


if __name__ == '__main__':
    #网页驱动
    driver=webdriver.Firefox()
    #driver=webdriver.Ie()
    #初始化四川省的数据
    sc_areacode = [{'text':['510000000000','四川省'],
                   'link':'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/51.html',
                   'next':[]
                  }]
    #获取四川21个市州信息
    sc_areacode[0] = read_to_next(driver,sc_areacode[0],'citytr')
    driver.close()
    #运行多线程抓取四川各个市州信息，每个市州一个线程，最多同时运行3个线程。
    threads = []
    for city in sc_areacode[0]['next']:
        threads.append(threading.Thread(target = read_citycodes,args=(city,)))
    for i in range(len(threads)):
        threads[i].start()
        #每3个市州一组进行读取
        if (i+1) % 3 == 0:
            for m in range(i-2,i+1):
                threads[m].join()
        #四川刚好是21个市州，如果不是3的倍数，还要处理最后几个线程的退出问题。

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

    sc_areacode[0]['next']= []
    for areacode in areacodes:
        sc_areacode[0]['next'].append(areacode[0])
    text_file = open('area_file.txt', 'w')
    save_to_text(sc_areacode, text_file)
    print("恭喜，抓取任务已完成！")

"""To do:
1.用OPP实现本文的功能。
2.运行多线程任务保存数据。
3.捕获子线程运行时的异常，通过queue传递给父线程。
"""

