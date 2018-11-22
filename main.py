import node
import time
import threading
import queue
import tkinter
from tkinter import *


class GuiPart:
    def __init__(self, master, queue, endCommand):
        self.queue = queue
        # console = tkinter.Button(master, text='Stop', command=endCommand)
        # console.pack()

    def processIncoming(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        # while self.queue.qsize():
        #     try:
        #         msg = self.queue.get(0)
        #         print(msg)
        #     except Queue.Empty:
        #         pass


class NodeThread(threading.Thread):
    def __init__(self, thread_id, master):
        self.master = master
        self.queue = queue.Queue()
        self.gui = GuiPart(master, self.queue, self.endApplication)

        self.running = 1
        threading.Thread.__init__(self)
        self.node = node.Node(ip, target_ip, thread_id, num, is_bad, is_PBFT, master)

    def run(self):
        self.node.connect()
        time.sleep(2)
        # t = threading.Thread(target=self.print_loop)
        # t.setDaemon(True)
        # t.start()
        self.node.start()
        self.periodicCall()

    def periodicCall(self):
        self.gui.processIncoming()
        if not self.running:
            import sys
            sys.exit(1)
        self.master.after(100, self.periodicCall)

    def endApplication(self):
        self.running = 0

    def print_loop(self):
        while True:
            time.sleep(5)
            s = self.node.block_chain.get_block_chain()
            self.node.peer.connect_and_send('127.0.0.1', 22222, s)
            time.sleep(5)

root = tkinter.Tk()
root.resizable(width=False, height=False)
root.title('Dpos + PBFT BlockChain Demo')
root.geometry('1520x740')
scrollbary = Scrollbar(root)
scrollbarx = Scrollbar(root, orient=HORIZONTAL)

mylist = Listbox(root, width=180, height=40, yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)

mylist.grid(row=0, column=0, rowspan=100, columnspan=10)
scrollbary.grid(row=0, column=11, rowspan=100, columnspan=1, sticky=N+S+W)
scrollbarx.grid(row=101, column=0, rowspan=1, columnspan=11, sticky=W+E)

scrollbary.config(command=mylist.yview)
scrollbarx.config(command=mylist.xview)

# add input placeholders for bad nodes transaction info
Label(root, text="Vote 1").grid(row=24, column=13)
Label(root, text="Amount").grid(row=26, column=12)
Label(root, text="Candidate").grid(row=27, column=12)
Label(root, text="Community").grid(row=28, column=12)

e1_tra1 = Entry(root)
e2_tra1 = Entry(root)
e3_tra1 = Entry(root)

e1_tra1.grid(row=26, column=13)
e2_tra1.grid(row=27, column=13)
e3_tra1.grid(row=28, column=13)

Label(root, text="Vote 2").grid(row=45, column=13)
Label(root, text="Amount").grid(row=47, column=12)
Label(root, text="Candidate").grid(row=48, column=12)
Label(root, text="Community").grid(row=49, column=12)

e1_tra2 = Entry(root)
e2_tra2 = Entry(root)
e3_tra2 = Entry(root)

e1_tra2.grid(row=47, column=13)
e2_tra2.grid(row=48, column=13)
e3_tra2.grid(row=49, column=13)



is_bad = True
is_PBFT = True
ip = "10.12.253.2"
target_ip = "10.13.142.90"
num = 18
self_id = 0

thread = NodeThread(self_id, root)
thread.start()
root.mainloop()
