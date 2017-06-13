# -*- coding:utf-8 -*-

import requests
import re
import MySQLdb

conn = MySQLdb.connect(host='localhost', user='root', passwd='root', charset='utf8', db='scrapy')
cursor = conn.cursor()


def crawl_ip():
    headers = {'Host':'www.xicidaili.com','Referer':'http://www.xicidaili.com/',
                'User-Agent':'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    insert_sql = "insert into proxy_ip VALUES ('{}', {}, '{}', {}) on duplicate key update speed={}"

    for page in range(1,1000):
        req = requests.get(url='http://www.xicidaili.com/nn/{}'.format(str(page)), headers=headers)
        result = re.findall(r'<td>([\d\.]+)</td>.*?<td>(\d+)</td>.*?<td>(\w+)</td>.*?<div title="([\d\.]+)', req.text, re.S)
        for i in result:
            try:
                cursor.execute(insert_sql.format(*i, i[-1]))
            except Exception as e:
                print('insert failed! ',e)
            else:
                conn.commit()
                print(i, 'insert success!')

    cursor.close()
    conn.close()


class Get_proxy_ip(object):
    def delete_ip(self, ip, port):
        del_sql = 'delete from proxy_ip where ip={} and port={}'
        cursor.execute(del_sql.format(ip, port))
        conn.commit()

    def test_ip(self, ip, port, proxy_type):
        # http_url = 'http://www.qq.com'
        http_url = 'http://123.207.88.97:7020/'
        https_url = 'https://www.baidu.com'
        porxy_url = '{}://{}:{}'.format(proxy_type, ip, port)

        proxies = {
            proxy_type: porxy_url
        }

        try:
            response = requests.get(http_url if proxy_type == 'HTTP' else https_url, proxies=proxies)
        except Exception as e:
            print('Invaild proxy ip!')
            self.delete_ip(ip, port)
            return False
        else:
            if response.status_code >= 200 and response.status_code <=300:
                print('proxy ip effective!')
                return True
            else:
                print('Invaild proxy ip!')
                self.delete_ip(ip, port)
                return False

    def get_rand_ip(self, proxy_type):
        proxy_type = proxy_type.upper() if proxy_type.upper() in ['HTTP', 'HTTPS'] else 'HTTP'
        status = 1
        while status:
            select_sql = "select ip,port,type from proxy_ip where speed<1 and type='{}' order by rand() limit 1;".format(proxy_type)
            cursor.execute(select_sql)
            result = cursor.fetchall()[0]
            if self.test_ip(result[0], str(result[1]), proxy_type):
                global status
                status = 0
                return result

if __name__ == '__main__':
    crawl_ip()