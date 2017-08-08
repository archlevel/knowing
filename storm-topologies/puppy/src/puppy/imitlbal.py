import zmq
import msgpack
import time
import random
import sys

sites = ('.tower.com', '.aifang.com', '.haozu.com', '.jinpu.com')
statuses = (200, 200, 200, 200, 200, 301, 302)
urls = ('/rental/broker/', '/rental/broker/n/', '/rental/landlord/', '/rental/sublessor/')

def rand_ip():
    def rand_255():
        return int(random.random() * 255)
    return '192.168.200.%d' % (rand_255())

socket = zmq.Socket(zmq.Context.instance(), zmq.PUSH)
socket.bind('ipc:///tmp/storm.ipc')

if len(sys.argv) > 1:
    interval = float(sys.argv[1])
else:
    interval = 0.01

while True:
    try:
        line = '- %f %s - -  [%s +0800] %s "GET %s HTTP/1.1" %d - "-" "-" "-" "-" - "- -"'\
               % (random.random() * 2,
                  rand_ip(),
                  time.strftime('%d/%b/%Y:%H:%M:%S'),
                  sites[int(random.random() * len(sites))],
                  urls[int(random.random() * len(urls))] + str(int(random.random() * 99999999)) + '?from=baidu',
                  statuses[int(random.random() * len(statuses))])
        print line
        socket.send(msgpack.packb(line))
        time.sleep(interval)

    except KeyboardInterrupt:
        break
