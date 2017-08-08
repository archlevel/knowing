package com.tower.storm.hello;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import junit.framework.TestCase;

import com.tower.storm.hello.AverageBolt;
import com.tower.storm.hello.NinetyBolt;

public class MiscellaneousTest extends TestCase {

    public void testInsort() {

        NinetyBolt ninetyBolt = new NinetyBolt();
        List<Double> list = new ArrayList<Double>();

        ninetyBolt.insort(list, 0.2);
        ninetyBolt.insort(list, 0.1);
        assertEquals(Arrays.asList(0.1, 0.2), list);

        ninetyBolt.insort(list, 0.1);
        ninetyBolt.insort(list, 0.2);
        assertEquals(Arrays.asList(0.1, 0.1, 0.2, 0.2), list);

        ninetyBolt.insort(list, 0.05);
        ninetyBolt.insort(list, 0.25);
        ninetyBolt.insort(list, 0.15);
        assertEquals(Arrays.asList(0.05, 0.1, 0.1, 0.15, 0.2, 0.2, 0.25), list);

    }

    public void testNinety() {

        NinetyBolt ninetyBolt = new NinetyBolt();

        assertEquals((int) 0.9e3, ninetyBolt.getNinety(Arrays.asList(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)));
        assertEquals((int) 1.0e3, ninetyBolt.getNinety(Arrays.asList(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1)));
        assertEquals((int) 1.0e3, ninetyBolt.getNinety(Arrays.asList(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2)));
        assertEquals((int) 0.3e3, ninetyBolt.getNinety(Arrays.asList(0.1, 0.2, 0.3, 0.4)));
        assertEquals((int) 0.1e3, ninetyBolt.getNinety(Arrays.asList(0.1)));

    }

    public void testAverage() {

        AverageBolt averageBolt = new AverageBolt();

        assertEquals((int) 0.1e3, averageBolt.getAverage(Arrays.asList(0.1)));
        assertEquals((int) 0.15e3, averageBolt.getAverage(Arrays.asList(0.1, 0.2)));

    }

}
