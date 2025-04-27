# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import time  # Thêm thư viện time để có thể tạm dừng nếu cần

# --- Phần kiểm tra và cài đặt thư viện ---
try:
    # Sử dụng importlib.metadata (Python 3.8+) để kiểm tra
    import importlib.metadata
    check_pkg = lambda pkg: importlib.metadata.version(pkg)
except ImportError:
    # Fallback cho Python < 3.8 dùng pkg_resources (cần setuptools)
    try:
        import pkg_resources
        check_pkg = lambda pkg: pkg_resources.get_distribution(pkg).version
    except ImportError:
        print("Lỗi: Không tìm thấy 'importlib.metadata' hoặc 'pkg_resources'.")
        print("Vui lòng cài đặt setuptools: python -m pip install setuptools")
        sys.exit(1)

REQUIRED_PACKAGES = ['httpx', 'colorama']
missing_packages = []

print("Đang kiểm tra các thư viện cần thiết...")
for package in REQUIRED_PACKAGES:
    try:
        version = check_pkg(package)
        print(f" - '{package}' (phiên bản {version}) đã được cài đặt.")
    except Exception: # Bắt chung lỗi PackageNotFoundError hoặc DistributionNotFound
        print(f" - '{package}' chưa được cài đặt.")
        missing_packages.append(package)

if missing_packages:
    print(f"\nĐang tiến hành cài đặt các thư viện còn thiếu: {', '.join(missing_packages)}")
    try:
        # Sử dụng sys.executable để đảm bảo dùng đúng pip của môi trường python hiện tại
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing_packages])
        print("\nĐã cài đặt thành công các thư viện cần thiết.")
        print("Vui lòng chạy lại script.")
        # Có thể tạm dừng để người dùng đọc thông báo
        # time.sleep(3)
        sys.exit(0) # Thoát để script được chạy lại với thư viện mới
    except subprocess.CalledProcessError as e:
        print(f"\nLỖI: Không thể cài đặt các thư viện. Lỗi: {e}")
        print("Vui lòng thử cài đặt thủ công bằng lệnh:")
        print(f"   {sys.executable} -m pip install {' '.join(missing_packages)}")
        sys.exit(1)
    except Exception as e:
        print(f"\nLỖI: Đã xảy ra lỗi không mong muốn trong quá trình cài đặt: {e}")
        sys.exit(1)
# --- Kết thúc phần kiểm tra và cài đặt thư viện ---

# --- Import các thư viện đã được đảm bảo cài đặt ---
import httpx
from colorama import Fore, Style, init

# Khởi tạo colorama, tự động reset màu sau mỗi lần print
init(autoreset=True)

# --- Định nghĩa các màu sắc ---
fr = Fore.RED
fg = Fore.GREEN
fy = Fore.YELLOW
fw = Fore.WHITE
fc = Fore.CYAN
fb = Fore.BLUE
fm = Fore.MAGENTA
rs = Style.RESET_ALL # Reset tất cả style và màu

