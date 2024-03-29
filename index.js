/*
@Filename	:	index.js
@Created 	:	2021/08/29
@Updated	:	2024/03/29
@Author   	:	goonhope@gmail.com;Teddy;Zhuhai
@Function	:	获取广东备案信息
@Reference	:	node.js -> add  "type": "module"  to package.json file
*/

import fetch from "node-fetch"
//const { JSDOM } = require("jsdom");

var fnow = (now=0,i=1)=>{ var nnow =  new Date(now? now: Date.now()) ; return i ? nnow.getTime() : nnow.toLocaleString()}; 
var strftime = l => l.map((x,i)=>"56".includes(i)?fnow(x,0):x);
var toList =(y) => [Object.keys(y[0]), ...y.map(x=>strftime(Object.values(x)))].map(x=>x.toString()).join("\n");
var toCsv = async (b="", ext="csv") => await llist(b).then(x=>toList(x));
var llist = async (b="", f=false) => { var hold = [], i = 0;
    while (1) {
        var url = "http://210.76.81.107/api/recordNotice?size=2000&page=" + i;
        var data =await fetch(url).then(r =>r.json()); // 加载选项数据
        var fdata = b? data.data.content.filter(x=>x.proCode && x.proCode.includes(b)): data.data.content;
        hold.push(...fdata);
        //console.log("@Page " + i );
        if(f || (data.data.page === data.data.pages -1)){break;};
        i++;};
return hold;};

toCsv()
	.then(x=>console.log(x))
	.catch(err=>console.log(err))
	.finally();
