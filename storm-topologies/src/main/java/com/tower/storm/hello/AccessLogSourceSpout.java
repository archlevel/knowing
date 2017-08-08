package com.tower.storm.hello;

import java.io.InputStream;
import java.util.Map;
import java.util.Properties;

import org.apache.log4j.Logger;
import org.msgpack.MessagePack;

import backtype.storm.spout.SpoutOutputCollector;
import backtype.storm.task.TopologyContext;
import backtype.storm.topology.IRichSpout;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.base.BaseRichSpout;
import backtype.storm.tuple.Fields;
import backtype.storm.tuple.Values;

import com.tower.storm.hello.util.ZMQClient;

public class AccessLogSourceSpout extends BaseRichSpout implements IRichSpout {

    private static final long serialVersionUID = -6680404047134384730L;
    private static Logger logger = Logger.getLogger(AccessLogSourceSpout.class);
    private SpoutOutputCollector collector;

    private ZMQClient zmqClient;
    private MessagePack msgpack;

    public void open(@SuppressWarnings("rawtypes") Map conf, TopologyContext context,
            SpoutOutputCollector collector) {

        this.collector = collector;
        this.msgpack = new MessagePack();

        try {

            Properties prop = new Properties();
            InputStream in = getClass().getResourceAsStream("/config.properties");
            prop.load(in);

            zmqClient = new ZMQClient(prop.getProperty("access_log.endpoint"));

        } catch (Exception e) {
            logger.error(String.format("Fail to fetch endpoint, %s", e));
            throw new RuntimeException(e);
        }

    }

    public void nextTuple() {
        for (byte[] raw : zmqClient.poll()) {
            String line = null;
            try {
                line = msgpack.read(raw, String.class);
            } catch (Exception e) {
                logger.debug(e);
            }
            if (line == null) {
                continue;
            }
            collector.emit(new Values(line));
        }
    }

    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        declarer.declare(new Fields("raw"));
    }

    @Override
    public void deactivate() {
        zmqClient.disconnect();
    }

    @Override
    public void activate() {
        zmqClient.connect();
    }

}
