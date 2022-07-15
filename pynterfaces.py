#!/usr/bin/python3
import collections
import time
from puresnmp import walk
from puresnmp import get
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

ip = "192.168.1.14"
community = "public"

OID_NAME = '1.3.6.1.2.1.31.1.1.1.1'
OID_HC_IN = '1.3.6.1.2.1.31.1.1.1.6'
OID_HC_OUT = '1.3.6.1.2.1.31.1.1.1.10'

interfaces = collections.defaultdict(dict)

def sizeof_fmt(num, suffix="bps"):
    for unit in ["", "k", "m", "g", "t", "p", "e", "z"]:
        if abs(num) < 1000.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1000.0
    return f"{num:.1f}Yi{suffix}"

def get_bw_usage(iterfaces):
    for oid,name in walk(ip, community, OID_NAME):
        inhc=get(ip,community,OID_HC_IN+'.'+str(oid[11]))
        intime=time.time()
        outhc=get(ip,community,OID_HC_OUT+'.'+str(oid[11]))
        outtime=time.time()
        if inhc != outhc != 0:
            curin=curout=bpsin=bpsout=0
            if int(oid[11]) in interfaces:
                curin=inhc-interfaces[int(oid[11])]['in']
                curout=outhc-interfaces[int(oid[11])]['out']
                bpsin=8*curin/(intime-interfaces[int(oid[11])]['intime'])
                bpsout=8*curout/(outtime-interfaces[int(oid[11])]['outtime'])
            interfaces[int(oid[11])]['name']=str(name.decode())
            interfaces[int(oid[11])]['in']=inhc
            interfaces[int(oid[11])]['out']=outhc
            interfaces[int(oid[11])]['intime']=intime
            interfaces[int(oid[11])]['outtime']=outtime
            interfaces[int(oid[11])]['bpsin']=bpsin
            interfaces[int(oid[11])]['bpsout']=bpsout
    return interfaces

ws  = Tk()
ws.title('pynterfaces')
ws.geometry('1400x791')
ws['bg'] = '#481036'
s = ttk.Style()
s.configure('Treeview', rowheight=40)
snmp_frame = Frame(ws)
snmp_frame.pack()
snmp_scroll = Scrollbar(snmp_frame)
snmp_scroll.pack(side=RIGHT, fill=Y)
snmp_scroll = Scrollbar(snmp_frame,orient='horizontal')
snmp_scroll.pack(side= BOTTOM,fill=X)
tree = ttk.Treeview(snmp_frame,yscrollcommand=snmp_scroll.set, xscrollcommand =snmp_scroll.set)
tree.pack()
snmp_scroll.config(command=tree.yview)
snmp_scroll.config(command=tree.xview)
tree['columns'] = ('if_name', 'if_in', 'if_out')
tree.column("#0", width=0,  stretch=NO)
tree.column("if_name",anchor=CENTER, width=320)
tree.column("if_in",anchor=CENTER,width=160)
tree.column("if_out",anchor=CENTER,width=160)
tree.heading("#0",text="",anchor=CENTER)
tree.heading("if_name",text="Interface Name",anchor=CENTER)
tree.heading("if_in",text="In",anchor=CENTER)
tree.heading("if_out",text="Out",anchor=CENTER)

def update_data():
    global interfaces
    global ip
    global community
    newip=hostid_entry.get()
    if newip != ip:
        ip=newip
        interfaces=collections.defaultdict(dict)
    community=communityg_entry.get()
    children=tree.get_children()
    for child in children:
        tree.delete(child)
    try:
        interfaces=get_bw_usage(interfaces)
    except:
        messagebox.showerror(title="Error", message='Error acessing snmp data.')
        return False
    for interface in interfaces:
        tree.insert(parent='',index='end',iid=interface,text='',values=(interfaces[interface]['name'],sizeof_fmt(interfaces[interface]['bpsin']),sizeof_fmt(interfaces[interface]['bpsout'])))
    tree.pack()

frame = Frame(ws)
frame.pack(pady=20)
hostid= Label(frame,text = "host")
hostid.grid(row=0,column=0 )
communityg = Label(frame,text="community")
communityg.grid(row=0,column=1)
hostid_entry= Entry(frame)
hostid_entry.grid(row= 1, column=0)
hostid_entry.insert(0,ip)
communityg_entry = Entry(frame)
communityg_entry.grid(row=1,column=1)
communityg_entry.insert(0,community)
refresh_button = Button(ws,text="Refresh",command=update_data)
refresh_button.pack(pady = 10)
ws.mainloop()