# --- Danh sách các URL chứa proxy list ---
# *** Danh sách này đã được mở rộng ***
list_proxy_urls = [
    # === Nguồn gốc và bổ sung lần 1 ===
    'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
    'https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt',
    'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt',
    'https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt',
    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
    'https://raw.githubusercontent.com/proxylist-to/proxy-list/main/http.txt',
    'https://raw.githubusercontent.com/yuceltoluyag/GoodProxy/main/raw.txt',
    'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
    'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt',
    'https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt',
    'https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt',
    'https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt',
    'https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/https_proxies.txt',
    'https://api.openproxylist.xyz/http.txt',
    'https://api.proxyscrape.com/v2/?request=displayproxies',
    'https://api.proxyscrape.com/?request=displayproxies&proxytype=http',
    'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
    'https://www.proxydocker.com/en/proxylist/download?email=noshare&country=all&city=all&port=all&type=all&anonymity=all&state=all&need=all',
    'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=anonymous',
    'http://worm.rip/http.txt',
    'https://proxyspace.pro/http.txt',
    'https://multiproxy.org/txt_all/proxy.txt',
    'https://proxy-spider.com/api/proxies.example.txt',
    'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt',
    'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt',
    'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
    'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt',
    'https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt',
    'https://raw.githubusercontent.com/HyperBeats/proxy-list/main/http.txt',
    'https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/http.txt',
    'https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt',
    'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt',
    'http://alexa.lr2b.com/proxylist.txt',
    'https://multiproxy.org/txt_protocol/http.txt',
    'https://multiproxy.org/txt_protocol/https.txt',
    'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all',
    'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt',
    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt',
    'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt',
    'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt',
    'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',

    # === Bổ sung lần 2 (Nhiều nguồn hơn) ===
    'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt',
    'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks4/socks4.txt',
    'https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/http/global/http_checked.txt', # Danh sách đã check (?)
    'https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt',
    'https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt',
    'https://raw.githubusercontent.com/NotUnko/proxy-list/main/proxy-list.txt', # Tổng hợp
    'https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt',
    'https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks4.txt',
    'https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks5.txt',
    'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt',
    'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/https.txt',
    'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks4.txt',
    'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt',
    'https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-Repo/master/proxy_list.txt', # Tổng hợp
    'https://raw.githubusercontent.com/aslisk/proxyhttps/main/https.txt',
    'https://raw.githubusercontent.com/saisuiu/Lionkings-Http-Proxys-Proxies/main/free.txt', # Tổng hợp
    'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt',
    'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt',
    'https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks4.txt',
    'https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks5.txt',
    'https://raw.githubusercontent.com/HyperBeats/proxy-list/main/https.txt',
    'https://raw.githubusercontent.com/HyperBeats/proxy-list/main/socks4.txt',
    'https://raw.githubusercontent.com/HyperBeats/proxy-list/main/socks5.txt',
    'https://www.proxy-list.download/api/v1/get?type=http', # API
    'https://www.proxy-list.download/api/v1/get?type=https', # API
    'https://www.proxy-list.download/api/v1/get?type=socks4', # API
    'https://www.proxy-list.download/api/v1/get?type=socks5', # API
    'https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/http.txt',
    'https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/https.txt',
    'https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/socks4.txt',
    'https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/socks5.txt',
    'https://raw.githubusercontent.com/ValidProxy/ValidProxy/main/http.txt',
    'https://raw.githubusercontent.com/ValidProxy/ValidProxy/main/https.txt',
    'https://raw.githubusercontent.com/ValidProxy/ValidProxy/main/socks4.txt',
    'https://raw.githubusercontent.com/ValidProxy/ValidProxy/main/socks5.txt',
    'https://raw.githubusercontent.com/caliphdev/Proxy-List/master/http.txt',
    'https://raw.githubusercontent.com/caliphdev/Proxy-List/master/https.txt',
    'https://raw.githubusercontent.com/caliphdev/Proxy-List/master/socks4.txt',
    'https://raw.githubusercontent.com/caliphdev/Proxy-List/master/socks5.txt',
    'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt',
    'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt',
    'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks4.txt',
    'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt',
    # Thêm các nguồn API từ proxyscrape cho SOCKS
    'https://api.proxyscrape.com/?request=displayproxies&proxytype=socks4',
    'https://api.proxyscrape.com/?request=displayproxies&proxytype=socks5',
]

