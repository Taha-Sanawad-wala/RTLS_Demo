from django.shortcuts import render
from django.http import HttpResponse
from rtlsapp.models import ConfigurationValue, MaterialPullLog,TagLog 
import json
import threading
# import websocket
import random
from django.utils import timezone
import time
from django.db.models import F, ExpressionWrapper, fields, Avg
from django.db.models.functions import TruncDate

# Create your views here.
def index(request,connection_msg=None):
    global status_material
    global background_task_active
    if background_task_active:
        data={'bgactive':True,'connectionmsg':connection_msg,'statusmaterial':status_material,}
        return render(request,'rtlsapp/index.html',data)
    else:
        data={'connectionmsg':connection_msg,'statusmaterial':status_material,}
        return render(request,'rtlsapp/index.html',data)


def materialRequestScreen(request):
    if request.method=='GET':
        plant,material,assembly,assembly_under_process,tags=getReqData()
        tagsInUse=MaterialPullLog.objects.filter(processed='X').values_list('tagId',flat=True)
        tagAvailable=list(set(tags)-set(tagsInUse))
        data={'plantdata':plant,
                'materialdata': material,
                'assemblydata':assembly[1:],
                'assemblyinprocess':assembly_under_process,
                'tagdata':tagAvailable
            }
        return render(request,'rtlsapp/materialrequestscreen.html',data)
    elif request.method=='POST':
        plant=request.POST.get('plant')
        material=request.POST.get('material')
        assembly=request.POST.get('assembly')
        tag=request.POST.get('tag')
        data=MaterialPullLog(plant=plant,materialNumber=material,requestZoneId=assembly,
        processed='X',tagId=tag
        )
        data.save()
        success='material'+':'+material +' is requested from'+' '+assembly
        plant,material,assembly,assembly_under_process,tags=getReqData()
        tagsInUse=MaterialPullLog.objects.filter(processed='X').values_list('tagId',flat=True)
        tagAvailable=list(set(tags)-set(tagsInUse))
        data={'plantdata':plant,
                'materialdata': material,
                'assemblydata':assembly[1:],
                'assemblyinprocess':assembly_under_process,
                'success': success,
                'tagdata':tagAvailable
            }
        return render(request,'rtlsapp/materialrequestscreen.html',data)


def deliveryStatusTracker(request):
    material_pull_log_data=MaterialPullLog.objects.all()
    # print(material_pull_log_data.values())
    data= {'data':material_pull_log_data.values()}
    return render(request,'rtlsapp/deliverystatustracker.html',data)


def kPI(request):
    delivery_time=MaterialPullLog.objects.raw(
        """
        SELECT
        autoId,
        transferOrderNumber,
        CASE
        WHEN deliveredTimeStamp IS NOT NULL  THEN
        CAST((JulianDay(deliveredTimeStamp) - JulianDay(requestTimeStamp)) * 24 * 60 * 60 AS Integer)
        ELSE
        0
        END AS diff
        FROM rtlsapp_materialpulllog order by requestTimeStamp Desc limit 7"""
        )
    dtlist=[]
    for i in delivery_time:
        dtlist.append({'autoId':i.autoId,'diff':i.diff,'transferOrderNumber':i.transferOrderNumber})

    # avgdeliverytime calculations
    result = MaterialPullLog.objects.annotate(
    time_difference=ExpressionWrapper(
    F('deliveredTimeStamp') - F('requestTimeStamp'),
    output_field=fields.DurationField()
    )
    ).annotate(
    truncated_date=TruncDate('requestTimeStamp')
    ).values('truncated_date').annotate(
    avg_time_difference=Avg(
    ExpressionWrapper(
    F('time_difference'),
    output_field=fields.DurationField()
    )
    )
    )
    adtlist=[]
    for entry in result:
        entry['avg_time_difference'] = entry['avg_time_difference'].total_seconds()
        entry['truncated_date']=str(entry['truncated_date'])
        adtlist.append({'avg_time_difference':entry['avg_time_difference'] ,'truncated_date':entry['truncated_date']})
    

    #Live tracking
    global background_task_active
    if background_task_active:
        tagId,zoneId,status = getSewioData()
        zones=list(ConfigurationValue.objects.filter(confgKey='RTLS_ZONE_ID').values_list('keyValue',flat=True))
        livedata={}
        for i in zones:
            if i==zoneId:
                livedata[i]=1
            else:
                livedata[i]=0
        livedata['zones']=zones
        print(livedata)
        data={'deliverytime':dtlist,
        'avgdeliverytime':adtlist,  
        'livedata':livedata                 
        }
        return render(request,'rtlsapp/kpi.html',data)
    else:
        data={'deliverytime':dtlist,
        'avgdeliverytime':adtlist,               
        }
        return render(request,'rtlsapp/kpi.html',data)

