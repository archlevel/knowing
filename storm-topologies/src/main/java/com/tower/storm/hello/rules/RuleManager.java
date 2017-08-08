package com.tower.storm.hello.rules;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.regex.Pattern;

import org.apache.log4j.Logger;
import org.apache.zookeeper.data.Stat;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.yaml.snakeyaml.Yaml;

import com.tower.storm.hello.rules.Filter.FieldType;
import com.tower.storm.hello.rules.Filter.NumericOperator;
import com.tower.storm.hello.rules.Filter.StringOperator;
import com.tower.storm.hello.rules.Rule.RuleType;
import com.netflix.curator.framework.CuratorFramework;
import com.netflix.curator.framework.CuratorFrameworkFactory;
import com.netflix.curator.retry.RetryUntilElapsed;

public class RuleManager {

    private static Logger logger = Logger.getLogger(RuleManager.class);
    private int REFRESH_INTERVAL = 60; // update rules every one minute

    private Map<String, Map<Integer, Rule>> datasourcesRules = new HashMap<String, Map<Integer, Rule>>();
    private Map<String, Map<String, FieldType>> datasources = new HashMap<String, Map<String, FieldType>>();

    public void start() throws Exception {

        getDatasources();
        for (String datasourceString : datasources.keySet()) {
            datasourcesRules.put(datasourceString, new ConcurrentHashMap<Integer, Rule>());
        }

        Properties prop = new Properties();
        InputStream in = getClass().getResourceAsStream("/config.properties");
        prop.load(in);

        CuratorFramework client = CuratorFrameworkFactory.newClient(prop.getProperty("zookeeper.hosts"), new RetryUntilElapsed(3000, 1000));
        client.start();

        new Refresher(client, prop.getProperty("zookeeper.path")).start();

    }

    public Map<Integer, Rule> getDatasourceRules(String datasource) {
        return datasourcesRules.get(datasource);
    }

    public String getRuleDatasource(Integer typeid) {
        for (Entry<String, Map<Integer, Rule>> entry : datasourcesRules.entrySet()) {
            if (entry.getValue().keySet().contains(typeid)) {
                return entry.getKey();
            }
        }
        return null;
    }

    @SuppressWarnings("unchecked")
    public Map<String, Map<String, FieldType>> getDatasources() throws Exception {

        if (datasources.size() == 0) {

            Yaml yaml = new Yaml();
            Map<String, Object> tmpDatasources = (Map<String, Object>) yaml.load(getClass().getResourceAsStream("/datasources.yaml"));
            for (Entry<String, Object> datasourceEntry : tmpDatasources.entrySet()) {
                Map<String, FieldType> datasource = new HashMap<String, FieldType>();
                Map<String, String> tmpDatasource = (Map<String, String>) datasourceEntry.getValue();
                for (Entry<String, String> fieldEntry : tmpDatasource.entrySet()) {
                    datasource.put(fieldEntry.getKey(), FieldType.valueOf(fieldEntry.getValue().toUpperCase()));
                }
                datasources.put(datasourceEntry.getKey(), datasource);
            }

        }

        return datasources;
    }

    public Rule parseRule(byte[] data, JSONParser parser) throws Exception {

        JSONObject map = (JSONObject) parser.parse(new InputStreamReader(new ByteArrayInputStream(data)));

        Rule rule = new Rule();

        String datasourceString = (String) map.get("datasource");
        Map<String, FieldType> datasource = datasources.get(datasourceString);
        if (datasource == null) {
            throw new Exception(String.format("datasource %s not found", datasourceString));
        }
        rule.setDatasourceString(datasourceString);
        rule.setDatasource(datasource);

        Boolean logging = (Boolean) map.get("logging");
        if (logging == null) {
            logging = false;
        }
        rule.setLogging(logging);

        RuleType ruleType = RuleType.valueOf(((String) map.get("rule_type")).toUpperCase());
        rule.setRuleType(ruleType);
        switch (ruleType) {
        case COUNT:
            rule.setField(null);
            break;

        case UNIQUE:
        case AVERAGE:
        case NINETY:
            String field = (String) map.get("field");
            if (!datasource.containsKey(field)) {
                throw new Exception(String.format("field %s not found in datasource %s", field, datasourceString));
            }
            rule.setField(field);
            break;
        }

        List<Filter> filters = new ArrayList<Filter>();
        for (Object filterItemRaw : (JSONArray) map.get("filters")) {

            JSONArray filterItem = (JSONArray) filterItemRaw;

            Filter filter = new Filter();

            String field = (String) filterItem.get(0);
            if (!datasource.containsKey(field)) {
                throw new Exception(String.format("field %s not found in datasource %s", field, datasourceString));
            }
            filter.setField(field);

            switch (datasource.get(field)) {
            case STRING:
                filter.setStringOperator(StringOperator.valueOf(((String) filterItem.get(1)).toUpperCase()));
                filter.setNegative((Boolean) filterItem.get(2));

                switch (filter.getStringOperator()) {
                case EQUALS:
                case CONTAINS:
                case STARTSWITH:
                case ENDSWITH:
                    filter.setContent((String) filterItem.get(3));
                    break;
                case REGEX:
                    filter.setContent(Pattern.compile((String) filterItem.get(3)));
                    break;
                case IN:
                    JSONArray inListRaw = (JSONArray) filterItem.get(3);
                    List<String> inList = new ArrayList<String>();
                    for (Object inItem : inListRaw) {
                        inList.add((String) inItem);
                    }
                    filter.setContent(inList);
                    break;
                }

                break;

            case NUMERIC:
                filter.setNumericOperator(NumericOperator.valueOf(((String) filterItem.get(1)).toUpperCase()));

                switch (filter.getNumericOperator()) {
                case EQ:
                case NEQ:
                case GT:
                case GTE:
                case LT:
                case LTE:
                    filter.setContent((Number) filterItem.get(3));
                    break;
                case IN:
                case NIN:
                    JSONArray inListRaw = (JSONArray) filterItem.get(3);
                    List<Number> inList = new ArrayList<Number>();
                    for (Object inItem : inListRaw) {
                        inList.add((Number) inItem);
                    }
                    filter.setContent(inList);
                    break;
                }

                break;
            }

            filters.add(filter);

        }
        rule.setFilters(filters);

        return rule;
    }

