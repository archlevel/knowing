package com.tower.storm.hello.rules;

import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

import com.tower.storm.hello.rules.Filter.FieldType;

public class Rule {

    public enum RuleType { COUNT, UNIQUE, AVERAGE, NINETY }

    private String datasourceString;
    private Map<String, FieldType> datasource;
    private RuleType ruleType;
    private String field;
    private Boolean logging;
    private List<Filter> filters;
    private Integer version;
    public Integer getVersion() {
        return version;
    }
    public void setVersion(Integer version) {
        this.version = version;
    }
    public String getDatasourceString() {
        return datasourceString;
    }
    public void setDatasourceString(String datasourceString) {
        this.datasourceString = datasourceString;
    }
    public Map<String, FieldType> getDatasource() {
        return datasource;
    }
    public void setDatasource(Map<String, FieldType> datasource) {
        this.datasource = datasource;
    }
    public RuleType getRuleType() {
        return ruleType;
    }
    public void setRuleType(RuleType ruleType) {
        this.ruleType = ruleType;
    }
    public String getField() {
        return field;
    }
    public void setField(String field) {
        this.field = field;
    }
    public Boolean getLogging() {
        return logging;
    }
    public void setLogging(Boolean logging) {
        this.logging = logging;
    }
    public List<Filter> getFilters() {
        return filters;
    }
    public void setFilters(List<Filter> filters) {
        this.filters = filters;
    }

    @SuppressWarnings("unchecked")
    public boolean matches(Map<String, String> row) {

        for (Filter filter : filters) {

            String filterField = filter.getField();

            switch (datasource.get(filterField)) {
            case STRING:

                String stringContent = row.get(filterField);
                if (stringContent == null) {
                    return false;
                }

                Boolean stringCondition = null;
                switch (filter.getStringOperator()) {
                case EQUALS:
                    stringCondition = stringContent.equals((String) filter.getContent());
                    break;
                case CONTAINS:
                    stringCondition = stringContent.contains((String) filter.getContent());
                    break;
                case STARTSWITH:
                    stringCondition = stringContent.startsWith((String) filter.getContent());
                    break;
                case ENDSWITH:
                    stringCondition = stringContent.endsWith((String) filter.getContent());
                    break;
                case REGEX:
                    stringCondition = ((Pattern) filter.getContent()).matcher(stringContent).matches();
                    break;
                case IN:
                    stringCondition = ((List<String>) filter.getContent()).contains(stringContent);
                    break;
                }

                if (stringCondition == null || (stringCondition && filter.getNegative()) || (!stringCondition && !filter.getNegative())) {
                    return false;
                }

                break;

            case NUMERIC:

                double numericContent;
                try {
                    numericContent = Double.parseDouble(row.get(filterField));
                } catch (Exception e) {
                    return false;
                }

                Boolean numericCondition = null;
                switch (filter.getNumericOperator()) {
                case EQ:
                    numericCondition = numericContent == ((Number) filter.getContent()).doubleValue();
                    break;
                case NEQ:
                    numericCondition = numericContent != ((Number) filter.getContent()).doubleValue();
                    break;
                case GT:
                    numericCondition = numericContent > ((Number) filter.getContent()).doubleValue();
                    break;
                case GTE:
                    numericCondition = numericContent >= ((Number) filter.getContent()).doubleValue();
                    break;
                case LT:
                    numericCondition = numericContent < ((Number) filter.getContent()).doubleValue();
                    break;
                case LTE:
                    numericCondition = numericContent <= ((Number) filter.getContent()).doubleValue();
                    break;
                case IN:
                case NIN:
                    List<Number> inList = (List<Number>) filter.getContent();
                    boolean in = false;
                    for (Number inItem : inList) {
                        if (numericContent == inItem.doubleValue()) {
                            in = true;
                            break;
                        }
                    }
                    if (filter.getNumericOperator() == Filter.NumericOperator.IN) {
                        numericCondition = in;
                    } else {
                        numericCondition = !in;
                    }
                    break;
                }

                if (numericCondition == null || !numericCondition) {
                    return false;
                }

                break;
            }

        }

        return true;

    }

}
