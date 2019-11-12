#!/usr/bin/env python
# encoding:utf-8
  
import os
from pyinotify import WatchManager, Notifier, ProcessEvent,IN_DELETE, IN_CREATE,IN_MODIFY,IN_MOVE_SELF
  
class EventHandler(ProcessEvent):
    """事件处理"""
    def process_IN_CREATE(self, event):
        print("Create file: %s " %  os.path.join(event.path,event.name))
 
    def process_IN_DELETE(self, event):
        print("Delete file: %s " %  os.path.join(event.path,event.name))

    def process_IN_MODIFY(self, event):
        print("Modify file: %s " %  os.path.join(event.path,event.name))

    def process_IN_MOVE_SELF(self, event):
        print("Move file: %s " %  os.path.join(event.path,event.name))

  
def FSMonitor(path='.'):
    wm = WatchManager()
    mask= IN_DELETE | IN_CREATE |IN_MODIFY |IN_MOVE_SELF
    notifier=Notifier(wm, EventHandler())
    wm.add_watch(path, mask,auto_add=True,rec=True)
    print('now starting monitor %s'%(path))
    while True:
        try:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
        except KeyboardInterrupt:
            print("keyboard")
            notifier.stop()
            break

if __name__ =="__main__":
    FSMonitor(".")
