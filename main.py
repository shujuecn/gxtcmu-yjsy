#!/usr/local/bin/python3
# -*- encoding: utf-8 -*-
'''
@Brief  : 面向对象学习记录——爬取广西中医药大学导师信息
@Time   : 2023/02/02 15:31:19
@Author : https://github.com/shujuecn
'''


import requests
from lxml import etree


class Spider(object):

    def __init__(self) -> None:
        self.url = 'https://yjsy.gxtcmu.edu.cn/Category_70/Index.aspx'
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70'
        }

    def get_major_page(self):
        '''
        1.解析主页面
        2.获取各专业页面
        3.调用解析各专业页面方法
        '''
        response = requests.get(self.url, headers=self.headers)

        if response.status_code != 200:
            print('主页面请求失败，程序退出...')
            return

        html = response.content.decode()
        html = etree.HTML(html)
        major_list = html.xpath('//div[@id="sideMenu"]/div/ul/li/a')

        return major_list

    def parse_major_page(self, major_list):
        '''
        解析各专业页面
        :return: None
        '''

        # 遍历各专业页面
        for major in major_list:
            major_name = major.xpath('./text()')[0]
            major_url = 'https://yjsy.gxtcmu.edu.cn/' + major.xpath('./@href')[0]

            response = requests.get(major_url, headers=self.headers)
            if response.status_code != 200:
                print(f'{major_name}页面请求失败，跳过该专业...')
                continue
            html = response.content.decode()
            html = etree.HTML(html)

            # 该专业的页面数量
            page_num = html.xpath('//div[@class="pager"]/span[@class="disabled"]/text()')[0].split('共')[2].split('页')[0]

            print(f'正在解析{major_name}，共{page_num}页...')

            # 遍历该专业的各页
            for page in range(1, int(page_num) + 1):
                page_url = major_url.replace('.aspx', f'_{page}.aspx')
                response = requests.get(page_url, headers=self.headers)
                if response.status_code != 200:
                    print(f'{major_name}第{page}页请求失败，跳过该页面...')
                    continue

                html = response.content.decode()
                html = etree.HTML(html)

                # 该专业该页下的导师列表
                tr_list = html.xpath('//div[@class="mBd"]/ul/li')

                for tr in tr_list:
                    # li标签下没有a标签，跳过该li标签
                    if tr.xpath('./a') == []:
                        continue
                    # 使用字典储存所有信息
                    item = {}
                    title = tr.xpath('./a/text()')[0]
                    item['major'] = major_name
                    item['subject'] = title.split('—')[0]
                    item['name'] = title.split('—')[-1]
                    item['url'] = 'https://yjsy.gxtcmu.edu.cn/' + tr.xpath('./a/@href')[0]

                    # 解析各导师页面信息
                    # item['info'] = self.parse_teacher_page(item['url'])

                    # 导出文件
                    self.save_page(item)

                    # print(item)
                    # return

                print(f'第{page}页保存成功，共{len(tr_list)}条数据...')
            print()

    def parse_teacher_page(self, url):
        '''
        解析各导师页面
        :param url: 导师页面url
        :return: None
        '''
        response = requests.get(url, headers=self.headers)
        html = response.content.decode()
        html = etree.HTML(html)

        # 个人信息
        info = html.xpath('//div[@id="fontzoom"]/p/span/span/text()')
        # 合并信息
        info = ''.join(info)
        return info

    def save_page(self, item):
        '''
        保存数据
        :param item: 数据
        :return: None
        '''
        with open('./gxtcmu-yjsy.csv', 'a', encoding='utf-8') as f:
            f.write(f"{item['major']},{item['subject']},{item['name']}, {item['url']}\n")

    def run(self):
        '''
        主函数
        '''
        major_list = self.get_major_page()
        self.parse_major_page(major_list)


if __name__ == '__main__':
    spider = Spider()
    spider.run()
