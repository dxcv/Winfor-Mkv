# -*- coding:utf-8 -*-
# ! python3


from WindPy import w
from Mkv_constant import *
from dateutil.relativedelta import relativedelta
from datetime import datetime


class BTdate(object):
    """处理回测时间点序列相关"""
    def __init__(self, start, end, freq):
        self._start = start
        self._end = end
        self._freq = freq

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def freq(self):
        return self._freq

    def get_backtest_dates(self):
        """返回对应回测频率的重新回测日期"""
        seq_dict = {
            "M": lambda x: self.get_seq_m(*x),
            "W": lambda x: self.get_seq_w(*x),
            "D": lambda x: self.get_seq_d(*x)
        }
        return seq_dict[self.freq]((self._start, self._end))

    def get_eval_dates(self, ref_seq):
        """返回对应回测频率的rebalance后持仓收益评估日期"""
        seq_dict = {
            "M": lambda x: self._eval_seq_m(x),
            "W": lambda x: self._eval_seq_w(x),
            "D": lambda x: self._eval_seq_d(x)
        }
        return seq_dict[self.freq](ref_seq)

    def get_backtest_first_date(self, num_d):
        """返回第一次回测所需要提取数据的最早日期"""
        if not w.isconnected():
            w.start()
        first = w.tdaysoffset(-(num_d - 1), self._start).Data[0][0].strftime("%Y-%m-%d")
        return first

    @staticmethod
    def get_seq_m(start, end):
        if not w.isconnected():
            w.start()
        seq = w.tdays(start, end, "Period=M").Data[0]
        seq = [dd.strftime("%Y-%m-%d") for dd in seq]
        return seq

    @staticmethod
    def get_seq_w(start, end):
        if not w.isconnected():
            w.start()
        # wind的w.tdays函数准确性较差，需要严格检验
        seq = w.tdays(start, end, "Period=W").Data[0]
        if seq[-1].weekday() != 4:
            seq.pop()
        seq = [dd.strftime("%Y-%m-%d") for dd in seq]
        return seq

    @staticmethod
    def get_seq_d(start, end):
        if not w.isconnected():
            w.start()
        seq = w.tdays(start, end).Data[0]
        seq = [dd.strftime("%Y-%m-%d") for dd in seq]
        return seq

    @staticmethod
    def _eval_seq_d(seq_d):
        if not w.isconnected():
            w.start()
        seq = seq_d.copy()
        seq.pop(0)
        last = seq[-1]
        next_ = w.tdaysoffset(1, last).Data[0][0].strftime("%Y-%m-%d")
        seq.append(next_)
        return seq

    @staticmethod
    def _eval_seq_w(seq_w):
        if not w.isconnected():
            w.start()
        seq = seq_w.copy()
        seq.pop(0)
        last = seq[-1]
        tail = (datetime(*map(int, last.split("-"))) +
                relativedelta(months=1)).strftime("%Y-%m-%d")
        next_ = w.tdays(last, tail, "Period=W").Data[0][1].strftime("%Y-%m-%d")
        seq.append(next_)
        return seq

    @staticmethod
    def _eval_seq_m(seq_m):
        if not w.isconnected():
            w.start()
        seq = seq_m.copy()
        seq.pop(0)
        last = seq[-1]
        tail = (datetime(*map(int, last.split("-")[:2]), 1) +
                relativedelta(months=2)).strftime("%Y-%m-%d")
        next_ = w.tdays(last, tail, "Period=M").Data[0][1].strftime("%Y-%m-%d")
        seq.append(next_)
        return seq

