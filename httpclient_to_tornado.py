import requests
from datetime import datetime
import copy

request_json_blank = {
    "workers_in": [],
    "workers_out": [],
    "other_departments": [],
    "waiting_order": 1,
    "comments": [],
    "stat": [],
    "total_stat": {},
    "abonent": {},
}

class HttpClientTornado:
    def __init__(self):
        self.URL='http://vodokanal.asofts.ru/api'
        #self.request=request_json_blank

    def QueueStatus(self, message, method:str, call:dict=None):
        waiting_order=0
        req = copy.deepcopy(request_json_blank)
        for msg in message:
            worker = {}
            worker['worker']=''
            if (msg.Event=='QueueMember'):
                worker['SIPLocation'] = msg.Location
                worker['status'] = msg.Status
                if call!=None:
                    if 'call_begin' in call:
                        worker['call_begin']=call['call_begin']
                    if 'call_end' in call:
                        worker['call_end'] = call['call_end']
                    if 'call_duration' in call:
                        worker['call_duration'] = call['call_duration']
                if (msg.Queue=='operator'):
                    req['workers_in'].append(worker)
                else:
                    req['other_departments'].append(worker)

            if msg.Event=='QueueEntry':
                waiting_order=waiting_order+1

        req['waiting_order']=waiting_order
        req['method']=method
        print(req)
        return req

    def SendRequest(self,message):
        result=requests.post(self.URL,json=message)
        print(result)