# --- Hàm chính thực thi ---
if __name__ == "__main__":
    output_file = "proxy.txt" # Tên file output
    timeout_seconds = 15 # Thời gian chờ cho mỗi request (giây)
    proxies_downloaded = set() # Sử dụng set để tự động loại bỏ trùng lặp
    total_lines_written = 0
    failed_sources = 0

    # Xóa màn hình console
    os.system('cls' if os.name == 'nt' else 'clear')

    # --- Thông báo bắt đầu ---
    print(f"{fc}{Style.BRIGHT}==============================================")
    print(f"{fc}{Style.BRIGHT}   Bắt đầu Script Tải Proxy Tự Động")
    print(f"{fc}{Style.BRIGHT}==============================================")
    print(f"{fb}[INFO] Tệp lưu trữ proxy: {fw}{output_file}")
    print(f"{fb}[INFO] Timeout cho mỗi request: {fw}{timeout_seconds} giây")
    print(f"{fb}[INFO] Số lượng nguồn proxy: {fw}{len(list_proxy_urls)}")
    print(f"{fc}{Style.BRIGHT}----------------------------------------------")

    # --- Kiểm tra và xóa file cũ nếu tồn tại ---
    if os.path.isfile(output_file):
        try:
            os.remove(output_file)
            print(f"{fy}[!] Tệp '{output_file}' đã tồn tại. Đã xóa tệp cũ thành công.")
        except OSError as e:
            print(f"{fr}[LỖI] Không thể xóa tệp cũ '{output_file}': {e}")
            print(f"{fr}Vui lòng kiểm tra quyền ghi hoặc xóa thủ công.")
            sys.exit(1)

    print(f"\n{fb}Đang tiến hành tải proxy từ các nguồn...")

    # --- Vòng lặp tải proxy ---
    # Mở file ở chế độ 'a' (append) để ghi liên tục, encoding='utf-8' để hỗ trợ ký tự quốc tế
    try:
        with open(output_file, 'a', encoding='utf-8') as data_file:
            for index, url in enumerate(list_proxy_urls, 1):
                print(f"{fb} ({index}/{len(list_proxy_urls)}){rs} Đang thử tải từ: {fc}{url}{rs}", end=' ... ')
                try:
                    # Thêm User-Agent giả lập trình duyệt thông thường
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                    
                    # Thực hiện request GET với timeout và cho phép redirect
                    response = httpx.get(url, timeout=timeout_seconds, headers=headers, follow_redirects=True)
                    
                    # Kiểm tra mã trạng thái HTTP, nếu là lỗi (4xx, 5xx) sẽ raise exception
                    response.raise_for_status()

                    # Lấy nội dung text
                    proxies_text = response.text
                    lines_in_batch = 0
                    
                    if proxies_text:
                        # Ghi vào file và thêm dòng mới cuối cùng để phân tách các nguồn
                        data_file.write(proxies_text.strip() + '\n') 
                        # Đếm số dòng thực sự có nội dung và thêm vào set
                        for line in proxies_text.splitlines():
                            proxy = line.strip()
                            # Thêm kiểm tra cơ bản định dạng IP:PORT (đơn giản)
                            if proxy and ':' in proxy and '.' in proxy.split(':')[0]: 
                                proxies_downloaded.add(proxy)
                                lines_in_batch += 1
                        total_lines_written += lines_in_batch # Cập nhật tổng số dòng đã ghi (chỉ tính dòng hợp lệ)

                    if lines_in_batch > 0:
                        print(f"{fg}OK{rs} (Thêm {lines_in_batch} proxy hợp lệ)")
                    else:
                        # Nếu không có dòng nào hợp lệ được thêm, coi như không thành công
                        print(f"{fy}OK nhưng không tìm thấy proxy hợp lệ{rs}")


                # --- Xử lý các lỗi có thể xảy ra khi tải ---
                except httpx.HTTPStatusError as e:
                    print(f"{fr}LỖI HTTP {e.response.status_code}{rs}")
                    failed_sources += 1
                except httpx.TimeoutException:
                    print(f"{fr}LỖI Timeout (Quá {timeout_seconds}s){rs}")
                    failed_sources += 1
                except httpx.RequestError as e:
                    # In ra lỗi cụ thể hơn nếu có thể
                    error_message = str(e)
                    if "Name or service not known" in error_message or "Could not resolve host" in error_message:
                         print(f"{fr}LỖI Không phân giải được tên miền{rs}")
                    elif "Connection refused" in error_message:
                         print(f"{fr}LỖI Kết nối bị từ chối{rs}")
                    else:
                        print(f"{fr}LỖI Mạng: {error_message}{rs}")
                    failed_sources += 1
                except Exception as e: # Bắt các lỗi không mong muốn khác
                    print(f"{fr}LỖI Không xác định: {e}{rs}")
                    failed_sources += 1

    except IOError as e:
        print(f"\n{fr}[LỖI NGHIÊM TRỌNG] Không thể mở hoặc ghi vào tệp '{output_file}': {e}")
        print(f"{fr}Vui lòng kiểm tra quyền ghi thư mục.")
        sys.exit(1)

    # --- Thông báo kết quả cuối cùng ---
    print(f"\n{fm}{Style.BRIGHT}==============================================")
    print(f"{fm}{Style.BRIGHT}           Hoàn Thành Quá Trình Tải")
    print(f"{fm}{Style.BRIGHT}==============================================")

    if failed_sources > 0:
        print(f"{fy}[!] Số nguồn tải bị lỗi hoặc không có proxy hợp lệ: {failed_sources} / {len(list_proxy_urls)}")

    final_unique_count = len(proxies_downloaded)

    if final_unique_count > 0:
        print(f"{fg}[✓] Đã tải và lưu thành công {fw}{Style.BRIGHT}{final_unique_count}{rs}{fg} proxy DUY NHẤT và hợp lệ.")
        print(f"{fg}[✓] Dữ liệu đã được lưu vào tệp: {fw}{Style.BRIGHT}{output_file}{rs}")
    else:
        print(f"{fr}[X] Không tải được proxy hợp lệ nào từ tất cả các nguồn.")
        if os.path.isfile(output_file):
             try:
                 # Kiểm tra xem file có nội dung không trước khi xóa
                 if os.path.getsize(output_file) == 0:
                     os.remove(output_file) 
                     print(f"{fy}[INFO] Đã xóa tệp rỗng '{output_file}'.")
                 else:
                     # Có thể file có nội dung nhưng không đúng định dạng proxy
                     print(f"{fy}[INFO] Tệp '{output_file}' có chứa dữ liệu nhưng không có proxy hợp lệ nào được ghi nhận.")
             except OSError:
                 pass # Bỏ qua nếu không xóa được

    print(f"{fm}{Style.BRIGHT}==============================================")
