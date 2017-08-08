package com.tower.storm.hello;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.log4j.Logger;

import backtype.storm.task.OutputCollector;
import backtype.storm.task.TopologyContext;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.base.BaseRichBolt;
import backtype.storm.tuple.Fields;
import backtype.storm.tuple.Tuple;
import backtype.storm.tuple.Values;

import com.tower.storm.hello.util.Misc;

public class AccessLogBolt extends BaseRichBolt {

    private static final long serialVersionUID = -3046496660889377496L;
    private static Logger logger = Logger.getLogger(AccessLogBolt.class);
    private OutputCollector collector;

    private long startTime = Misc.nextMinute();
    private Pattern oldLogPattern;
    private Pattern newLogPattern;
    private SimpleDateFormat dateFormat = new SimpleDateFormat("dd/MMM/yyyy:HH:mm:ss Z");
    private long[] executionTime = new long[] {0, 0, 0, 0};
    private String executionLog = null;

    public void prepare(@SuppressWarnings("rawtypes") Map stormConf, TopologyContext context,
                        OutputCollector collector) {

        this.collector = collector;

        // '$request_time $upstream_response_time $remote_addr $request_length $upstream_addr  [$time_local] '
        // '$host "$request_method $request_url $request_protocol" $status $bytes_send '
        // '"$http_referer" "$http_user_agent" "$gzip_ratio" "$http_x_forwarded_for" - "$server_addr $cookie_aQQ_ajkguid"'
        this.oldLogPattern = Pattern.compile(
            "([0-9.]+|-) " +
            "([0-9.]+|-) " +
            "([0-9.]+|-) " +
            "([0-9]+|-) " +
            "([0-9.:, ]+|-)  " +
            "\\[([^\\]]+)\\] " +
            "([^ ]+) " +
            "\"([^ ]+) " +
            "([^ ]+) " +
            "([^\"]+)\" " +
            "([0-9]+|-) " +
            "([0-9]+|-) " +
            "\"([^\"]+)\" " +
            "\"([^\"]+)\" " +
            "\"([^\"]+)\" " +
            "\"([^\"]+)\" - " +
            "\"([^ ]+) " +
            "([^\"]+)\"");

        this. newLogPattern = Pattern.compile(
            "([0-9.]+|-)\\t" +
            "([0-9.]+|-)\\t" +
            "([0-9.]+|-)\\t" +
            "([0-9]+|-)\\t" +
            "([0-9.:, ]+|-)\\t" +
            "([^\\t]+)\\t" +
            "([^\\t]+)\\t" +
            "([^ \\t]+) " +
            "([^ \\t]+) " +
            "([^ \\t]+)\\t" +
            "([0-9]+|-)\\t" +
            "([0-9]+|-)\\t" +
            "([^\\t]+)\\t" +
            "([^\\t]+)\\t" +
            "([^\\t]+)\\t" +
            "([^\\t]+)\\t" +
            "([^\\t]+)\\t" +
            "([^\\t]+)\\t" +
            "([^\\t]+)\\t" +
            "([^\\t]+)");

        new ExecuteTimeThread().start();

    }

    public void execute(Tuple input) {

        executionTime[0] = System.nanoTime();

        Boolean newFormat = true;

        try {

            executionLog = input.getStringByField("raw");
            if (executionLog == null) {
                logger.debug("line is null");
                return;
            }

            Matcher matcher = newLogPattern.matcher(executionLog);
            if (!matcher.matches()) {
                newFormat = false;
                matcher = oldLogPattern.matcher(executionLog);
                if (!matcher.matches()) {
                    return;
                }
            }
            executionTime[1] = executionTime[0];

            // parse time
            Date date = null;
            try {
                date = dateFormat.parse(matcher.group(6));
            } catch (Exception e) {
                return;
            }
            if (date == null || date.getTime() < startTime) {
                return;
            }

            Map<String, String> accessLog = new HashMap<String, String>();
            accessLog.put("request_time", matcher.group(1));
            accessLog.put("upstream_response_time", matcher.group(2));
            accessLog.put("remote_addr", matcher.group(3));
            accessLog.put("request_length", matcher.group(4));
            accessLog.put("upstream_addr", matcher.group(5));
            accessLog.put("time_local", matcher.group(6));
            accessLog.put("host", matcher.group(7));
            accessLog.put("request_method", matcher.group(8));
            accessLog.put("request_url", matcher.group(9));
            accessLog.put("request_protocol", matcher.group(10));
            accessLog.put("status", matcher.group(11));
            accessLog.put("bytes_send", matcher.group(12));
            accessLog.put("http_referer", matcher.group(13));
            accessLog.put("http_user_agent", matcher.group(14));
            accessLog.put("gzip_ratio", matcher.group(15));
            accessLog.put("http_x_forwarded_for", matcher.group(16));

            if (newFormat) {
                accessLog.put("server_addr", matcher.group(17) +
                              ":" + matcher.group(18));
                accessLog.put("cookie_aQQ_ajkguid", matcher.group(19));
                accessLog.put("http_ajk", matcher.group(20));
            }
            else {
                accessLog.put("server_addr", matcher.group(17));
                accessLog.put("cookie_aQQ_ajkguid", matcher.group(18));
                accessLog.put("http_ajk", "");
            }

            collector.emit(new Values(date.getTime(), accessLog));
            executionTime[2] = executionTime[0];

        }
        catch (Exception e) {
            e.printStackTrace();
        }
        finally {
            collector.ack(input);
            executionTime[3] = executionTime[0];
        }

    }

    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        declarer.declare(new Fields("time", "event"));
    }

    private class ExecuteTimeThread extends Thread {

        @Override
        public void run() {

            while (!Thread.interrupted()) {

                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < executionTime.length; ++i) {
                    sb.append(String.valueOf(executionTime[i] % 1000000));
                    sb.append(", ");
                }
                sb.append(executionLog);
                logger.info(sb.toString());

                try {
                    Thread.sleep(60000);
                } catch (InterruptedException e) {
                    break;
                }
            }

        }


    }

}
