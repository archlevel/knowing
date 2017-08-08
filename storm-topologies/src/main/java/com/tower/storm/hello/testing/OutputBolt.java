package com.tower.storm.hello.testing;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import org.apache.commons.lang.StringUtils;

import backtype.storm.task.OutputCollector;
import backtype.storm.task.TopologyContext;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.base.BaseRichBolt;
import backtype.storm.tuple.Tuple;


public class OutputBolt extends BaseRichBolt {

    private OutputCollector collector = null;
    private FileOutputStream fos = null;

    public void prepare(@SuppressWarnings("rawtypes") Map stormConf,
                        TopologyContext context,
                        OutputCollector collector) {
        this.collector = collector;
        try {
            File file = new File("/tmp/parsed_logs.txt");
            this.fos = new FileOutputStream(file);
        }
        catch (IOException e) {
            e.printStackTrace();
        }

    }

    public void execute(Tuple input) {
        Map<String, String> event = (Map<String, String>)
            input.getValueByField("event");

        String[] fields = new String[19];

        fields[0]  = event.get("request_time");
        fields[1]  = event.get("upstream_response_time");
        fields[2]  = event.get("remote_addr");
        fields[3]  = event.get("request_length");
        fields[4]  = event.get("upstream_addr");
        fields[5]  = event.get("time_local");
        fields[6]  = event.get("host");
        fields[7]  = event.get("request_method");
        fields[8]  = event.get("request_url");
        fields[9]  = event.get("request_protocol");
        fields[10] = event.get("status");
        fields[11] = event.get("bytes_send");
        fields[12] = event.get("http_referer");
        fields[13] = event.get("http_user_agent");
        fields[14] = event.get("gzip_ratio");
        fields[15] = event.get("http_x_forwarded_for");
        fields[16] = event.get("server_addr");
        fields[17] = event.get("cookie_aQQ_ajkguid");
        fields[18] = event.get("http_ajk");

        String output = StringUtils.join(fields, "\t");
        try {
            this.fos.write((output + "\n").getBytes());
        }
        catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        return;
    }
}
