package com.tower.storm.hello;

import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

import org.apache.log4j.Logger;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;

import backtype.storm.spout.SpoutOutputCollector;
import backtype.storm.task.TopologyContext;
import backtype.storm.topology.IRichSpout;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.base.BaseRichSpout;
import backtype.storm.tuple.Fields;
import backtype.storm.tuple.Values;

import com.tower.storm.hello.util.Misc;
import com.tower.storm.hello.util.ZMQClient;

public class SojSpout extends BaseRichSpout implements IRichSpout {

    private static final long serialVersionUID = -1781151834108643279L;
    private static Logger logger = Logger.getLogger(SojSpout.class);

    private static final String[] FIELDS = new String[] {
        "stamp",
        "cstamp",
        "site",
        "url",
        "referer",
        "p",
        "pn",
        "rfpn",
        "guid",
        "uguid",
        "sessid",
        "cip",
        "cid",
        "agent",
        "cstparam",
        "lui"
    };

    private SpoutOutputCollector collector;
    private JSONParser parser;
    private long startTime = Misc.nextMinute();

    private ZMQClient zmqClient;

    public void open(@SuppressWarnings("rawtypes") Map conf, TopologyContext context,
            SpoutOutputCollector collector) {

        this.collector = collector;
        this.parser = new JSONParser();

        try {

            Properties prop = new Properties();
            InputStream in = getClass().getResourceAsStream("/config.properties");
            prop.load(in);

            zmqClient = new ZMQClient(prop.getProperty("soj.endpoint"));

        } catch (Exception e) {
            logger.error(String.format("Cannot open SojSpout, %s", e));
            throw new RuntimeException(e);
        }
    }

    public void nextTuple() {

        for (byte[] raw : zmqClient.poll()) {

            try {

                String data = new String(raw);

                int colon = data.indexOf(':');
                if (colon == -1) {
                    return;
                }

                JSONObject map = (JSONObject) parser.parse(data.substring(colon + 1));
                Long stamp = Long.parseLong((String) map.get("stamp"));

                if (stamp < startTime) {
                    return;
                }

                Map<String, String> soj = new HashMap<String, String>();
                for (String field : FIELDS) {
                    soj.put(field, (String) map.get(field));
                }

                soj.put("p", data.substring(13, colon));

                collector.emit(new Values(stamp, soj));

            } catch (Exception e) {
                logger.debug("Fail to parse event.", e);
            }

        }

    }

    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        declarer.declare(new Fields("time", "event"));
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
