package com.tower.storm.hello.util;

import java.io.InputStream;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Properties;

import org.apache.log4j.Logger;
import org.msgpack.MessagePack;
import org.msgpack.packer.BufferPacker;
import org.zeromq.ZMQ;

public class UniqueLogger {

    private final static Logger logger = Logger.getLogger(UniqueLogger.class);

    private ZMQ.Context zmqContext;
    private ZMQ.Socket zmqSocket;
    private MessagePack msgpack;

    public void connect() throws Exception {

        Properties prop = new Properties();
        InputStream in = getClass().getResourceAsStream("/config.properties");
        prop.load(in);
        String endpoint = prop.getProperty("unique_logger.endpoint");

        zmqContext = ZMQ.context(1);
        zmqSocket = zmqContext.socket(ZMQ.PUSH);
        zmqSocket.setLinger(1000);
        zmqSocket.connect(endpoint);
        logger.info("Connected to " + endpoint);

        msgpack = new MessagePack();

    }

    public void log(Long time, Integer tid, Map<String, MutableInteger> result) {

        BufferPacker packer = msgpack.createBufferPacker();

        try {

            packer.write(time);
            packer.write(tid);
            for (Entry<String, MutableInteger> entry : result.entrySet()) {
                packer.write(entry.getKey());
                packer.write(entry.getValue().get());
            }

            zmqSocket.send(packer.toByteArray(), 0);

        } catch (Exception e) {

            logger.warn("Fail to pack message.", e);

        } finally {

            try {
                packer.close();
            } catch (Exception e1) {}

        }

    }

}
