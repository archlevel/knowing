package com.tower.storm.hello;

import java.io.Serializable;
import java.util.HashMap;
import java.util.Map;

public abstract class WhetherToStats implements Serializable {

    private static final long serialVersionUID = -6382752225576765990L;

    private Map<String, Long> datasourceNextTime = new HashMap<String, Long>();

    public final int STATS_INTERVAL = 60;

    abstract void stats(Long statsTime);
    abstract void clear();
    abstract void event();

    public void go(Long time, String datasource) {

        Long logTime = Math.round(time / 1000.0);

        Long nextTime = datasourceNextTime.get(datasource);
        if (nextTime == null) {
            datasourceNextTime.put(datasource, getNextTime(logTime));
        } else if (logTime >= nextTime) {
            stats(nextTime);
            clear();
            datasourceNextTime.put(datasource, getNextTime(logTime));
        }

        event();
    }

    private Long getNextTime(Long logTime) {
        return logTime - logTime % STATS_INTERVAL + STATS_INTERVAL;
    }

}
