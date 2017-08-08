package com.tower.storm.hello.util;

import java.util.Calendar;

public class Misc {

    public static long nextMinute() {
        Calendar calendar = Calendar.getInstance();
        calendar.set(Calendar.SECOND, 0);
        calendar.set(Calendar.MILLISECOND, 0);
        calendar.add(Calendar.MINUTE, 1);
        return calendar.getTimeInMillis();
    }

}
