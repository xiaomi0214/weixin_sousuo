#coding=utf-8
from django.shortcuts import render
from django.http import HttpResponse,StreamingHttpResponse,FileResponse
import os
import sys
import json
import requests
sys.path.append('..')

from hello.models import taskTable,spiderkeyTable
import codecs
from  .tasks import spider_key
from .other import mail_Verification_link,pushworkLimit,pageNum,allPageNum
import datetime



def getOpenid(request):
    if request.method=="POST":
        requestData=json.loads(request.body)
        code=requestData.get('code',None)
        if code!=None:
            url="https://api.weixin.qq.com/sns/jscode2session?appid=wx6edbdc08d0d7e84e&secret=c6a617ae9c051ab5c32d4ab8760659eb&js_code=%s&grant_type=authorization_code"%(code)
            response=requests.get(url=url)
            responseData=json.loads(response.text)
            print (responseData,type(responseData))
            openid=responseData.get('openid')
            session_key=responseData.get('session_key')
        return HttpResponse(openid)


def search(request):
    if request.method == "POST":
        request_body=json.loads(request.body)
        print (request_body)
        starturl =request_body.get("url")
        domain = request_body.get("site")
        keyword = request_body.get('keywords')
        uid=request_body.get('openid')
        print (request.body,type(request.body),request_body,starturl,domain,keyword,uid)

        status=True
        msg=""

        limitResult,msg=pushworkLimit(starturl,domain,keyword)
        if limitResult:
            taskObj = taskTable(
                uid=uid,
                url=starturl,
                domain=domain,
                keyword=keyword,
                taskCreateDate=datetime.datetime.now(),
                subscribeStatus=0,
                status=0,
            )
            taskObj.save()
            spider_key.delay(starturl,domain,keyword,str(taskObj.id))
        else:
            status=False
        return HttpResponse(json.dumps({"status":status,"msg":msg}))


def setSubscribe(request):
    if request.method=="POST":
        request_body = json.loads(request.body)
        taskid=request_body.get('taskid')

        taskObj=taskTable.objects.get(id=taskid)
        taskObj.subscribeStatus=1
        taskObj.save()

        return HttpResponse(json.dumps({"status":True}))

def getHistoryList(request):
    if request.method=="POST":
        request_body=json.loads(request.body)
        uid=request_body.get('openid')
        pageIndex=int(request_body.get("pageIndex"))
        # pageNum=10
        # subscribe = request_body.get('subscribe')

        startIndex=(pageIndex-1)*pageNum
        endIndex=pageIndex*pageNum

        taskList=taskTable.objects.filter(uid=uid)[startIndex:endIndex]
        allpagenum=allPageNum(len(taskTable.objects.filter(uid=uid)),int(pageNum))

        status=True
        data=[]

        if taskList:
            for taskObj in taskList:
                taskdate = datetime.datetime.strftime(taskObj.taskCreateDate, "%Y-%m-%d %H:%M:%S")
                onedata = {
                    "taskid": taskObj.id,
                    "startUrl": taskObj.url,
                    "domain": taskObj.domain,
                    "keyword": taskObj.keyword,
                    "subscribeStatus": taskObj.subscribeStatus,
                }
                data.append(onedata)
        else:
            status=False

        return HttpResponse(json.dumps({"status":status,"data":data,"allpagenum":allpagenum}))


def getSubscribeList(request):
    if request.method=="POST":
        request_body=json.loads(request.body)
        uid=request_body.get('openid')
        # subscribe = request_body.get('subscribe')
        pageIndex = int(request_body.get("pageIndex"))
        startIndex = (pageIndex - 1) * pageNum
        endIndex = pageIndex * pageNum


        taskList=taskTable.objects.filter(uid=uid,subscribeStatus=1)[startIndex:endIndex]
        status=True
        data=[]

        if taskList:
            for taskObj in taskList:
                taskdate = datetime.datetime.strftime(taskObj.taskCreateDate, "%Y-%m-%d %H:%M:%S")
                onedata = {
                    "taskid": taskObj.id,
                    "startUrl": taskObj.url,
                    "domain": taskObj.domain,
                    "keyword": taskObj.keyword,
                    "taskCreateDate": taskdate,
                }
                data.append(onedata)
        else:
            status=False

        return HttpResponse(json.dumps({"status":status,"data":data}))


def showResult(request):
    if request.method=="POST":
        request_body=json.loads(request.body)
        taskid=request_body.get('taskid')
        pageIndex = int(request_body.get("pageIndex"))
        print (taskid,pageIndex)
        startIndex = (pageIndex - 1) * pageNum
        endIndex = pageIndex * pageNum

        taskObj=taskTable.objects.get(id=taskid)
        ##默认返回10条数据 按照num大小排序
        # getNum=5

        spiderResult=spiderkeyTable.objects.filter(task_id=taskid)
        print(len(spiderResult),spiderResult)
        # if spiderResult.count()<getNum:
        #     getNum=spiderResult.count()
        print(startIndex,endIndex)
        spiderResult=spiderResult.order_by("-keyWordNum")[startIndex:endIndex]
        print (spiderResult)
        status=True
        data={}
        urls=[]
        if spiderResult:
            keyWord=taskObj.keyword
            domain=taskObj.domain

            for  onespider in spiderResult:
                url=onespider.url
                num=onespider.keyWordNum
                modifiedDate = datetime.datetime.strptime(onespider.modifiedTime,"%a, %d %b %Y %H:%M:%S %Z")
                modifiedDateStr=datetime.datetime.strftime(modifiedDate, "%Y-%m-%d %H:%M:%S")
                urls.append({"url":url,"num":num,"modifiedDate":modifiedDateStr})

            data={
                "keyWord":keyWord,
                "domain":domain,
                "urls":urls,
            }
        else:
            status=False

        return HttpResponse(json.dumps({"status":status,"data":data}))
