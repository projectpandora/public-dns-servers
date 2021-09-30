import sys
import time
import urllib.request
from multiprocessing.dummy import Pool as ThreadPool
import dns.resolver

public_dns_servers = []

if (len(sys.argv) >= 2):
    if ".txt" in sys.argv[1]:
        file1 = open(sys.argv[1], 'r')
        temp_dns_servers = []
        for line in file1.readlines():
            if "#" not in line:
                temp_dns_servers.append(line.strip())
        file1.close()
        public_dns_servers = temp_dns_servers
    else:
        public_dns_servers = sys.argv[1:]
else:
    temp = urllib.request.urlopen(
        "https://public-dns.info/nameservers.txt").read()
    temp_dns_servers = []
    for line in temp.splitlines():
        if b"#" not in line:
            temp_dns_servers.append(line.decode("utf-8").strip())
    public_dns_servers = temp_dns_servers

data = open("/etc/resolv.conf").read().split()
for item in data:
    if len(item.split(".")) == 4:
        public_dns_servers.append(item.strip())

test_domains = [
    "wix-engage-visitors-prod-13.example.com",
    "webfinance.example.com",
    "webtcmgo.example.com",
    "searchanise-ef84.abc.net",
    "wix-engage-visitors-prod-22.abc.net",
    "webpsicologia.abc.net",
    "webordineavvocati.bbc.co.uk",
    "westerncentralny.bbc.co.uk",
    "wati-integration-service.bbc.co.uk",
    "wisp-production-storage.s3.sidn.nl",
    "widgetthemes-live.sidn.nl",
    "webmaringa.sidn.nl",
    "websites-18cb9.nic.io",
    "webimprensaoficial.nic.io",
    "webbeniculturali.nic.io",
    "webtrashiyangtse.python.org",
    "webcafelandia.python.org",
    "webczestochowa.python.org",
    "wakeforest.vnnic.vn",
    "weblinkoutsea01.vnnic.vn",
    "willywilly.vnnic.vn",
    "myenterpriseregistration.vng.com.vn",
    "wm-backend-prod-dot-watermelonmessenger.vng.com.vn",
    "wholebrainteaching-com.vng.com.vn",
    "wxv73zw8wg-flywheel.vng.com.vn",
    "myrepublica.vng.com.vn",
    "webfiles.vng.com.vn",
]

results = {}


def process(dns_server):
    error_case = 0
    total_time = 0
    number_of_tests = 0
    for test_domain in test_domains:
        number_of_tests = number_of_tests + 1
        my_resolver = dns.resolver.Resolver()
        my_resolver.nameservers = [dns_server]
        my_resolver.timeout = 1
        my_resolver.lifetime = 1
        start = time.time()
        try:
            my_resolver.resolve(test_domain, "A")
            error_case = error_case + 1
        except dns.resolver.NXDOMAIN:
            pass
        except:
            error_case = error_case + 1
        end = time.time()
        total_time = total_time + (end - start)
        if (error_case >= 3):
            break
    avg_time = total_time / number_of_tests
    success_rate = (number_of_tests - error_case) / number_of_tests
    return {
        "dns_server": dns_server,
        "avg_time": avg_time,
        "success_rate": success_rate
    }


# make the pool of workers
pool = ThreadPool(256)
results = pool.map(process, public_dns_servers)
# close the pool and wait for the work to finish
pool.close()
pool.join()

sorted_results = sorted(results, key=lambda x: (
    x["avg_time"])
)
count = 0
for result in sorted_results:
    if (result["success_rate"] == 1.0 and result["avg_time"] < 0.1):
        if count == 100:
            break
        count = count + 1
        print(result["dns_server"], flush=True)
