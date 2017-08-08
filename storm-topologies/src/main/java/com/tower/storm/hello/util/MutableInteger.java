package com.tower.storm.hello.util;

public class MutableInteger {

    private int value = 1;

    public void increment() {
        ++value;
    }

    public int get() {
        return value;
    }

}
