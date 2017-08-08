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
import com.tower.storm.hello.util.UniqueLogger;

public class UniqueBolt extends BaseRichBolt {

    private static final long serialVersionUID = -6377953525736027487L;

    private static Logger logger = Logger.getLogger(UniqueBolt.class);
    private OutputCollector collector;
    private UniqueLogger uniqueLogger;

    private Map<String, Map<Integer, Map<String, MutableInteger>>> datasourceTypeidUnique = new HashMap<String, Map<Integer, Map<String, MutableInteger>>>();
    private Map<Integer, Map<String, MutableInteger>> typeidUnique;

    private Long time;
    private String datasource;
    private Integer typeid;
    private String unique;

    private WhetherToStats whetherToStats = new WhetherToStats() {

        private static final long serialVersionUID = 4587818843620289297L;

        @Override
        void stats(Long statsTime) {
            for (Entry<Integer, Map<String, MutableInteger>> entry : typeidUnique.entrySet()) {
                collector.emit(new Values(statsTime, entry.getKey(), entry.getValue().size()));
                uniqueLogger.log(statsTime, entry.getKey(), entry.getValue());
            }
        }

        @Override
        void clear() {
            typeidUnique.clear();
        }

        @Override
        void event() {

            Map<String, MutableInteger> uniqueMap = typeidUnique.get(typeid);
            if (uniqueMap == null) {
                uniqueMap = new HashMap<String, MutableInteger>();
                typeidUnique.put(typeid, uniqueMap);
            }

            MutableInteger count = uniqueMap.get(unique);
            if (count == null) {
                uniqueMap.put(unique, new MutableInteger());
            } else {
                count.increment();
            }
        }

    };

    public void prepare(@SuppressWarnings("rawtypes") Map stormConf, TopologyContext context,
            OutputCollector collector) {

        this.collector = collector;

        this.uniqueLogger = new UniqueLogger();
        try {
            this.uniqueLogger.connect();
        } catch (Exception e) {
            logger.error("Fail to start UnqiueLogger", e);
            throw new RuntimeException();
        }
    }

    public void execute(Tuple input) {

        try {

            time = input.getLongByField("time");
            datasource = input.getStringByField("datasource");
            typeid = input.getIntegerByField("typeid");
            unique = input.getStringByField("unique");

            typeidUnique = datasourceTypeidUnique.get(datasource);
            if (typeidUnique == null) {
                typeidUnique = new HashMap<Integer, Map<String, MutableInteger>>();
                datasourceTypeidUnique.put(datasource, typeidUnique);
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
