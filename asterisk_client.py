import asyncio
from panoramisk import Manager
from call_base import CallBaseManager
from pprint import pprint
from httpclient_to_tornado import HttpClientTornado


# def main(loop):
#     #loop = asyncio.get_event_loop()
#
#     manager = Manager(loop=loop,
#                       host='178.248.87.116',
#                       port=1709,
#                       username='admin',
#                       secret='100')
#
#     # @manager.register_event('*')
#     # def callback(manager, message):
#     #     if "FullyBooted" not in message.event:
#     #         """This will print every event, but the FullyBooted events as these
#     #         will continuously spam your screen"""
#     #
#     #         print(message)
#     #         print(message.AccountID)
#     #         print(message.CallerIDNum)
#     #         print(message.EventTV)
#
#     callManager = CallBaseManager()
#     httpclient = HttpClientTornado()
#
#     def FullyBooted(manager, message):
#         print(message)
#         resp = yield from manager.send_action({'Action': 'SIPpeers'})
#         callManager.FillSIPpeers(resp)
#         resp = yield from manager.send_action({'Action': 'QueueStatus'})
#         pprint(resp)
#         result = httpclient.QueueStatus(resp, method='connect')
#         httpclient.SendRequest(result)
#
#     manager.register_event('FullyBooted', FullyBooted)
#
#     def BridgeEnter(manager, message):
#         # global isDial
#         # isDial=False
#         print(message)
#         Bridge = callManager.CallBegin(CallerNumber=message.CallerIDNum, ConnectedNumber=message.ConnectedLineNum)
#         if isinstance(Bridge, dict):
#             resp = yield from manager.send_action({'Action': 'QueueStatus'})
#             pprint(resp)
#             result = httpclient.QueueStatus(resp, method='call_begin', call=Bridge)
#             httpclient.SendRequest(result)
#
#     manager.register_event('BridgeEnter', BridgeEnter)
#
#     def Hangup(manager, message):
#         print(message)
#         Call = callManager.CallEnd(CallerNumber=message.CallerIDNum)
#         if isinstance(Call, dict):
#             resp = yield from manager.send_action({'Action': 'QueueStatus'})
#             pprint(resp)
#             result = httpclient.QueueStatus(resp, method='call_end', call=Call)
#             httpclient.SendRequest(result)
#
#     manager.register_event('Hangup', Hangup)
#
#     manager.connect()
#     try:
#         manager.loop.run_forever()
#     except KeyboardInterrupt:
#         manager.loop.close()




class AsteriskClient:
    def __init__(self,loop):
        self.manager = Manager(loop=loop,
                          host='178.248.87.116',
                          port=1709,
                          username='admin',
                          secret='100')
        self.callManager = CallBaseManager()
        self.httpclient = HttpClientTornado()

        self.manager.register_event('FullyBooted', self.FullyBooted)
        self.manager.register_event('BridgeEnter', self.BridgeEnter)
        self.manager.register_event('Hangup', self.Hangup)

        self.manager.connect()
        try:
            self.manager.loop.run_forever()
        except KeyboardInterrupt:
            self.manager.loop.close()

    def FullyBooted(self, manager, message):
        print(message)
        resp = yield from manager.send_action({'Action': 'SIPpeers'})
        self.callManager.FillSIPpeers(resp)
        resp = yield from manager.send_action({'Action': 'QueueStatus'})
        pprint(resp)
        result = self.httpclient.QueueStatus(resp, method='connect')
        self.httpclient.SendRequest(result)

    def BridgeEnter(self, manager, message):
        # global isDial
        # isDial=False
        print(message)
        Bridge = self.callManager.CallBegin(CallerNumber=message.CallerIDNum, ConnectedNumber=message.ConnectedLineNum)
        if isinstance(Bridge, dict):
            resp = yield from manager.send_action({'Action': 'QueueStatus'})
            pprint(resp)
            result = self.httpclient.QueueStatus(resp, method='call_begin', call=Bridge)
            self.httpclient.SendRequest(result)

    def Hangup(self, manager, message):
        print(message)
        Call = self.callManager.CallEnd(CallerNumber=message.CallerIDNum)
        if isinstance(Call, dict):
            resp = yield from manager.send_action({'Action': 'QueueStatus'})
            pprint(resp)
            result = self.httpclient.QueueStatus(resp, method='call_end', call=Call)
            self.httpclient.SendRequest(result)

    def ChanSpy(self,channel_from:str, channel_to:str, type:str):
        call=yield from self.manager.send_action({
            'Action': 'Originate',
            'Channel': 'SIP/'+channel_from,
            'Application': 'ChanSpy',
            'Data': 'SIP/'+channel_to+','+type,
            'Priority': 1,
            'Callerid': 'Spy-{%s} <{%s}>'.format(channel_to),
            'Variable': 'SIPADDHEADER="Call-Info:\;answer-after=0"',
        })
        pprint(call)

    def PickUp(self, channel:str):
        call = yield from self.manager.send_action({
            'Action': 'Originate',
            'Channel': 'SIP/'+channel,
            'Application': 'PickupChan',
            'Data': 'SIP/' + channel,
            'Priority': 1,
            'Callerid': channel,
            'Variable': 'SIPADDHEADER="Call-Info:\;answer-after=0"',
        })
        pprint(call)

    def Originate(self, channel_from, channel_to):
        call = yield from self.manager.send_action({
            'Action': 'Originate',
            'Channel': 'SIP/' + channel_from,
            'Exten': channel_to,
            'Priority': 1,
            'Callerid': channel_from,
            'Variable': 'SIPADDHEADER="Call-Info:\;answer-after=0"',
        })
        pprint(call)

    def Redirect(self,channel_from, channel_to):
        call = yield from self.manager.send_action({
            'Action': 'Redirect',
            # 'Channel': 'SIP/' + channel_from,
            # 'Exten': channel_to,
            'Priority': 1,
            'Context':'from-internal',
        })
        pprint(call)

    def QueueAdd(self,channel):
        call = yield from self.manager.send_action({
            'Action': 'QueueAdd',
            'Queue': 'operator',
            'Interface': 'SIP/'+channel,
            'Penalty': 0,
        })
        pprint(call)

    def QueueRemove(self,channel):
        call = yield from self.manager.send_action({
            'Action': 'QueueRemove',
            'Queue': 'operator',
            'Interface': 'SIP/'+channel,
        })
        pprint(call)

    def Queue(self,worker:str,action:int):
        if action==1:
            self.QueueAdd(worker)
        else:
            self.QueueRemove(worker)


    def Parse(self, message:dict):
        method = message['method']
        if method == 'call_abonent':
            self.Originate(message['from'], message['to'])
        elif method == 'transfer_call':
            self.Redirect(message['from'], message['to'])
        elif method == 'connect_with_abonent':
            self.ChanSpy(message['from'], message['to'], 'qBx')
        elif method == 'connect_without_abonent':
            self.ChanSpy(message['from'], message['to'], 'wx')
        elif method == 'connect_without_microphone':
            self.ChanSpy(message['from'], message['to'], 'qx')
        elif method == 'queue':
            self.Queue(message['worker'],message['action'])


# if __name__ == '__main__':
#     main()