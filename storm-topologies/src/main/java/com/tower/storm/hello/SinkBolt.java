package com.tower.storm.hello;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.Timestamp;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;

import org.apache.log4j.Logger;

import backtype.storm.task.OutputCollector;
import backtype.storm.task.TopologyContext;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.base.BaseRichBolt;
import backtype.storm.tuple.Tuple;

import com.tower.storm.hello.rules.Rule;
import com.tower.storm.hello.rules.RuleManager;
import com.mchange.v2.c3p0.ComboPooledDataSource;

public class SinkBolt extends BaseRichBolt {

    private static final long serialVersionUID = -4311754448085027132L;
    private static Logger logger = Logger.getLogger(SinkBolt.class);
    private static final int STATS_INTERVAL = 60;

    private OutputCollector collector;
    private RuleManager ruleManager;
    private Map<String, Set<Integer>> datasourceRules = new HashMap<String, Set<Integer>>();
    private Map<String, Long> datasourceNextTime = new HashMap<String, Long>();

    private SimpleDateFormat dateFormat = new SimpleDateFormat("yyyyMMdd");
    private BlockingQueue<StatsItem> queue = new LinkedBlockingQueue<StatsItem>();

    public void prepare(@SuppressWarnings("rawtypes") Map stormConf, TopologyContext context,
            OutputCollector collector) {

        this.collector = collector;

        this.ruleManager = (RuleManager) context.getExecutorData("rule_manager");
        if (this.ruleManager == null) {
            this.ruleManager = new RuleManager();
            try {
                this.ruleManager.start();
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
            context.setExecutorData("rule_manager", this.ruleManager);
        }

        try {
            SaveThread saveThread = new SaveThread();
            saveThread.init();
            saveThread.start();
        } catch (Exception e) {
            logger.error("Fail to start SaveThread", e);
            throw new RuntimeException();
        }

    }

    public void execute(Tuple input) {

        Long statsTime = input.getLongByField("stats_time");
        Integer typeid = input.getIntegerByField("typeid");
        Integer value = input.getIntegerByField("value");

        if (statsTime != null && typeid != null && value != null) {

            String datasource = ruleManager.getRuleDatasource(typeid);
            if (datasource != null) {

                // whether to compensate
                Long nextTime = datasourceNextTime.get(datasource);
                if (nextTime == null) {
                    datasourceNextTime.put(datasource, getNextTime(statsTime));
                } else if (statsTime >= nextTime) {
                    compensate(datasource, nextTime - STATS_INTERVAL);
                    datasourceNextTime.put(datasource, getNextTime(statsTime));
                }

                // mark the rule has data
                Set<Integer> ruleSet = datasourceRules.get(datasource);
                if (ruleSet == null) {
                    ruleSet = new HashSet<Integer>();
                    datasourceRules.put(datasource, ruleSet);
                }
                ruleSet.add(typeid);
            }

            queue.add(new StatsItem(statsTime, typeid, value));
        }

        this.collector.ack(input);

    }

    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        return;
    }

    private Long getNextTime(Long time) {
        return time - time % STATS_INTERVAL + STATS_INTERVAL;
    }

    private void compensate(String datasource, Long statsTime) {

        Map<Integer, Rule> ruleMap = ruleManager.getDatasourceRules(datasource);
        Set<Integer> ruleSet = datasourceRules.get(datasource);
        if (ruleMap == null || ruleSet == null) {
            return;
        }

        for (Entry<Integer, Rule> entry : ruleMap.entrySet()) {
            if (!ruleSet.contains(entry.getKey())) {
                queue.add(new StatsItem(statsTime, entry.getKey(), 0));
            }
        }

        ruleSet.clear();
    }

    private class StatsItem {
        long statsTime;
        int typeid;
        int value;
        public StatsItem(long statsTime, int typeid, int value) {
            this.statsTime = statsTime;
            this.typeid = typeid;
            this.value = value;
        }
    }

    private class SaveThread extends Thread {

        private ComboPooledDataSource cpds;
        private static final long SAVE_INTERVAL = 5;
        private List<StatsItem> list = new ArrayList<StatsItem>();

        public void init() throws Exception {

            Properties prop = new Properties();
            prop.load(getClass().getResourceAsStream("/c3p0.properties"));

            cpds = new ComboPooledDataSource();
            cpds.setJdbcUrl(prop.getProperty("knowing.jdbcUrl"));
            cpds.setUser(prop.getProperty("knowing.user"));
            cpds.setPassword(prop.getProperty("knowing.password"));

        }

        @Override
        public void run() {

            while (!Thread.interrupted()) {

                long start = System.currentTimeMillis();
                long realTimeout = SAVE_INTERVAL * 1000;

                do {

                    StatsItem item = null;
                    try {
                        item = queue.poll(realTimeout, TimeUnit.MILLISECONDS);
                    } catch (InterruptedException e) {
                        break;
                    }
                    if (item != null) {
                        list.add(item);
                    }

                    realTimeout = SAVE_INTERVAL * 1000 - (System.currentTimeMillis() - start);

                } while (realTimeout > 0);

                if (list.isEmpty()) {
                    logger.debug("Nothing to save.");
                    continue;
                }

                save();
                list.clear();

            }

        }

        private void save() {

            try {

                Connection connection = cpds.getConnection();
                Calendar calendar = Calendar.getInstance();
                int affectedRows = 0;

                for (StatsItem item : list) {

                    try {

                        calendar.setTimeInMillis(item.statsTime * 1000);

                        PreparedStatement stmt = connection.prepareStatement(
                                "INSERT INTO `t_chartdata_" + dateFormat.format(calendar.getTime()) + "` (`f_ds_id`, `f_time`, `f_data`)" +
                                " VALUES (?, ?, ?)");

                        stmt.setInt(1, item.typeid);
                        stmt.setTimestamp(2, new Timestamp(item.statsTime * 1000), calendar);
                        stmt.setInt(3, item.value);

                        affectedRows += stmt.executeUpdate();
                        stmt.close();

                    } catch (Exception e) {
                        logger.warn(e);
                    }

                }

                logger.info(String.format("%d rows inserted, %d failed.", affectedRows, list.size() - affectedRows));

                connection.close();

            } catch (Exception e) {
                logger.warn(e);
            }

        }
    }

}
