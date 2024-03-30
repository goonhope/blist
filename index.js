/*
@Filename	:	index.js
@Created 	:	2021/08/29
@Updated	:	2024/03/29
@Author   	:	goonhope@gmail.com;Teddy;Zhuhai
@Function	:	获取广东备案信息
@Reference	:	node.js -> add  "type": "module"  to package.json file
*/
import fetch from "node-fetch";
import xlsx from "node-xlsx";
import fs from "fs";

//const { JSDOM } = require("jsdom");
var fnow = (now=0,i=1,a=8)=>{ 
	var nnow =  new Date((now || Date.now()) + a * 3600 * 1000) ;
	return i ? nnow.getTime() : nnow.toJSON().substr(0, 19).replace("T"," ")}; 
var strftime = l => l.map((x,i)=>"56".includes(i)?fnow(x,0):x);
var toList =(y) => [Object.keys(y[0]), ...y.map(x=>strftime(Object.values(x)))];
var toCsv = async (b="", ext="csv") => await llist(b).then(x=>toList(x).map(x=>x.toString()).join("\n"));
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

var buffer = xlsx.build([{name: 'mySheetName', data: data}]);
var toxls = (data, name="list.xlsx") => fs.writeFile(name, 
			xlsx.build([{name: 'list', data: data}]), 
			(err) => console.log(...(err?[err,"fail!"]:["done!"])));

toxls().then().catch(err=>console.log(err)).finally()
// toCsv()
// 	.then(x=>console.log(x))
// 	.catch(err=>console.log(err))
// 	.finally();
