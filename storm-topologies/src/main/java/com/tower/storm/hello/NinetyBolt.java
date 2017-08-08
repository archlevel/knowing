package com.tower.storm.hello;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
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

public class NinetyBolt extends BaseRichBolt {

    private static final long serialVersionUID = -6005168495365855319L;
    private static final long MAX_SIZE = 9999;

    private static Logger logger = Logger.getLogger(NinetyBolt.class);
    private OutputCollector collector;

    private Map<String, Map<Integer, List<Double>>> datasourceTypeidNinety = new HashMap<String, Map<Integer, List<Double>>>();
    private Map<Integer, List<Double>> typeidNinety;

    private Long time;
    private String datasource;
    private Integer typeid;
    private Double ninety;

    private WhetherToStats whetherToStats = new WhetherToStats() {

        private static final long serialVersionUID = 3867179352283239767L;

        @Override
        void stats(Long statsTime) {
            for (Entry<Integer, List<Double>> entry : typeidNinety.entrySet()) {
                collector.emit(new Values(statsTime, entry.getKey(), getNinety(entry.getValue())));
            }
        }

        @Override
        void clear() {
            typeidNinety.clear();
        }

        @Override
        void event() {
            List<Double> list = typeidNinety.get(typeid);
            if (list == null) {
                list = new ArrayList<Double>();
                typeidNinety.put(typeid, list);
            }
            if (list.size() < MAX_SIZE) {
                insort(list, ninety);
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
            ninety = Double.valueOf(input.getStringByField("ninety"));

            typeidNinety = datasourceTypeidNinety.get(datasource);
            if (typeidNinety == null) {
                typeidNinety = new HashMap<Integer, List<Double>>();
                datasourceTypeidNinety.put(datasource, typeidNinety);
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

    public void insort(List<Double> list, Double item) {
        int index = Collections.binarySearch(list, item);
        if (index >= 0) {
            list.add(index, item);
        } else {
            list.add(- index - 1, item);
        }
    }

    public int getNinety(List<Double> list) {
        return (int) (list.get((int) Math.floor((list.size() - 1) * 0.9)) * 1e3);
    }

}
