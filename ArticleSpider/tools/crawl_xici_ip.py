# -*- coding: utf-8 -*-

import requests
from scrapy.selector import Selector
import MySQLdb

conn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', password='', db='JobBoleSpider', charset='utf8')
cursor = conn.cursor()


def crawl_ips():
    # 获取西刺免费IP代理池
    headers = {"User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36'}

    ip_list = []
    for i in range(500):
        re = requests.get('http://www.xicidaili.com/nn/{0}'.format(i), headers=headers)

        selector = Selector(text=re.text)
        all_trs = selector.xpath('//*[@id="ip_list"]/tr')

        for tr in all_trs[1:]:
            # FIXME: 在这个循环里用xpath选择器时，有数据重复的bug，待解决
            # speed_str = tr.xpath('//div[@class="bar"]/@title').extract()[0] 这里用 xpath 选择器时数据重复
            speed_str = tr.css('.bar::attr(title)').extract()[0]

            if speed_str:
                speed = float(speed_str.split('秒')[0])
            all_texts = tr.css('td::text').extract()
            ip = all_texts[0]
            port = all_texts[1]

            ip_list.append((ip, port, speed))

        for ip_info in ip_list:
            cursor.execute(
                "insert proxy_ip_pool (ip, port, speed, proxy_type) values ('{0}', '{1}', '{2}', 'http/https')".format(
                    ip_info[0], ip_info[1], ip_info[2]
                )
            )
            conn.commit()


class GetIPRandom(object):
    def delete_ip(self, ip):
        # 从数据库中删除无效的ip
        delete_sql = """
            delete from proxy_ip_pool where ip='{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self, ip, port):
        # 判断ip是否可用
        http_url = "http://www.baidu.com"
        proxy_url = "http://{0}:{1}".format(ip, port)
        try:
            proxy_dict = {
                "http": proxy_url,
            }
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print("invalid ip and port")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                print("effective ip")
                return True
            else:
                print("invalid ip and port")
                self.delete_ip(ip)
                return False

    def get_random_ip(self):
        # 从数据库中随机获取一个可用的ip
        random_sql = """
              SELECT ip, port FROM proxy_ip_pool
              ORDER BY RAND() LIMIT 1
            """
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]

            judge_re = self.judge_ip(ip, port)
            if judge_re:
                return "http://{0}:{1}".format(ip, port)
            else:
                return self.get_random_ip()


if __name__ == "__main__":
    get_ip = GetIPRandom()
    ip = get_ip.get_random_ip()
