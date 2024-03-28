# -*- coding: utf-8 -*-
"""
@Filename	:	 info_GDTZ.py
@Created 	:	2019/04/14
@Updated	:	2022/06/19
@Author   	:	goonhope@gmail.com;Teddy;Zhuhai
@Function	:	投资、技改项目备案、节能评估数据抓取-for github
"""

from require import open_txt,google_hder as ghdr,post_,excel,json_to_list,time_from,post_while,CNUM
import time, json, random
from fire import Fire

@excel(na="list.xlsx",t=1)
def get_all_list(city="珠海",num=1000,inv=True):
    """获取投资备案或节能评估公示清单 From 20220709"""
    pages,_,titles = get_ilist(city=city,inv=inv,num=num)
    rows = get_ilist(pages=pages,city=city,num=num,inv=inv)
    rows.insert(0,titles)
    return rows


def get_ilist(code="",city="珠海",inv=True,pages=0,num=1000,pr=None):
    """获取投资备案或节能评估公示清单"""
    url = r"https://gd.tzxm.gov.cn/tzxmspweb/api/publicityInformation/selectByPageBA" if inv else \
            r"https://gd.tzxm.gov.cn/tzxmspweb/api/publicityInformation/selectJnscByPage"
    hd = { #'Cookie': 'SESSIONID=517F1ADC412EA4F00A7AE122066C7E12',
          'Host': 'gd.tzxm.gov.cn', 'Origin': 'https://gd.tzxm.gov.cn',"DNT":"1",'Content-Type': 'application/json;charset=UTF-8',
          'Referer': 'https://gd.tzxm.gov.cn/PublicityInformation/PublicityHandlingResultsList.html',
          'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'Sec-Fetch-Dest': 'empty',
          'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'X-Requested-With': 'XMLHttpRequest',
           "sec-ch-ua": '''"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"'''}
    log = f"invest{'' if inv else '_e'}.log"
    log = f"_{city or 'all'}.".join(log.split("."))
    city = CNUM[city][-1].strip("0") if city and city in CNUM else ""
    data = {"flag": "1", "nameOrCode": code, "pageSize": num, "city": city, "pageNumber": 1}
    if not pages:
        info = post_(url, data=json.dumps(data), hdrs=ghdr(hd), proxy=pr)
        info = info["data"]
        print(len(info["list"]))
        info = info["totalPage"], info["totalRow"],list(info["list"][0].keys())
        print("@共{}页，{}条".format(*info))
        return info
    else:
        hold, ohold, c = [], open_txt(file=log), False
        for page in range(1,pages + 1):
            data.update(dict(pageNumber=page))
            print(page,end="\t")
            info = post_while(url, data=json.dumps(data), hdrs=ghdr(hd), proxy=pr)
            if info:
                info = info["data"]["list"]
                ky = "projectCode" if inv else "proofCode"
                for y in info:
                    if y[ky] and city in y[ky]:
                        rows = [x.replace("\t", "") if isinstance(x,str) else x for x in y.values()]
                        c = choose(ohold, rows[-2],c=-2)
                        if c: break
                        else: hold.extend([rows])
            if c:break
            time.sleep(random.uniform(2.6,4.618))
        print("@查询完毕！")
        if ohold: hold.extend(ohold)
        open_txt(hold,file=log)
        return hold


@excel(na="list.xlsx",t=False)
def get_blist(city="珠海",num=2000):
    """获取技改备案公示清单 From 20220623"""
    _,pages,titles = get_once(city=city,num=num)
    rows = get_once(pages,city=city,num=num)
    rows.insert(0,titles)
    return rows


def get_once(pages=0,num=2000,city="珠海"):
    """广东技改备案系统公示抓取 js
        var strftime = l => l.map((x,i)=>"56".includes(i)?fnow(x,0):x);
        var toList =(y) => [Object.keys(y[0]), ...y.map(x=>strftime(Object.values(x)))].map(x=>x.toString()).join("\n");
        var toCsv = async (b="", ext="json") => {var data = await llist(b).then(x=>toList(x)); fsave(data,"console",ext);};
        var llist = async (b="", f=false) => { var hold = [], i = 0;
            while (1) {
                var url = window.location.href.slice(0,-1) + i;
                var data =await fetch(url).then(r =>r.json()); // 加载选项数据
                fdata = b? data.data.content.filter(x=>x.proCode && x.proCode.includes(b)): data.data.content;
                hold.push(...fdata);
                console.log("@Page " + i );
                if(f || (data.data.page === data.data.pages -1)){break;};
                i++;};
	    return hold;};
    """
    url = f"http://210.76.81.107/api/recordNotice?size={str(num)}&page=0"
    file = f"invest_blist_{city or 'all' }.log"
    dist = CNUM[city][-1].strip("0") if city and city in CNUM else ""
    if not pages:
        info = json_to_list(url)["data"]
        info = info["total"], info["pages"],list(info["content"][0].keys())
        print("@共{1}页，共{0}条".format(*info))
        return info
    else:
        hold, ohold ,c = [], open_txt(file=file), False
        for page in range(pages):
            urlx = url.strip("0") + str(page)
            print(urlx)
            info = json_to_list(urlx)
            if info:
                info = info["data"]['content']
                for y in info:
                    if y["proCode"] and dist in y["proCode"]:
                        rows = [str(time_from(y[x] / 1000)).strip() if "Time" in x else str(y[x]).strip() for x in y]
                        # print(rows)
                        c = choose(ohold, rows[1])
                        if c: break
                        else: hold.extend([rows])
            if c: break
            time.sleep(random.uniform(1,1.618))
        if ohold: hold.extend(ohold)
        open_txt(hold,file=file)
        return hold


def choose(hold,stri,c=1,cl=3):
    """判断循环终止条件"""
    inkeys = [x[c] for x in hold[:cl]] if hold else []
    return stri and any(x in stri for x in inkeys)


if __name__ == '__main__':
    Fire()

