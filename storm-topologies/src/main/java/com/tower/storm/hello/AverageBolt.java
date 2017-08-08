package com.tower.storm.hello;

import java.util.ArrayList;
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

public class AverageBolt extends BaseRichBolt {

    private static final long serialVersionUID = -3041763797696823733L;
    private static final long MAX_SIZE = 9999;

    private static Logger logger = Logger.getLogger(AverageBolt.class);
    private OutputCollector collector;

    private Map<String, Map<Integer, List<Double>>> datasourceTypeidAverage = new HashMap<String, Map<Integer, List<Double>>>();
    private Map<Integer, List<Double>> typeidAverage;

    private Long time;
    private String datasource;
    private Integer typeid;
    private Double average;

    private WhetherToStats whetherToStats = new WhetherToStats() {

        private static final long serialVersionUID = 4858913556960403389L;

        @Override
        void stats(Long statsTime) {
            for (Entry<Integer, List<Double>> entry : typeidAverage.entrySet()) {
                collector.emit(new Values(statsTime, entry.getKey(), getAverage(entry.getValue())));
            }
        }

        @Override
        void clear() {
            typeidAverage.clear();
        }

        @Override
        void event() {
            List<Double> list = typeidAverage.get(typeid);
            if (list == null) {
                list = new ArrayList<Double>();
                typeidAverage.put(typeid, list);
            }
            if (list.size() < MAX_SIZE) {
                list.add(average);
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
            average = Double.valueOf(input.getStringByField("average"));

            typeidAverage = datasourceTypeidAverage.get(datasource);
            if (typeidAverage == null) {
                typeidAverage = new HashMap<Integer, List<Double>>();
                datasourceTypeidAverage.put(datasource, typeidAverage);
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

    public int getAverage(List<Double> list) {
        Double sum = 0.0;
        for (Double item : list) {
            sum += item;
        }
        return (int) Math.round(sum * 1e3 / list.size());
    }

}
