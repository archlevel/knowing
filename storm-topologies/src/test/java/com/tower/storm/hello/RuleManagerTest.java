package com.tower.storm.hello;

import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import junit.framework.TestCase;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;

import com.tower.storm.hello.rules.Filter;
import com.tower.storm.hello.rules.Filter.FieldType;
import com.tower.storm.hello.rules.Rule;
import com.tower.storm.hello.rules.RuleManager;

public class RuleManagerTest extends TestCase {

    private RuleManager ruleManager;
    private Map<String, Map<String, FieldType>> datasources;
    private JSONParser parser;
    private JSONArray list;

    @Override
    protected void setUp() throws Exception {
        super.setUp();

        ruleManager = new RuleManager();
        datasources = ruleManager.getDatasources();
        parser = new JSONParser();
        list = (JSONArray) parser.parse(new InputStreamReader(getClass().getResourceAsStream("/rules.json")));

    }

    private Rule parseRule(int index) throws Exception {
        JSONObject item = (JSONObject) list.get(index);
        Rule rule = ruleManager.parseRule(item.toJSONString().getBytes(), parser);
        return rule;
    }

    public void testParseRule_0() throws Exception {

        Rule rule = parseRule(0);
        assertEquals(datasources.get("access_log"), rule.getDatasource());
        assertTrue(rule.getLogging());
        assertEquals(Rule.RuleType.NINETY, rule.getRuleType());
        assertEquals("upstream_response_time", rule.getField());
        assertEquals(3, rule.getFilters().size());

        Filter filter = rule.getFilters().get(0);
        assertEquals("host", filter.getField());
        assertEquals(Filter.StringOperator.ENDSWITH, filter.getStringOperator());
        assertFalse(filter.getNegative());
        assertEquals(".haozu.com", (String) filter.getContent());

        filter = rule.getFilters().get(1);
        assertTrue(filter.getNegative());

    }

    public void testParseRule_1() throws Exception {

        Rule rule = parseRule(1);

        assertFalse(rule.getLogging());

        assertNull(rule.getField());

        Filter filter = rule.getFilters().get(1);
        assertEquals(Filter.NumericOperator.GT, filter.getNumericOperator());
        assertEquals((double) 0.2, ((Number) filter.getContent()).doubleValue());

        filter = rule.getFilters().get(2);
        assertEquals((double) 10, ((Number) filter.getContent()).doubleValue());

    }

    @SuppressWarnings("unchecked")
    public void testParseRule_2() throws Exception {

        Rule rule = parseRule(2);

        Filter filter = rule.getFilters().get(0);
        List<String> tmpList1 = new ArrayList<String>();
        tmpList1.add("shanghai.tower.com");
        tmpList1.add("shanghai.aifang.com");
        assertEquals(tmpList1, (List<String>) filter.getContent());

        filter = rule.getFilters().get(1);
        List<Number> tmpList2 = (List<Number>) filter.getContent();
        assertEquals((double) 301, tmpList2.get(0).doubleValue());
        assertEquals((double) 302, tmpList2.get(1).doubleValue());
        assertEquals((double) 8.8, tmpList2.get(2).doubleValue());


    }

    public void testParseRule_3() throws Exception {

        Rule rule = parseRule(3);
        assertEquals(datasources.get("soj"), rule.getDatasource());
        assertEquals(2, rule.getFilters().size());

    }

    public void testRuleMatches_0() throws Exception {
        Rule rule = parseRule(0);

        Map<String, String> row = new HashMap<String, String>();
        row.put("host", "shanghai.haozu.com");
        row.put("request_url", "/rental/broker/n/123456?from=baidu");
        assertTrue(rule.matches(row));

        row.put("host", "shanghai.tower.com");
        assertFalse(rule.matches(row));

        row.put("host", "www.haozu.com");
        assertFalse(rule.matches(row));

        row.put("host", "shanghai.haozu.com");
        row.put("request_url", "/rental/broker/123456");
        assertFalse(rule.matches(row));

    }

    public void testRuleMatches_1() throws Exception {
        Rule rule = parseRule(1);

        Map<String, String> row = new HashMap<String, String>();
        row.put("host", "shanghai.tower.com");
        row.put("upstream_response_time", "0.201");
        assertTrue(rule.matches(row));

        row.put("upstream_response_time", "10.0");
        assertTrue(rule.matches(row));

        row.put("upstream_response_time", "0.200");
        assertFalse(rule.matches(row));

        row.put("upstream_response_time", "10.001");
        assertFalse(rule.matches(row));

        row.put("upstream_response_time", "-");
        assertFalse(rule.matches(row));
    }

    public void testRuleMatches_2() throws Exception {
        Rule rule = parseRule(2);

        Map<String, String> row = new HashMap<String, String>();
        row.put("host", "shanghai.aifang.com");
        row.put("status", "200");
        assertTrue(rule.matches(row));

        row.put("host", "-");
        assertFalse(rule.matches(row));

        row.put("host", "shanghai.tower.com");
        row.put("status", "301.0");
        assertFalse(rule.matches(row));

        row.put("status", "302");
        assertFalse(rule.matches(row));

        row.put("status", "8.8");
        assertFalse(rule.matches(row));

        row.put("status", "");
        assertFalse(rule.matches(row));
    }

    public void testRuleMatches_3() throws Exception {

        Rule rule = parseRule(3);

        Map<String, String> row = new HashMap<String, String>();
        row.put("site", "haozu");
        row.put("pn", "View_Sublessor_ViewPage_He");
        assertTrue(rule.matches(row));

        row.put("site", "tower");
        assertFalse(rule.matches(row));

        row.put("site", "haozu");
        row.put("pn", "Haozu_Home_City");
        assertFalse(rule.matches(row));

    }

}
