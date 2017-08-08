# -*- coding: utf-8 -*-

from collections import OrderedDict
from sakuya import get_zk

datasources = OrderedDict((
    ('access_log', OrderedDict((
        ('request_time', ('numeric', '请求时间（单位：秒）', '0.217')),
        ('upstream_response_time', ('numeric', '返回时间（单位：秒）', '0.215')),
        ('remote_addr', ('string', '客户端IP', '222.67.171.155')),
        ('request_length', ('numeric', '请求内容大小', '32')),
        ('upstream_addr', ('string', '服务端IP及端口', '10.10.6.30:20080')),
        ('time_local', ('string', '访问时间', '26/Jul/2012:15:35:19 +0800')),
        ('host', ('string', '域名', 'shanghai.anjuke.com')),
        ('request_method', ('string', '请求方法', 'GET')),
        ('request_url', ('string', 'URL', '/prop/view/127014571')),
        ('request_protocol', ('string', '请求协议', 'HTTP/1.1')),
        ('status', ('numeric', '返回状态', '200')),
        ('bytes_send', ('numeric', '字节数', '91123')),
        ('http_referer', ('string', 'Referer', 'http://shanghai.anjuke.com/sale/')),
        ('http_user_agent', ('string', 'User Agent', 'Mozilla/4.0 (compatible;)')),
        ('gzip_ratio', ('numeric', '压缩比', '3.52')),
        ('http_x_forwarded_for', ('string', '源ip', '222.67.171.155')),
        ('server_addr', ('string', '外网IP', '114.80.230.221')),
        ('cookie_aQQ_ajkguid', ('string', '安居客GUID', '8B7698ED-49B0-0D45-AA72-D26B3C952D89')),
        ('http_ajk', ('string', 'AJK HTTP 头', 'm=app10-083, pv=2014_26_03, jv=ga'))
    ))),
    ('soj', OrderedDict((
        ('stamp', ('numeric', '访问时间', '1346376858365')),
        ('cstamp', ('numeric', '客户端时间', '1346376866290')),
        ('site', ('string', '网站', 'haozu')),
        ('url', ('string', 'URL', 'http://zhengzhou.haozu.com/listing/')),
        ('referer', ('string', 'Referer', 'http://zhengzhou.haozu.com/')),
        ('p', ('string', '页面', 'Listing_V2_IndexPage_All')),
        ('pn', ('string', '页面名称', 'Listing_V2_IndexPage_All')),
        ('rfpn', ('string', 'Referer页面', 'Home_Index_City')),
        ('guid', ('string', 'GUID', '163B7F8A-EA80-2D5A-C6F5-D99127CDA573')),
        ('uguid', ('string', 'UGUID', '7171E8AF-E764-C3F3-B12E-BAD51878B02D')),
        ('sessid', ('string', '会话ID', 'D84B9F81-B458-3151-E797-32C4E45493EA')),
        ('cip', ('string', '客户端IP', '222.143.28.2')),
        ('cid', ('numeric', '城市', '26')),
        ('agent', ('string', 'User Agent', 'Mozilla/4.0 (compatible;)')),
        ('cstparam', ('string', '自定义参数', '{"found":"0"}')),
        ('lui', ('string', 'Unknown', 'Unknown'))
    )))
))

rule_types = OrderedDict((
    ('count', ('计数', False)),
    ('unique', ('唯一值', True)),
    ('average', ('平均值', 'numeric')),
    ('ninety', ('90%值', 'numeric'))
))

operators = {
    'string': (OrderedDict((
        ('equals', '等于'),
        ('contains', '包含'),
        ('startswith', '以...开始'),
        ('endswith', '以...结束'),
        ('regex', '正则表达式'),
        ('in', '属于...')
    )), True),
    'numeric': (OrderedDict((
        ('eq', '等于'),
        ('neq', '不等于'),
        ('gt', '大于'),
        ('gte', '大于等于'),
        ('lt', '小于'),
        ('lte', '小于等于'),
        ('in', '属于...'),
        ('nin', '不属于...')
    )), False)
}

RULES_PATH = '/pyfisheyes/rules'

def set_rule(typeid, content):
    p = '%s/%s' % (RULES_PATH, typeid)
    zk = get_zk()
    zk.ensure_path(p)
    zk.set(p, content)

def delete_rule(typeid):
    p = '%s/%s' % (RULES_PATH, typeid)
    zk = get_zk()
    if zk.exists(p):
        zk.delete(p)