    private class Refresher extends Thread {

        private JSONParser parser = new JSONParser();
        private CuratorFramework client;
        private String path;

        public Refresher(CuratorFramework client, String path) {
            this.client = client;
            this.path = path;
        }

        @Override
        public void run() {

            while (!Thread.interrupted()) {
                refresh();
                try {
                    Thread.sleep(REFRESH_INTERVAL * 1000);
                } catch (InterruptedException e) {}
            }

        }

        private void refresh() {

            List<String> children;
            try {
                children = client.getChildren().forPath(path);
                if (children.isEmpty()) {
                    logger.info("Children list is empty.");
                    return;
                }
            } catch (Exception e) {
                logger.error("Unable to get children.", e);
                return;
            }

            // prepare
            Map<String, Set<Integer>> toRemove = new HashMap<String, Set<Integer>>();
            for (Entry<String, Map<Integer, Rule>> entry : datasourcesRules.entrySet()) {
                toRemove.put(entry.getKey(), new HashSet<Integer>(entry.getValue().keySet()));
            }

            // add or mark deleted
            for (String child : children) {

                Integer typeid = null;
                try {
                    typeid = Integer.valueOf(child);
                } catch (Exception e) {
                    logger.error("Invalid child name: " + child, e);
                    continue;
                }

                String childPath = String.format("%s/%s", path, child);
                Stat stat = new Stat();
                byte[] data = null;
                try {
                    data = client.getData().storingStatIn(stat).forPath(childPath);
                    if (stat.getDataLength() == 0 || data.length == 0) {
                        throw new Exception("Data length is 0.");
                    }
                } catch (Exception e) {
                    logger.error("Unable to get data for " + childPath, e);
                    continue;
                }

                Rule oldRule = null;
                String operation = null;
                for (Entry<String, Set<Integer>> entry : toRemove.entrySet()) {
                    if (entry.getValue().remove(typeid)) {
                        oldRule = datasourcesRules.get(entry.getKey()).get(typeid);
                        break;
                    }
                }
                if (oldRule == null) {
                    operation = "added";
                } else if (oldRule.getVersion() == stat.getVersion()) { // skip
                    continue;
                } else {
                    operation = "updated";
                }

                Rule newRule = null;
                try {
                    newRule = parseRule(data, parser);
                } catch (Exception e) {
                    logger.error("Unable to parse rule for " + childPath, e);
                    continue;
                }
                newRule.setVersion(stat.getVersion());

                if (oldRule != null // datasource not changed
                        && !newRule.getDatasourceString().equals(oldRule.getDatasourceString())) {

                    datasourcesRules.get(oldRule.getDatasourceString()).remove(typeid);
                }
                datasourcesRules.get(newRule.getDatasourceString()).put(typeid, newRule);

                logger.info(String.format("Rule %d %s", typeid, operation));

            }

            // delete
            for (Entry<String, Map<Integer, Rule>> entry : datasourcesRules.entrySet()) {
                for (Integer id : toRemove.get(entry.getKey())) {
                    datasourcesRules.get(entry.getKey()).remove(id);
                    logger.info(String.format("Rule %d deleted.", id));
                }
            }

        }

    }

}
