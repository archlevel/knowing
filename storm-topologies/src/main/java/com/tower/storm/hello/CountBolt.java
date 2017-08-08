package com.tower.storm.hello;

import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;

import org.apache.log4j.Logger;

import backtype.storm.task.OutputCollector;
import backtype.storm.task.TopologyContext;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.base.BaseRichBolt;
import backtype.storm.tuple.Fields;
import backtype.storm.tuple.Tuple;
import backtype.storm.tuple.Values;

import com.tower.storm.hello.util.MutableInteger;

public class CountBolt extends BaseRichBolt {

    private static final long serialVersionUID = -1636219900771522002L;

    private static Logger logger = Logger.getLogger(CountBolt.class);
    private OutputCollector collector;

    private Map<String, Map<Integer, MutableInteger>> datasourceTypeidCount = new HashMap<String, Map<Integer, MutableInteger>>();
    private Map<Integer, MutableInteger> typeidCount;

    private Long time;
    private String datasource;
    private Integer typeid;

    private WhetherToStats whetherToStats = new WhetherToStats() {

        private static final long serialVersionUID = 6847347742948088745L;

        @Override
        void stats(Long statsTime) {
            for (Entry<Integer, MutableInteger> entry : typeidCount.entrySet()) {
                collector.emit(new Values(statsTime, entry.getKey(), entry.getValue().get()));
            }
        }

        @Override
        void clear() {
            typeidCount.clear();
        }

        @Override
        void event() {
            MutableInteger count = typeidCount.get(typeid);
            if (count == null) {
                typeidCount.put(typeid, new MutableInteger());
            } else {
                count.increment();
            }
        }

    };

    public void prepare(@SuppressWarnings("rawtypes") Map stormConf, TopologyContext context,
            OutputCollector collector) {

        this.collector = collector;
    }

    public void execute(Tuple input) {

        try {

            time = input.getLongByField("time");
            datasource = input.getStringByField("datasource");
            typeid = input.getIntegerByField("typeid");

            typeidCount = datasourceTypeidCount.get(datasource);
            if (typeidCount == null) {
                typeidCount = new HashMap<Integer, MutableInteger>();
                datasourceTypeidCount.put(datasource, typeidCount);
            }

            whetherToStats.go(time, datasource);

        } catch (Exception e) {
            logger.debug(e);
        } finally {
            collector.ack(input);
        }

    }

    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        declarer.declare(new Fields("stats_time", "typeid", "value"));
    }

}
