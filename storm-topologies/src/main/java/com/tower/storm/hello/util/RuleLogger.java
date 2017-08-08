package com.tower.storm.hello.util;

import java.io.InputStream;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import org.apache.log4j.Logger;
import org.msgpack.MessagePack;
import org.zeromq.ZMQ;

public class RuleLogger {

    private final static Logger logger = Logger.getLogger(RuleLogger.class);

    private ZMQ.Context zmqContext;
    private ZMQ.Socket zmqSocket;
    private MessagePack msgpack;

    public void connect() throws Exception {

        Properties prop = new Properties();
        InputStream in = getClass().getResourceAsStream("/config.properties");
        prop.load(in);
        String endpoint = prop.getProperty("rule_logger.endpoint");

        zmqContext = ZMQ.context(1);
        zmqSocket = zmqContext.socket(ZMQ.PUSH);
        zmqSocket.setLinger(60);
        zmqSocket.connect(endpoint);
        logger.info("Connected to " + endpoint);

        msgpack = new MessagePack();

    }

    public void log(Long time, String datasource, Map<String, String> event, List<Integer> rules) {

        Map<String, Object> msg = new HashMap<String, Object>();
        msg.put("time", time);
        msg.put("datasource", datasource);
        msg.put("event", event);
        msg.put("rules", rules);

        byte[] raw = null;
        try {
            raw = msgpack.write(msg);
            if (raw == null) {
                throw new Exception("raw is empty");
            }
        } catch (Exception e) {
            logger.warn("Fail to msgpack, %s", e);
            return;
        }

        zmqSocket.send(raw, 0);

    }

}
