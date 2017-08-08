import zmq
import time
import msgpack

socket = zmq.Socket(zmq.Context.instance(), zmq.PUSH)
socket.setsockopt(zmq.LINGER, 0)
socket.bind('ipc:///tmp/storm.ipc')

while True:
    try:
        with file('lbal.log') as f:
            for line in f:
                line = line.strip()
                print line
                socket.send(msgpack.packb(line))
                time.sleep(0.1)

    except KeyboardInterrupt:
        break

