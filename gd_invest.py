# -*- coding: utf-8 -*-
"""
@Filename	:	gd_invest.py
@Created 	:	2019/04/14
@Updated	:	2024/06/01
@Author 	:	goonhope@gmail.com; Teddy; Zhuhai
@Function	:	广东技改备案、投资备案信息获取--自动更新
@Process 	:	读取已有文本-> 获取json文件 -> 写入文件
@WitNote	:	备注
@Reference	:	引用
"""
import json
from fire import Fire
from require import CNUM, tsleep, open_txt, excel,fetch,time_from,google_hder


class GD:
    """广东技改、投资备案"""
    def __init__(self,size=2000,inv="",inn=''):
        self.base,self.b,self.inv,self.inn = 'http://210.76.81.107/api/recordNotice',False, inv, inn
        self.k, self.hold, self.p, self.s, self.of = '', [], 0, size, f'blist{inv and "_"+ inv}.log'
        self.i, self.o = 'pages total content'.split(), open_txt(file=self.of)
        self.hd = {  # 'Cookie': 'SESSIONID=517F1ADC412EA4F00A7AE122066C7E12',
            'Host': 'gd.tzxm.gov.cn', 'Origin': 'https://gd.tzxm.gov.cn', "DNT": "1",
            'Content-Type': 'application/json;charset=UTF-8',
            'Referer': 'https://gd.tzxm.gov.cn/PublicityInformation/PublicityHandlingResultsList.html',
            'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'X-Requested-With': 'XMLHttpRequest',
            "sec-ch-ua": '''"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"'''}

    def get_list(self):
        """获取list"""
        while True:
            p = dict(size=self.s,page=self.p) if not self.inv else json.dumps(
                 {"flag": f"1{'3' if self.inv == 'N' else ''}", "nameOrCode": self.inn, "pageSize": self.s, "city": '', "pageNumber": self.p + 1})
            h = google_hder(self.hd) if self.inv else None
            if (info := fetch(self.base, h, p, json=True,g=not self.inv)) and (info := info["data"]):
                pages, c, content = [info.get(x) for x in self.i]
                print(f"@items: {c}, list pages: {self.p:02}/{pages}")
                if content: self.hold.extend(self.dealx(content,self.inv))
                if self.p == pages - 1 or self.b: break
                else:self.p += 1; tsleep(2,1)
            else: return print('@ERROR !')

    def dealx(self,hold,year=''):
        """字典处理"""
        holdx = []
        for en,x in enumerate(hold):
            if str(x.get("id")) != (self.o and len(self.o) >1 and self.o[1][0]) and ('2024' in x.get('finishDate') if year else True):
                info = {i:time_from(j / 1000) if 'Time' in i and isinstance(j,int) else
                            str(j).replace('\t',' ').strip() for i,j in x.items() if j and not isinstance(j, (dict,list))}
                holdx.append(info)
            else: self.b = True; break
        return holdx

    def deal(self,where=''):
        """数据处理"""
        self.k = list(self.hold[0].keys()) if not self.o else self.o[0]
        v = ([[x.get(i) for i in self.k] for x in self.hold] if self.hold else []) + self.o[1:]
        if v != self.o[1:]: open_txt([self.k] + v, self.of)
        if where and (where := CNUM.get(where)[-1].strip('0')):
            v = [i for i in v if i and i[2] and where in i[2]]
        self.hold = [self.k] + v

    @excel(na="blist", t=False)
    def go(self,where='珠海'):
        """执行"""
        if self.inv:
            self.base = r"https://gd.tzxm.gov.cn/tzxmspweb/api/publicityInformation/" + \
                        ("selectByPageBA" if 'BA' in self.inv else "selectJnscByPage")
            self.i = 'totalPage totalRow list'.split()
        self.get_list()
        self.deal(where)
        return self.hold


def go(where='珠海'):
    """执行 投资: _BA, 节能: _N"""
    where, inv, *_ = where.split('_') + [""] 
    GD(inv=inv).go(where)


if __name__ == '__main__':
    Fire(go)
