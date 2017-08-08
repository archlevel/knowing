package com.tower.storm.hello;

import java.util.ArrayList;
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

import com.tower.storm.hello.rules.Rule;
import com.tower.storm.hello.rules.RuleManager;
import com.tower.storm.hello.util.RuleLogger;

public class FilterBolt extends BaseRichBolt {

    private static final long serialVersionUID = 929262917599035659L;
    @SuppressWarnings("unused")
    private static Logger logger = Logger.getLogger(FilterBolt.class);
    private OutputCollector collector;
    private RuleManager ruleManager;
    private RuleLogger ruleLogger;

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

        this.ruleLogger = (RuleLogger) context.getExecutorData("rule_logger");
        if (this.ruleLogger == null) {
            this.ruleLogger = new RuleLogger();
            try {
                this.ruleLogger.connect();
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
            context.setExecutorData("rule_logger", this.ruleLogger);
        }

    }

    @SuppressWarnings("unchecked")
    public void execute(Tuple input) {

        String datasource = input.getSourceComponent();
        Long time = input.getLongByField("time");
        Map<String, String> event = (Map<String, String>) input.getValueByField("event");
        assert(datasource != null && time != null && event != null);

        Map<Integer, Rule> datasourceRules = ruleManager.getDatasourceRules(datasource);
        if (datasourceRules != null) {

            List<Integer> loggedRules = new ArrayList<Integer>();

            for (Entry<Integer, Rule> entry : datasourceRules.entrySet()) {
                Rule rule = entry.getValue();
                if (rule.matches(event)) {

                    switch (rule.getRuleType()) {
                    case COUNT:
                        collector.emit("count", new Values(time, datasource, entry.getKey()));
                        break;

                    case UNIQUE:
                        collector.emit("unique", new Values(time, datasource, entry.getKey(), event.get(rule.getField())));
                        break;

                    case AVERAGE:
                        collector.emit("average", new Values(time, datasource, entry.getKey(), event.get(rule.getField())));
                        break;

                    case NINETY:
                        collector.emit("ninety", new Values(time, datasource, entry.getKey(), event.get(rule.getField())));
                        break;
                    }

                    if (rule.getLogging()) {
                        loggedRules.add(entry.getKey());
                    }

                }
            }

            if (loggedRules.size() > 0) {
                ruleLogger.log(time, datasource, event, loggedRules);
            }

        }

        this.collector.ack(input);
    }

    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        declarer.declareStream("count", new Fields("time", "datasource", "typeid"));
        declarer.declareStream("unique", new Fields("time", "datasource", "typeid", "unique"));
        declarer.declareStream("average", new Fields("time", "datasource", "typeid", "average"));
        declarer.declareStream("ninety", new Fields("time", "datasource", "typeid", "ninety"));
    }

}
