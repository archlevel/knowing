package com.tower.storm.hello.rules;


public class Filter {

    public enum FieldType { STRING, NUMERIC }

    public enum StringOperator {
        EQUALS,
        CONTAINS,
        STARTSWITH,
        ENDSWITH,
        REGEX,
        IN
    }
    public enum NumericOperator {
        EQ,
        GT,
        GTE,
        LT,
        LTE,
        NEQ,
        IN,
        NIN
    }

    private String field;
    private StringOperator stringOperator;
    private NumericOperator numericOperator;
    private Boolean negative;
    private Object content;
    public String getField() {
        return field;
    }
    public void setField(String field) {
        this.field = field;
    }
    public StringOperator getStringOperator() {
        return stringOperator;
    }
    public void setStringOperator(StringOperator stringOperator) {
        this.stringOperator = stringOperator;
    }
    public NumericOperator getNumericOperator() {
        return numericOperator;
    }
    public void setNumericOperator(NumericOperator numericOperator) {
        this.numericOperator = numericOperator;
    }
    public Boolean getNegative() {
        return negative;
    }
    public void setNegative(Boolean negative) {
        this.negative = negative;
    }
    public Boolean isNegative() {
        return negative;
    }
    public void setNegative(boolean negative) {
        this.negative = negative;
    }
    public Object getContent() {
        return content;
    }
    public void setContent(Object content) {
        this.content = content;
    }

}
