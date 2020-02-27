import re


def most_repeat_ip(file_path: str, ip_number: int, ip=None, ip_count=None):
    if ip_count is None:
        ip_count = {}
    if ip is None:
        ip = []
    '''
    Reading ip from file
    '''
    with open(file_path, 'r') as inf:
        for line in inf:
            ip.extend(re.findall(r'[0-9]{1,3}[.][0-9]{1,3}[.][0-9]{1,3}[.][0-9]{1,3}', line))
    '''
    Ip repeat count
    '''
    for i in ip:
        if i in ip_count:
            ip_count[i] += 1
        else:
            ip_count.setdefault(i, 1)
    '''
    Sort and output the most repeated ip
    '''
    ip_count = sorted(ip_count.items(), key=lambda x: x[1], reverse=True)

    for i in range(ip_number):
        print(ip_count[i][0])


if __name__ == '__main__':
    most_repeat_ip(file_path='./hits.txt', ip_number=5)
