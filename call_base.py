import os
import sys
from datetime import datetime
from datetime import timedelta
import time

BASE_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, DATETIME, TIME
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
from sqlalchemy import and_

#engine=create_engine('sqlite:///:memory:',echo=True)
engine = create_engine('sqlite:///'+BASE_DIR+'/call_database.db',echo=True)


Base=declarative_base()
class CallBase(Base):
    __tablename__='callbase'

    Id=Column(Integer, primary_key=True)
    CustomerNumber=Column(String)
    EmployeeNumber=Column(String)
    CallBegin=Column(DATETIME)
    CallEnd=Column(DATETIME)
    CallDuration=Column(Integer)

    def __repr__(self):
        return "<CallBase(EmployeeNumber='%s', CustomerNumber='%s', CallBegin='%s', CallEnd='%s', CallDuration='%s')>" % \
               (self.EmployeeNumber, self.CustomerNumber, self.CallBegin.__str__(), self.CallEnd.__str__(), self.CallDuration.__str__())

#Base.metadata.create_all(engine)

# print(CallBase.__table__)
# call_table=CallBase(CallerNumber='79619813085',StartCall=datetime.datetime.now(),EndCall=datetime.datetime.now())
# print(call_table.CallerNumber)
# print(call_table.StartCall)
# print(call_table.EndCall)
#
#
# Session = sessionmaker(bind=engine)
# session = Session()
# session.add(call_table)
# print(session.new)
# session.commit()
# print(call_table.Id)

class CallBaseManager:
    def __init__(self):
        self.engine=create_engine('sqlite:///'+BASE_DIR+'/call_database.db',echo=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.currentID=0
        self.CustomerNumber=''
        self.EmployeeNumber=''
        self.SIPpeers=list()
        self.listcall=dict()

    # def Save(self, CallerNumber: str):
    #     if self.EmployeeNumber=='':
    #         self.callTable= CallBase(EmployeeNumber=CallerNumber, CallBegin=datetime.now())
    #         self.session.add(self.callTable)
    #         self.session.commit()
    #         self.currentID=self.callTable.Id
    #         print(self.currentID)
    #         self.EmployeeNumber=self.callTable.EmployeeNumber
    #         print(self.EmployeeNumber)

    def FillSIPpeers(self, message:list):
        print(message)
        for msg in message:
            if (msg.ObjectName!=None) and (msg.ObjectName!=''):
                self.SIPpeers.append(msg.ObjectName)
        print(self.SIPpeers)

    def CallBegin(self,CallerNumber: str, ConnectedNumber:str):
        #BridgeEnter
        if self.IsSIPPeer(CallerNumber):
            self.callTable= CallBase(EmployeeNumber=CallerNumber, CustomerNumber=ConnectedNumber, CallBegin=datetime.now())
            self.session.add(self.callTable)
            self.session.commit()
            self.currentID=self.callTable.Id
            print(self.currentID)
            self.EmployeeNumber=self.callTable.EmployeeNumber
            print(self.EmployeeNumber)
            self.CustomerNumber=self.callTable.CustomerNumber
            print(self.CustomerNumber)
            self.listcall[self.EmployeeNumber]=self.currentID
            call = dict()
            call['call_begin'] = datetime.now().__str__()
            print(call)
            return call
        return False

    def CallEnd(self, CallerNumber: str):
        #Hangup
        EmployeeNumber=''
        for key in self.listcall.keys():
            if key==CallerNumber:
                EmployeeNumber=CallerNumber
                break
        if EmployeeNumber != '':
            callquery = self.session.query(CallBase).filter_by(EmployeeNumber=EmployeeNumber).first()
            if callquery != None:
                callquery.CallEnd=datetime.now()
                delta=callquery.CallEnd-callquery.CallBegin
                callquery.CallDuration=delta.seconds
                call=dict()
                call['call_begin']=str(callquery.CallBegin)
                call['call_end']=str(callquery.CallEnd)
                call['call_duration']=datetime.fromtimestamp(delta.seconds).strftime("%H:%M:%S")
                print(call)
                print(self.session.dirty)
                self.session.commit()
                return call
        return False

    def IsSIPPeer(self, CallerNumber: str):
        i=0
        while i<len(self.SIPpeers):
            if (self.SIPpeers[i]==CallerNumber) or ('+'+self.SIPpeers[i]==CallerNumber):
                return True
            i+=1
        return False

    def OperatorInfo(self, worker:str):
        EmployeeNumber = ''
        for key in self.listcall.keys():
            if key==worker:
                EmployeeNumber=worker
                break
        if EmployeeNumber != '':
            callquery = self.session.query(CallBase).filter_by(EmployeeNumber=EmployeeNumber).all()
            call=dict()
            callscount=callquery.count()
            call['calls_count']=callscount
            maxduration=0
            for duration in callquery:
                sumduration=sumduration+duration.CallDuration
                if maxduration<duration.CallDuration:
                    maxduration=duration.CallDuration
            avduration=sumduration//callscount
            call['av_duration']=avduration
            call['max_duration']=maxduration
            return call
        return None
