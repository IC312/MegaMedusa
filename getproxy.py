import json
import datetime
import requests
import re
import time
from requests.exceptions import ConnectionError, HTTPError, RequestException

class DownloadProxies:
    def __init__(self) -> None:
        self.api = {
            'socks4': [
                'https://raw.githubusercontent.com/ObcbO/getproxy/master/file/socks4.txt',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
                'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks4/socks4.txt',
                'https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/socks4.txt',
                'https://raw.githubusercontent.com/TuanMinPay/live-proxy/master/socks4.txt',
                'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks4.txt'
            ],
            'socks5': [
                'https://raw.githubusercontent.com/ObcbO/getproxy/master/file/socks5.txt',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
                'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt',
                'https://raw.githubusercontent.com/TuanMinPay/live-proxy/master/socks5.txt',
                'https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/socks5.txt',
                'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt'
            ],
            'http': [
                'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/https/https.txt',
                'https://raw.githubusercontent.com/ObcbO/getproxy/master/file/http.txt',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
                'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt',
                'https://raw.githubusercontent.com/TuanMinPay/live-proxy/master/http.txt',
                'https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/http.txt',
                'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt',
                'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt'
            ]
        }
        self.proxy_dict = {'socks4': [], 'socks5': [], 'http': []}

    def get_special1(self):
        proxy_list = []
        try:
            r = requests.get("https://www.socks-proxy.net/", timeout=5)
            part = str(r.text).split("<tbody>")[1].split("</tbody>")[0].split("<tr><td>")
            for proxy in part:
                proxy = proxy.split("</td><td>")
                try:
                    proxy_list.append(f"{proxy[0]}:{proxy[1]}")
                except:
                    pass
            return proxy_list
        except:
            return []

    def get_special2(self):
        try:
            summary = json.loads(requests.get('https://proxylist.geonode.com/api/proxy-summary').text)
            for i in range(summary["summary"]['proxiesOnline'] // 100):
                proxies = json.loads(requests.get(
                    f'https://proxylist.geonode.com/api/proxy-list?limit=100&page={i}&sort_by=lastChecked&sort_type=desc').text)
                for p in proxies['data']:
                    protocol = 'http' if p['protocols'][0] == 'https' else p['protocols'][0]
                    self.proxy_dict[protocol].append(f"{p['ip']}:{p['port']}")
        except:
            pass

    def get(self):
        self.proxy_dict['socks4'] += self.get_special1()
        self.get_extra()

        for type in ['socks4', 'socks5', 'http']:
            for api in self.api[type]:
                proxy_list = []
                try_count = 0
                while try_count < 2:
                    try:
                        r = requests.get(api, timeout=5)
                        if r.status_code == requests.codes.ok:
                            proxy_list += re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', r.text)
                            self.proxy_dict[type] += list(set(proxy_list))
                            print(f'> Lấy được {len(proxy_list)} IP {type} từ {api}')
                            break
                    except (ConnectionError, HTTPError) as e:
                        try_count += 1
                        print(f"Tentative {try_count} lỗi khi lấy từ {api}: {e}")
                        if try_count < 2:
                            time.sleep(5)
                        else:
                            print(f"Bỏ qua URL sau {try_count} lần thất bại: {api}")
            print(f'> Hoàn tất lấy proxy {type}')

    def get_extra(self):
        retries = 5
        for q in range(20):
            count = {'http': 0, 'socks5': 0}
            day = datetime.date.today() + datetime.timedelta(-q)
            url = f'https://checkerproxy.net/api/archive/{day.year}-{day.month}-{day.day}'
            try_count = 0
            while try_count < retries:
                try:
                    response = requests.head(url, timeout=10)
                    if response.status_code != 200:
                        raise RequestException(f"API lỗi: {response.status_code}")
                    r = requests.get(url, timeout=30)
                    r.raise_for_status()
                    json_result = json.loads(r.text)
                    for i in json_result:
                        if re.match(r'172\.\d{1,3}\.0\.1', i['ip']):
                            if i['type'] in [1, 2] and i['addr'] in self.proxy_dict['http']:
                                self.proxy_dict['http'].remove(i['addr'])
                            if i['type'] == 4 and i['addr'] in self.proxy_dict['socks5']:
                                self.proxy_dict['socks5'].remove(i['addr'])
                        else:
                            if i['type'] in [1, 2]:
                                count['http'] += 1
                                self.proxy_dict['http'].append(i['addr'])
                            if i['type'] == 4:
                                count['socks5'] += 1
                                self.proxy_dict['socks5'].append(i['addr'])
                    print(f'> Lấy thêm {count["http"]} proxy http từ {r.url}')
                    print(f'> Lấy thêm {count["socks5"]} proxy socks5 từ {r.url}')
                    break
                except (ConnectionError, HTTPError) as e:
                    try_count += 1
                    print(f"Lỗi lần {try_count} với {url}: {e}")
                    if try_count < retries:
                        time.sleep(5)
                    else:
                        print(f"Bỏ qua ngày này sau {try_count} lần lỗi: {url}")
                except RequestException as e:
                    print(f"Lỗi khi kiểm tra API: {e}")
                    break

        self.proxy_dict['socks4'] = list(set(self.proxy_dict['socks4']))
        self.proxy_dict['socks5'] = list(set(self.proxy_dict['socks5']))
        self.proxy_dict['http'] = list(set(self.proxy_dict['http']))
        print('> Hoàn tất lấy proxy bổ sung')

    def save_all(self):
        with open('proxy.txt', 'w') as all_file:
            for proxy_type in self.proxy_dict:
                for proxy in self.proxy_dict[proxy_type]:
                    all_file.write(proxy + '\n')
        print("> Đã lưu tất cả proxy vào file proxy.txt")


if __name__ == '__main__':
    d = DownloadProxies()
    d.get()
    d.save_all()