#sewio connect disconnect logic
background_task_active = False
status_material = None
def start_background_task():
    global background_task_active
    while background_task_active:
        time.sleep(10)
    # Your background task logic here
        tagId,zoneId,status=getSewioData()
        # print(tags,zoneids,tagId,zoneId,status)
        if status=='in':
            transferOrderNumber=list(MaterialPullLog.objects.filter(processed='X',tagId=tagId).values_list('transferOrderNumber',flat=True))
            materialNumber=list(MaterialPullLog.objects.filter(processed='X',tagId=tagId).values_list('materialNumber',flat=True))
            print(transferOrderNumber,materialNumber)
            if transferOrderNumber:
                insert_tag = TagLog(tagId=tagId,
                zoneId=zoneId,
                transferOrderNumber=transferOrderNumber[0],
                materialNumber=materialNumber[0],
                zoneEnteredTimeStamp=timezone.now(),
                zoneName=list(ConfigurationValue.objects.filter(confgObject=list(ConfigurationValue.objects.filter(keyValue=zoneId).values_list('confgObject',flat=True))[0],confgKey='ZONE_NAME').values_list('keyValue',flat=True))[0]
                )
                insert_tag.save()
                confgObject=list(ConfigurationValue.objects.filter(keyValue=zoneId,confgKey='RTLS_ZONE_ID').values_list('confgObject',flat=True))[0]
                print("confgObject",confgObject,"Tonumber",transferOrderNumber[0],"tagid",tagId)
                print(list(ConfigurationValue.objects.filter(confgObject=confgObject,confgKey='ZONE_NAME').values_list('keyValue',flat=True))[0],list(MaterialPullLog.objects.filter(processed='X',tagId=tagId).values_list('requestZoneId',flat=True)))
                #check if zone is requested zone or not
                if list(ConfigurationValue.objects.filter(confgObject=list(ConfigurationValue.objects.filter(keyValue=zoneId,confgKey='RTLS_ZONE_ID').values_list('confgObject',flat=True))[0],confgKey='ZONE_NAME').values_list('keyValue',flat=True))[0]==list(MaterialPullLog.objects.filter(processed='X',tagId=tagId).values_list('requestZoneId',flat=True))[0]:
                    # it should be in enroute fist
                    if not MaterialPullLog.objects.filter(processed='X',tagId=tagId,enrouteTimeStamp=None):
                        update_material_pull_log=MaterialPullLog.objects.filter(processed='X',tagId=tagId).update(processed='O',deliveredTimeStamp=timezone.now())
                        print("delivered")
                        global status_material
                        status_material = "material" + list(MaterialPullLog.objects.filter(processed='O',tagId=tagId).values_list('transferOrderNumber',flat=True))[0] + "Delivered!!!"
                else :
                    status_material = "tag:"+ str(tagId) +"is in zone!!!" + str(zoneId)
            else:
                pass
                # insert_tag = TagLog(tagId=tagId,
                # zoneId=zoneId,
                # zoneEnteredTimeStamp=timezone.now(),
                # zoneName=list(ConfigurationValue.objects.filter(confgObject=list(ConfigurationValue.objects.filter(keyValue=zoneId).values_list('confgObject',flat=True))[0],confgKey='ZONE_NAME').values_list('keyValue',flat=True))[0]
                # )
                # insert_tag.save()
        elif status == 'out':
            transferOrderNumber=list(MaterialPullLog.objects.filter(processed='X',tagId=tagId).values_list('transferOrderNumber',flat=True))
            if transferOrderNumber:
                tag_instance=TagLog.objects.filter(tagId=tagId,zoneExitTimeStamp=None).update(zoneExitTimeStamp=timezone.now())
                # check if it got out from warehouse
                confgObject=list(ConfigurationValue.objects.filter(keyValue=zoneId).values_list('confgObject',flat=True))[0]
                if "WAREHOUSE"==list(ConfigurationValue.objects.filter(confgObject=confgObject,confgKey='ZONE_TYPE').values_list('keyValue'))[0][0] :
                    update_material_pull_log=MaterialPullLog.objects.filter(processed='X',tagId=tagId).update(enrouteTimeStamp=timezone.now())
                    status_material = "material" + list(MaterialPullLog.objects.filter(processed='X',tagId=tagId).values_list('transferOrderNumber',flat=True))[0] + "is in enroute!!!"
                    print("enroute")
            else:
                tag_instance=TagLog.objects.filter(tagId=tagId,zoneExitTimeStamp=None).update(zoneExitTimeStamp=timezone.now())



