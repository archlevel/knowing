package com.tower.storm.hello.util;

import java.util.Arrays;

import org.apache.log4j.Logger;
import org.zeromq.ZMQ;

public class ZMQClient {

    private final static Logger logger = Logger.getLogger(ZMQClient.class);
    public final static long POLL_INTERVAL = 500 * 1000;
    public final static long MAX_GAP = 10 * 1000;

    private String[] endpoints;
    private ZMQ.Context zmqContext;
    private ZMQ.Poller zmqPoller;
    private SocketInfo[] socketInfos;

    public ZMQClient(String endpoints) {
        this.endpoints = endpoints.split(",");
    }

    public void connect() {
        zmqContext = ZMQ.context(1);
        zmqPoller = zmqContext.poller();
        socketInfos = new SocketInfo[endpoints.length];

        long now = System.currentTimeMillis();
        for (int i = 0; i < endpoints.length; ++i) {
            ZMQ.Socket socket = zmqContext.socket(ZMQ.PULL);
            socket.connect(endpoints[i]);
            int pos = zmqPoller.register(socket, ZMQ.Poller.POLLIN);
            socketInfos[i] = new SocketInfo(socket, pos, now);
        }

        logger.info(String.format("ZeroMQ connected to %s", Arrays.toString(endpoints)));
    }

    public void disconnect() {
        logger.info("Disconnecting ZeroMQ...");
        for (SocketInfo info : socketInfos) {
            info.socket.close();
        }
        zmqContext.term();
    }

    public byte[][] poll() {

        long now = System.currentTimeMillis();
        long events = zmqPoller.poll(POLL_INTERVAL);
        byte[][] data = new byte[(int) events][];

        int j = 0;
        for (int i = 0; i < socketInfos.length; ++i) {

            if (zmqPoller.pollin(socketInfos[i].pos)) {
                data[j++] = socketInfos[i].socket.recv(0);
                socketInfos[i].recv = now;
            } else if (now > socketInfos[i].recv + MAX_GAP) {
                zmqPoller.unregister(socketInfos[i].socket);
                socketInfos[i].socket.close();
                socketInfos[i].socket = zmqContext.socket(ZMQ.PULL);
                socketInfos[i].socket.connect(endpoints[i]);
                socketInfos[i].pos = zmqPoller.register(socketInfos[i].socket, ZMQ.Poller.POLLIN);
                socketInfos[i].recv = now;
                logger.warn("Reconnect to " + endpoints[i]);
            }

        }

        return data;
    }

    class SocketInfo {
        public ZMQ.Socket socket;
        public int pos;
        public long recv;
        public SocketInfo(ZMQ.Socket socket, int pos, long recv) {
            this.socket = socket;
            this.pos = pos;
            this.recv = recv;
        }
    }

}
