package com.tower.storm.hello.testing;

import backtype.storm.Config;
import backtype.storm.LocalCluster;
import backtype.storm.StormSubmitter;
import backtype.storm.topology.TopologyBuilder;
import backtype.storm.tuple.Fields;
import backtype.storm.utils.Utils;

import com.tower.storm.hello.AccessLogBolt;
import com.tower.storm.hello.AccessLogSourceSpout;

public class AccessLogTestingTopology {

    public static void main(String[] args) throws Exception {

        TopologyBuilder builder = new TopologyBuilder();

        // access log
        builder.setSpout("access_log_source", new AccessLogSourceSpout(), 1);
        builder.setBolt("access_log", new AccessLogBolt(), 5)
            .shuffleGrouping("access_log_source");

        // sink
        builder.setBolt("output", new OutputBolt(), 1)
            .globalGrouping("access_log");

        // config
        Config conf = new Config();
        conf.setNumWorkers(10);
        conf.setDebug(false);
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