def start_background(request):
    global background_task_active
    if not background_task_active:
        background_task_active = True
        background_thread = threading.Thread(target=start_background_task)
        background_thread.start()
        return index(request,'connection created to the server')
    else:
        background_task_active = True
        return index(request,'connection already exist')

def stop_background(request):
    global background_task_active
    if background_task_active:
        background_task_active = False
        return index(request,"connetion terminated")
    else:
        background_task_active = False
        return index(request,"connetion already terminated")


def getReqData(x=None):
    plant= ConfigurationValue.objects.filter(plant__isnull=False).values_list('plant',flat=True).distinct()
    material=ConfigurationValue.objects.filter(confgObject='materialNumber').values_list('keyValue',flat=True)
    assembly=ConfigurationValue.objects.filter(confgKey='ZONE_NAME').values_list('keyValue',flat=True)
    assembly_under_process= MaterialPullLog.objects.filter(processed='X').values_list('requestZoneId',flat=True)
    tags = ConfigurationValue.objects.filter(confgKey='SEWIO_TAG_ID').values_list('keyValue',flat=True)
    return list(plant),list(material),list(assembly),list(assembly_under_process),list(tags)



def getSewioData():
     # ws=websocket.create_connection("wss://demo.sewio.net")
        # ws.send('{"headers":{"X-ApiKey":"o7GqnNmAQIvkq8G6X9SNSs4BA"},"method":"subscribe", "resource":"/zones/"}')
        # dict1=json.loads(ws.recv()) 
        # print(dict1.get('body').get('feed_id'),dict1.get('body').get('zone_id'))
        #tags and zone configured in our system 
        tags = ConfigurationValue.objects.filter(confgKey='SEWIO_TAG_ID').values_list('keyValue',flat=True)
        zoneids = ConfigurationValue.objects.filter(confgKey='RTLS_ZONE_ID').values_list('keyValue',flat=True)
        tagId=random.choice(list(tags))
        zoneId=random.choice(list(zoneids))
        status=random.choice(['in','out'])
        return tagId,zoneId,status
# def datacopy(request):
#     print('in datacopy')
#     with open('\\Users\\taha.sanawad\\Desktop\\test.json', 'r') as json_file:
#         json_data = json.load(json_file)
#         for i in json_data:
#             c= ConfigurationValue(**i)
#             c.save()
#     return HttpResponse('hello world')
