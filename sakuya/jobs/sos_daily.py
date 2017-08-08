# -*- coding: utf-8 -*-

import StringIO
import datetime
from turbomail import Message, interface
from sqlalchemy.orm import sessionmaker
from sakuya.models import engine_sakuya_db
from sakuya.models.sakuya_db import Charts, Categories,Users
from sakuya.lib import chart as libchart, graph as libgarph
from sakuya.config import get_config

import matplotlib
import matplotlib.pyplot as plt

from matplotlib.dates import MinuteLocator, DateFormatter, AutoDateFormatter, AutoDateLocator
from matplotlib.ticker import FuncFormatter

CHARTS = [
    (4951, 1),
    (4957, 1),
    (4958, 1),
    (4959, 1),
    (4961, 1),
    (4962, 1),
    (4963, 1),
    (4964, 1),
    (7352, 1),

    (4420, 2),
    (7342, 2),
    (7343, 2),
    (7350, 2),
    (7351, 2)
]

class Job(object):

    def __init__(self):
        self.session = sessionmaker(bind=engine_sakuya_db)()

        self.config = get_config('webapp')
        mail_config = {}
        mail_config['mail.on'] = self.config['turbomail']['enable']
        mail_config['mail.manager'] = self.config['turbomail']['manager']
        mail_config['mail.transport'] = self.config['turbomail']['transport']
        mail_config['mail.smtp.server'] = 'smtp.126.com'
        mail_config['mail.smtp.username'] = 'alert@126.com'
        mail_config['mail.smtp.password'] = 'alert@126.com'
        interface.start(mail_config)

    def run(self):

        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.dt_start = today - datetime.timedelta(days=8)
        self.dt_end = (today - datetime.timedelta(days=1)).replace(hour=23, minute=59, second=59)

        imgs1 = []
        imgs2 = []
        self.owner = []
        for chart_id, draw_type in CHARTS:
            chart = self.session.query(Charts).get(chart_id)
            category = self.session.query(Categories).get(chart.cate_id)
            if chart.owner =='':
                print 'no owner'
            else:
                users = self.session.query(Users).filter_by(username=chart.owner).first()
                self.owner.append(users.email)

            title = u'%s::%s' % (category.name, chart.name)
            print chart_id, title.encode('utf-8')

            img = getattr(self, 'draw_%d' % draw_type)(chart.id)

#            with open('%d.png' % chart_id, 'w') as f:
#                f.write(img.getvalue())

            if draw_type == 1:
                imgs1.append((chart_id, title, img))
            elif draw_type == 2:
                imgs2.append((chart_id, title, img))

        self.send_email(imgs1, imgs2)

    def draw_1(self, id):

        data = libchart.get_chart_data(self.session, self.dt_start, self.dt_end, [[id, datetime.timedelta()]])

        x = []
        y = []
        for k, v in data.iteritems():
            x.append(datetime.datetime.strptime(k, '%Y%m%d%H%M'))
            y.append(v[0])

        if y[0] is None:
            y[0] = 0
        if y[-1] is None:
            y[-1] = 0

        fig = plt.figure(figsize=(1024 / 80, 300 / 80))
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(x, y, color='blue')
        ax.grid(True, axis='y')

        ax.set_ylim(0)

        locator = AutoDateLocator()
        formatter = AutoDateFormatter(locator)
        formatter.scaled[(1.)] = '%Y-%m-%d'
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)

        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_size(9)
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_size(9)

        f = StringIO.StringIO()
        fig.savefig(f, bbox_inches='tight')
        plt.close()
        f.seek(0)
        return f

    def draw_2(self, id):

        data = libchart.get_chart_data(self.session, self.dt_start, self.dt_end, [[id, datetime.timedelta()]], daily=True)

        x = []
        y = []
        for k, v in data.iteritems():
            x.append(datetime.datetime.strptime(k, '%Y%m%d0000'))
            if v[0] is None:
                y.append(1)
            else:
                y.append(v[0])

        fig = plt.figure(figsize=(400 / 80, 200 / 80))
        ax = fig.add_subplot(1, 1, 1)
        ax.bar(x, y, width=0.4, align='center', color='blue')
        ax.grid(True, axis='y')

        ax.set_ylim(0)
        locator = AutoDateLocator()
        formatter = AutoDateFormatter(locator)
        formatter.scaled[(1.)] = '%m-%d'
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)

        def yaxis_formatter(y, pos):

            def r(i):
                i = round(i, 2)
                if i == int(i):
                    i = int(i)
                return i

            if y < 1e3:
                return int(y)
            elif y < 1e6:
                return '%sK' % r(y / 1e3)
            else:
                return '%sM' % r(y / 1e6)

        ax.yaxis.set_major_formatter(FuncFormatter(yaxis_formatter))

        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_size(9)
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_size(9)

        f = StringIO.StringIO()
        fig.savefig(f)
        plt.close()
        f.seek(0)
        return f

    def send_email(self, imgs1, imgs2):
        day_str = datetime.datetime.strftime(datetime.datetime.today(),"%Y-%m-%d")
        mail = Message()
        mail.subject = u'#%s#SOS日报' % day_str
        mail.sender = 'alert@126.com'
        #mail.to = self.config['sos_receiver']
        self.owner.append('kevinkuang@126.com')
        self.owner.append('gywang@126.com')
        self.owner.append('justin@126.com')
        self.owner.append('enzhang@126.com')
        self.owner.append('andycao@126.com')
        self.owner.append('fzhou@126.com')
        mailto = list(set(self.owner))
        mail.to = ','.join(mailto)

        mail.encoding = 'utf-8'
        mail.plain = u'本邮件由Knowing系统自动发送，如有疑问请联系运维团队，谢谢。'

        title_style = 'font-size: 15px; font-weight: bold; padding-top: 10px;'

        items = [u'<p>Hi All,</p><p>本邮件由Knowing系统自动发送，实时数据可<a href="http://knowing.corp.126.com/monitor/341">点此查看</a>，如有疑问请联系运维团队，谢谢。</p>']
        for img in imgs1:
            items.append(u'<div style="%s">%s</div><p><img src="cid:%d.png"></p>' % (title_style, img[1], img[0]))
            mail.embed(img[2], u'%d.png' % img[0])

        items.append('<table border="0" cellspacing="0" cellpadding="0" width="1024">')
        for i in xrange(0, len(imgs2), 2):
            items.append(u'<tr><td><div style="%s">%s</div><img src="cid:%d.png"></td>' % (title_style, imgs2[i][1], imgs2[i][0]))
            mail.embed(imgs2[i][2], u'%d.png' % imgs2[i][0])
            if i + 1 < len(imgs2):
                items.append(u'<td valign="bottom"><div style="%s">%s</div><img src="cid:%d.png"></td></tr>' % (title_style, imgs2[i+1][1], imgs2[i+1][0]))
                mail.embed(imgs2[i+1][2], u'%d.png' % imgs2[i+1][0])
            else:
                items.append(u'<td>&nbsp;</td></tr>')
        items.append('</table>')
        mail.rich = u''.join(items)

        print 'Sending email...'
        mail.send()

if __name__ == '__main__':
    Job().run()
