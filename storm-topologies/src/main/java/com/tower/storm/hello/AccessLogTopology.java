package com.tower.storm.hello;

import backtype.storm.Config;
import backtype.storm.LocalCluster;
import backtype.storm.StormSubmitter;
import backtype.storm.topology.TopologyBuilder;
import backtype.storm.tuple.Fields;
import backtype.storm.utils.Utils;

public class AccessLogTopology {

    public static void main(String[] args) throws Exception {

        TopologyBuilder builder = new TopologyBuilder();

        // access log
        builder.setSpout("access_log_source", new AccessLogSourceSpout(), 1);
        builder.setBolt("access_log", new AccessLogBolt(), 2)
                .shuffleGrouping("access_log_source");

        // soj
        builder.setSpout("soj", new SojSpout(), 1);

        // filters
        builder.setBolt("filter", new FilterBolt(), 6)
                .shuffleGrouping("access_log")
                .shuffleGrouping("soj");

        // collectors
        builder.setBolt("count", new CountBolt(), 1)
                .fieldsGrouping("filter", "count", new Fields("typeid"));
        builder.setBolt("unique", new UniqueBolt(), 1)
                .fieldsGrouping("filter", "unique", new Fields("typeid"));
        builder.setBolt("average", new AverageBolt(), 1)
                .fieldsGrouping("filter", "average", new Fields("typeid"));
        builder.setBolt("ninety", new NinetyBolt(), 1)
                .fieldsGrouping("filter", "ninety", new Fields("typeid"));

        // sink
        builder.setBolt("sink", new SinkBolt(), 1)
                .globalGrouping("count")
                .globalGrouping("unique")
                .globalGrouping("average")
                .globalGrouping("ninety");

        // config
        Config conf = new Config();
        conf.setNumWorkers(10);
        conf.setMaxSpoutPending(5000);

        if(args != null && args.length > 0) {

            StormSubmitter.submitTopology(args[0], conf, builder.createTopology());

        } else {
            conf.setDebug(true);
            LocalCluster cluster = new LocalCluster();
            cluster.submitTopology("test", conf, builder.createTopology());
            try {
                Utils.sleep(1800000);
            } finally {
                cluster.killTopology("test");
                cluster.shutdown();
            }

        }

    }

}
