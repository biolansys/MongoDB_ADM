"""
 MongoDB Admin Python/tkinter
 José Lanzos Gómez
 Version : 0.9.1
"""
import tkinter as tk
from ttkthemes import ThemedTk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename , askdirectory
import tkinter.font as tkfont
from datetime import date
import pymongo
from pymongo import errors
from bson  import json_util
from bson.json_util import dumps
from bson.json_util import loads
from bson.objectid import ObjectId
from bson.son import SON
import json
import pprint
import os
import webbrowser
import subprocess
from subprocess import call
from subprocess import PIPE, Popen

S_CONNECT = ['mongodb://localhost:27017/','mongodb://192.168.1.164:27017/',
             'mongodb+srv://<user>:<pass>@cluster0.uctoj.mongodb.net/?retryWrites=true&w=majority',
             'mongodb+srv://<user>:<pass>@cluster0.3ezre.mongodb.net/?retryWrites=true&w=majority']
M_CONNECT = ['localhost','DELL','MongoDB Atlas','MongoDB Atlas B']

PATH_FIREFOX      ='C://Program Files//Mozilla Firefox//firefox.exe'
PATH_MONGODB_TOOLS="C:\\Program Files\MongoDB\\Tools\\100\\bin\\"
PATH_MONGODB_BIN  ="C:\\Program Files\MongoDB\\Server\\4.4\\bin\\"
PATH_MONGODB_SH   ="C:\\Program Files\MongoDB\\mongosh\\"
#PATH_MONGODB_SH   ="C:\\Varios\\MongoDB\\"
PATH_BACKUP       ="C:\\Varios\\MongoDB\\Dump"
PATH_EXPORT       ="C:\\Varios\\MongoDB\\Export\\"

def center_window(w=1180, h=640):
    # get screen width and height
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    # calculate position x, y
    x = (ws/2) - (w/2)    
    y = (hs/2) - (h/2) - 40
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    
class CrearToolTip(object):
	def __init__(self,elemento,texto='Info del objeto'):
		self.espera = 500
		self.largo = 180
		self.objeto = elemento
		self.texto = texto
		self.objeto.bind("<Enter>",self.entrar)
		self.objeto.bind("<Leave>",self.salir)
		self.objeto.bind("<ButtonPress>",self.salir)
		self.id = None
		self.tw = None
	def entrar(self,event=None):
		self.asignar()
	def salir(self,event=None):
		self.liberar()
		self.ocultar_tip()
	def  asignar(self):
		self.liberar()
		self.id = self.objeto.after(self.espera,self.mostrar_tip)
	def  liberar(self):
		id = self.id
		self.id = None
		if id:
			self.objeto.after_cancel(id)
	def  mostrar_tip(self,event=None ):
		x = y = 0
		x,y,cx,cy = self.objeto.bbox("insert")
		x += self.objeto.winfo_rootx() + 25
		y += self.objeto.winfo_rooty() + 20
		self.tw = tk.Toplevel(self.objeto)
		self.tw.wm_overrideredirect(True)
		self.tw.wm_geometry("+%d+%d"%(x,y))
		label = tk.Label(self.tw,text=self.texto,justify="left",
					             background = "white",relief="solid",borderwidth=1,
								 wraplength = self.largo)
		label.pack(ipadx=1)
	def ocultar_tip(self):
		tw = self.tw
		self.tw = None
		if tw:
			tw.destroy()

def restore_instance():
    folder_selected = askdirectory(title="Select instance dump",mustexist=tk.TRUE)
    if not folder_selected:
        return
    dbname=os.path.basename(folder_selected)
    res = messagebox.askquestion('Confirmation', 'Do you want to Restore this instance ?')
    if res == 'yes':
       st_data.insert(tk.INSERT,"Instance Restore Start : " + dbname)
       p = subprocess.Popen('"'+PATH_MONGODB_TOOLS+'mongorestore" --uri=' + CONN_STR + '  ' + folder_selected + '  --gzip',
                  stdout=subprocess.PIPE,stderr=subprocess.PIPE)
       aaa, bbb = p.communicate()
       output = "\n" + aaa.decode('utf-8')+  "\n" +  bbb.decode('utf-8') + "\n" + "Instance Restore End"
       st_data.insert(tk.INSERT,output)
       
def restore_db():
    folder_selected = askdirectory(title="Select database dump",mustexist=tk.TRUE)
    if not folder_selected:
        return
    dbname=os.path.basename(folder_selected)
    res = messagebox.askquestion('Confirmation', 'Do you want to Restore this database : ' + dbname  + "  ?")
    if res == 'yes':
       st_data.insert(tk.INSERT,"Database Restore Start : " + dbname)
       p = subprocess.Popen('"'+PATH_MONGODB_TOOLS+'mongorestore" --uri=' + CONN_STR + ' --db ' + dbname + '  '+folder_selected + '  --gzip',
                  stdout=subprocess.PIPE,stderr=subprocess.PIPE)
       aaa, bbb = p.communicate()
       output = "\n" + aaa.decode('utf-8')+  "\n" +  bbb.decode('utf-8') + "\n" + "Database Restore End"
       st_data.insert(tk.INSERT,output)
    
def restore_coll():
    folder_selected = askdirectory(title="Select collection dump",mustexist=tk.TRUE)
    if not folder_selected:
        return
    dbname=os.path.basename(folder_selected)
    res = messagebox.askquestion('Confirmation', 'Do you want to Restore this collection : ' + dbname  + "  ?")
    if res == 'yes':  
       st_data.insert(tk.INSERT,"Database Restore Start : " + dbname)
       p = subprocess.Popen('"'+PATH_MONGODB_TOOLS+'mongorestore" --uri=' + CONN_STR + ' --db ' + dbname + '  '+folder_selected,
                  stdout=subprocess.PIPE,stderr=subprocess.PIPE)
       aaa, bbb = p.communicate()
       output = "\n" + aaa.decode('utf-8')+  "\n" +  bbb.decode('utf-8') + "\n" + "Database Restore End"
       st_data.insert(tk.INSERT,output)
    
def open_file():
    filepath = askopenfilename(filetypes=[("MQL Files", "*.mql"), ("All Files", "*.*")])
    if not filepath:
        return
    f = open(filepath, 'r')
    f2 = f.read()
    st_query.delete('1.0', 'end')
    st_query.insert('1.0', f2)
    f.close()  
    texto = tk.StringVar()
    texto.set('MQL file : ' + filepath)
    MQL_file_label.config(textvariable=texto)

def save_file():
    filepath = asksaveasfilename(
        defaultextension="mcl",
        initialfile = MQL_file_label.cget("text"),
        filetypes=[("MQL Files", "*.mql"), ("All Files", "*.*")],
    )
    if not filepath:
        return
    f = open(filepath, 'w')
    f.write(st_query.get(1.0, tk.END))
    f.close 
    
def save_file_as():
    filepath = asksaveasfilename(
        defaultextension="mcl",
        filetypes=[("MQL Files", "*.mql"), ("All Files", "*.*")],
    )
    if not filepath:
        return
    f = open(filepath, 'w')
    f.write(st_query.get(1.0, tk.END))
    f.close 
    texto = tk.StringVar()
    texto.set(filepath)
    MQL_file_label.config(textvariable=texto)

def read_json():
    filepath = askopenfilename(
        filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
    )
    if not filepath:
        return
    f = open(filepath, 'r')
    f2 = f.read()
    st_query_result.delete('1.0', 'end')
    st_query_result.insert('1.0', f2)
    f.close()  
    print(filepath)

def save_json():
    filepath = asksaveasfilename(
        defaultextension="json",
        filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
    )
    if not filepath:
        return
    f = open(filepath, 'w')
    f.write(st_query_result.get(1.0, tk.END))
    f.close 
    print(filepath) 
    
def copy_JSON_clipboard():
    root.clipboard_clear()
    root.clipboard_append(st_query_result.get(1.0, tk.END ))
    root.update()
    
def copy_MQL_clipboard():
    root.clipboard_clear()
    root.clipboard_append(st_query.get(1.0, tk.END ))
    root.update()
 
def Connect():   
   global myclient
   global mydb
   global mycol
   global server_info   
   try:    
      myclient = pymongo.MongoClient(CONN_STR,tlsAllowInvalidCertificates=True)
      server_info = myclient.server_info()
      st_connection.delete('1.0', tk.END) 
      st_connection.insert(tk.INSERT,"Connection String: " + M_CONN_STR+"\n")
      st_connection.insert(tk.INSERT,"MongoDB Version  : " + server_info["version"]+ "  " +  str(server_info["bits"])+"bits\n")
      st_connection.insert(tk.INSERT,"Debug            : " + str(server_info["debug"])+"\n")
      st_connection.insert(tk.INSERT,"OS distribution  : " + server_info["buildEnvironment"]["distmod"]+"\n")
      st_connection.insert(tk.INSERT,"CPU distribution : " + server_info["buildEnvironment"]["distarch"]+"\n")
      st_connection.insert(tk.INSERT,"OS version       : " + server_info["buildEnvironment"]["target_os"]+"\n")
      st_connection.insert(tk.INSERT,"CPU version      : " + server_info["buildEnvironment"]["target_arch"]+"\n")
      json_str = dumps(server_info, indent = 4)
      st_connection.insert(tk.INSERT,"Storage Engines  :"+"\n")
      for (engines ) in server_info["storageEngines"]:
           st_connection.insert(tk.INSERT," "+engines+" "  )
      i=0
      dbs_tv.delete(*dbs_tv.get_children())
      for dbs in pymongo.MongoClient(CONN_STR,tlsAllowInvalidCertificates=True).list_database_names():
          dbs_tv.insert(parent='', index=i, iid=i, values=(dbs))
          i=i+1 
      
      col_tv.delete(*col_tv.get_children())
      return True
   except  pymongo.errors.PyMongoError as e:
      messagebox.showwarning(title="Error", message="MongoDb server not reachable .." + str(e))
      return False
     
def Sel_Conn():
   global image2    #VERY IMPORTANT
   def Exit_Conn():
       if (Connect()) :
          filewin.destroy()  
          root.deiconify()
       else:
          Exit()   
       
   def CONN_combo_select(event):
       global CONN_STR ,M_CONN_STR    
       M_CONN_STR = CONN_combo.get()
       CONN_STR = S_CONNECT[CONN_combo.current()]
       root.title('MongoDb Demo : ' + M_CONN_STR) 
       
   filewin = tk.Toplevel(root)
   filewin.title("Servers")
   filewin.resizable(tk.FALSE,tk.FALSE)
   ws = filewin.winfo_screenwidth()
   hs = filewin.winfo_screenheight()
   w=210 ; h=240;
   x = (ws/2) - (w/2)    
   y = (hs/2) - (h/2) - 40
   filewin.geometry('%dx%d+%d+%d' % (w, h, x, y))
   
   image2=tk.PhotoImage(file="mongodb.gif")
   image2=image2.subsample(1,1)
   label=tk.Label(filewin, image=image2)  
   label.grid(row=0, column=0, padx=15, pady=10)
   
   CONN_combo = ttk.Combobox(filewin, state="readonly" ,width=25)
   CONN_combo.bind("<<ComboboxSelected>>", CONN_combo_select)
   CrearToolTip(CONN_combo," Servers ")
   CONN_combo.set(' Select Server')
   CONN_combo['values'] = M_CONNECT
   CONN_combo.grid(row=1, column=0, padx=15, pady=5)
   
   user_label = tk.Label(filewin,text="User  ") 
   user_label.grid(row=2, column=0, padx=15, pady=5,sticky=tk.W)
   user_entry = ttk.Entry(filewin,width=22)
   CrearToolTip(user_entry," User   ")
   user_entry.grid(row=2, column=0, padx=15, pady=5,sticky=tk.E)
   pass_label = tk.Label(filewin,text="Pass") 
   pass_label.grid(row=3, column=0, padx=15, pady=5,sticky=tk.W)
   pass_entry = ttk.Entry(filewin,show="*",width=22)
   CrearToolTip(user_entry," User   ")
   pass_entry.grid(row=3, column=0, padx=15, pady=5,sticky=tk.E)
   c10_button = tk.Button(filewin, width=7 , height=1 ,text=' Connect ', command=Exit_Conn)
   c10_button.grid(row=4, column=0, padx=15, pady=15,sticky=tk.N+tk.S)
   root.withdraw()

def About():
     tk.messagebox.showinfo(title="About ...", message="MongoDB demo" ) 

def Close():
    res = messagebox.askquestion('Exit', 'Do you want to exit?')
    if res == 'yes':
       ws.destroy()

def selectItem_dbs(a):
    global mydb,dbname
    curItem = dbs_tv.focus()
    dbname=dbs_tv.item(curItem)["values"][0]  
    mydb = myclient[dbname]
    col_tv.delete(*col_tv.get_children())
    st_data.delete('1.0', tk.END)
    i=0
    for coll in mydb.list_collection_names():
        col_tv.insert(parent='', index=i, iid=i, values=(coll))
        i=i+1

def selectItem_col(a):
    global mycol,colname
    curItem1 = col_tv.focus()
    colname = (col_tv.item(curItem1)["values"][0] ) 
    mycol = mydb[colname]
    texto = tk.StringVar() ; texto.set('db.col : ' + dbname+'.'+colname) ; db_col_label.config(textvariable=texto)
    st_data.delete('1.0', tk.END)
    myIndex=mycol.index_information()
    """
    st_data.insert(tk.INSERT, "Indexes:\n")
    for doc in mycol.list_indexes():
       json_str = dumps(doc, indent = 4)
       st_data.insert(tk.INSERT,json_str +" \n")
    st_data.insert(tk.INSERT, "\nFirst 10 Documents:\n")
    for doc in mycol.find({},{"_id":0},limit=100):
       json_str = dumps(doc, indent = 4)
       st_data.insert(tk.INSERT,json_str +" \n")
    """
    
def Exe_Query():     
    myqueryS = 'mycol.'+st_query.get(1.0, tk.END)
    myqueryS = myqueryS.replace(" ", "")
    myqueryS = myqueryS.replace("\n", "")
    print (myqueryS)
    mydoc = eval( myqueryS  ) 
    try:
      st_query_result.delete('1.0', tk.END)
      st_query_result.insert(tk.INSERT,"[\n")
      i=0
      for doc in mydoc:
         json_str = dumps(doc, indent = 4)
         st_query_result.insert(tk.INSERT,json_str+",\n")
         i=i+1
      st_query_result.insert(tk.INSERT,"]\n")   
      NR_entry.delete(0,tk.END) ; NR_entry.insert(0,str(i)) 
    except  pymongo.errors.PyMongoError as e:
      messagebox.showwarning(title="Error", message="MongoDb not reachable .." + str(e))  
      


def Exe01_Command(N): 
    st_query_result.delete('1.0', tk.END)
    try:
      if   (N=='0'):
         st_data.delete('1.0', tk.END)
         mycommandS = Commands_frame_st.get(1.0, tk.END)
         mydoc = mydb.command(mycommandS[:-1])
         print (mycommandS[:-1])
         json_str = dumps(mydoc) ;  record2  = loads(json_str)
         st_data.insert(tk.INSERT,json.dumps(record2, indent=4, sort_keys=True,default=json_util.default)) 
      elif (N=='1'):
         st_data.delete('1.0', tk.END)
         mydoc =(mydb.command("collstats",colname))  
         json_str = dumps(mydoc)
         record2 = loads(json_str)
         st_data.insert(tk.INSERT,json.dumps(record2, indent=4, sort_keys=True,default=json_util.default))
      elif (N=='2'):
         st_data.delete('1.0', tk.END)
         mydoc = myclient.list_database_names()
         print (mydoc)
         mydoc = dict((db, [collection for collection in myclient[db].list_collection_names()]) for db in myclient.list_database_names())
         st_data.insert(tk.INSERT,json.dumps(mydoc, indent=4, sort_keys=True))
      elif (N=='3'):
         st_data.delete('1.0', tk.END)
         mydoc =mydb.command("dbstats" )  
         st_data.insert(tk.INSERT,json.dumps(mydoc, indent=4, sort_keys=True))
         st_data.insert(tk.INSERT, "\n\nIndexes:\n")
         cols = mydb.list_collection_names();
         for colname0 in mydb.list_collection_names():
            json_str = dumps(colname0, indent = 4)
            st_data.insert(tk.INSERT,'\nCollection: '+json_str +' \n')
            mycol0 = mydb[colname0]
            for doc0 in mycol0.list_indexes():
              json_str0 = dumps(doc0, indent = 4)
              st_data.insert(tk.INSERT,json_str0 +" \n")
      elif (N=='4'):
         st_data.delete('1.0', tk.END)
         res = messagebox.askquestion('Confirmation', 'Do you want to Backup this database : ' + dbname   + "  ?")
         if res == 'yes':  
           st_data.insert(tk.INSERT,"Database Backup Start : " + dbname)
           p = subprocess.Popen('"'+PATH_MONGODB_TOOLS+'mongodump" --uri=' + CONN_STR + ' --db ' + dbname + ' --out='+PATH_BACKUP+ ' --gzip',
                  stdout=subprocess.PIPE,stderr=subprocess.PIPE)
           aaa, bbb = p.communicate()
           output = "\n" + aaa.decode('utf-8')+  "\n" +  bbb.decode('utf-8') + "\n" + "Database Backup End"
           st_data.insert(tk.INSERT,output)
      elif (N=='5'):
         mydoc = mycol.find_one({},{"_id":0})  
         json_str = dumps(mydoc, indent = 2)
         st_query_result.insert(tk.INSERT,json_str)
      elif (N=='6'):
         res = messagebox.askquestion('Confirmation', 'Do you want to Backup this Instance?')
         if res == 'yes': 
            st_data.delete('1.0', tk.END)
            p = subprocess.Popen('"'+PATH_MONGODB_TOOLS+'mongodump"  --uri=' + CONN_STR + ' --out='+PATH_BACKUP+' --gzip',
                  stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            aaa, bbb = p.communicate()
            output = "Instance Backup Start : \n" + aaa.decode('utf-8')+  "\n" +  bbb.decode('utf-8') + "\n" + "Instance Backup End"
            st_data.insert(tk.INSERT,output)   
      elif (N=='7'):
         res = messagebox.askquestion('Confirmation', 'Do you want to Export this colection : ' + dbname +"." + colname + "  ?")
         if res == 'yes':       
            st_data.delete('1.0', tk.END)
            st_data.insert(tk.INSERT,"Collection Export Start : " +  dbname + " " + colname )
            p = subprocess.Popen('"'+PATH_MONGODB_TOOLS+'mongoexport"  --uri=' + CONN_STR + ' --db ' +  dbname + ' --collection ' +  colname + ' --out='+PATH_EXPORT+ colname+'.json ',
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            aaa, bbb = p.communicate()
            output = "\n" + aaa.decode('utf-8')+  "\n" +  bbb.decode('utf-8') + " \nCollection Export End"
            st_data.insert(tk.INSERT,output) 
      elif (N=='8'):
         c ='start  cmd /c "'+PATH_MONGODB_BIN+'mongo.exe"  ' + CONN_STR ;    #print (c)
         p = os.system(c)
      elif (N=='9'):
         c ='start  cmd /c "'+PATH_MONGODB_SH+'mongosh.exe"  ' + CONN_STR  ;  #print (c)
         p = os.system(c)   
      elif (N=='10'):
         res = messagebox.askquestion('Confirmation', 'Do you want to Backup this colection : ' + dbname +"." + colname + "  ?")
         if res == 'yes':  
            st_data.delete('1.0', tk.END)
            st_data.insert(tk.INSERT,"Collection Backup Start : " +  dbname + " " + colname )
            p = subprocess.Popen('"'+PATH_MONGODB_TOOLS+'mongodump"  --uri=' + CONN_STR + ' --db ' +  dbname + ' --collection ' +  colname + ' --out='+PATH_BACKUP+ Col_combo.get()+' --gzip',
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            aaa, bbb = p.communicate()
            output = "\n" + aaa.decode('utf-8')+  "\n" +  bbb.decode('utf-8') + " \nCollection Backup End"
            st_data.insert(tk.INSERT,output) 
      elif (N=='11'):
         c ='start  cmd /c "'+PATH_MONGODB_TOOLS+'mongostat.exe"  ' + CONN_STR  ;  #print (c)
         p = os.system(c)    
      elif (N=='12'):
         c ='start  cmd /c "'+PATH_MONGODB_TOOLS+'mongotop.exe"  ' + CONN_STR  ;  #print (c)
         p = os.system(c) 
      elif (N=='13'):
         res = messagebox.askquestion('Confirmation', 'Do you want to Import this colection : ' + dbname +"." + colname + "  ?")
         if res == 'yes':       
            st_data.delete('1.0', tk.END)
            st_data.insert(tk.INSERT,"Collection Import Start : " +  dbname + " " + colname )
            p = subprocess.Popen('"'+PATH_MONGODB_TOOLS+'mongoimport"  --uri=' + CONN_STR + ' --db ' +  dbname + ' --collection ' +  colname + ' --file='+PATH_EXPORT+ colname+'.json ',
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            aaa, bbb = p.communicate()
            output = "\n" + aaa.decode('utf-8')+  "\n" +  bbb.decode('utf-8') + " \nCollection Import End"
            st_data.insert(tk.INSERT,output)  
      elif (N=='14'):
           st_data.delete('1.0', tk.END)
           mydoc = mydb.command('usersInfo') ; json_str = dumps(mydoc) ;  record2  = loads(json_str)
           st_data.insert(tk.INSERT,json.dumps(record2, indent=4, sort_keys=True,default=json_util.default))      
      elif (N=='15'):
           if ( ( 'mydb' in globals() ) and (dbname=='admin') ):
             st_data.delete('1.0', tk.END)
             try:
                js='{"getLog":"global"}'
                jj=loads(js)
                mydoc =  mydb.command(jj);
             except  pymongo.errors.PyMongoError as e:
                messagebox.showwarning(title="Error", message="MongoDb not reachable .." + str(e))  
             json_str = dumps(mydoc) ;  record2  = loads(json_str)
             st_data.insert(tk.INSERT,json.dumps(record2, indent=4, sort_keys=True,default=json_util.default))  
           else:   
             messagebox.showwarning(title="Error", message="Select admin dbs ..."  )                
    except  pymongo.errors.PyMongoError as e:
      messagebox.showwarning(title="Error", message="MongoDB not reachable .." + str(e))     
      
def Exe02_Command(N):     
    if   (N=='0'):   
      call("notepad c:\\varios\\python\\hints.txt")
    
      
def Docs(N): 
    if   (N=="0"):
      url = 'https://docs.mongodb.com/'
    elif (N=="1"):
      url = 'https://docs.mongodb.com/tools/'  
    elif (N=="2"):
      url = 'https://docs.mongodb.com/database-tools/' 
    elif (N=="3"):
      url = 'https://www.site24x7.com/tools/sql-to-mongodb.html' 
    elif (N=="4"):
      url = 'https://jsonformatter.org/'
    webbrowser.register('firefox',None,webbrowser.BackgroundBrowser(PATH_FIREFOX))
    webbrowser.get('firefox').open(url)

def pm_st_query_result_show(event):
   try:
      pm_st_query_result.tk_popup(event.x_root, event.y_root, 0)
   finally:
      pm_st_query_result.grab_release() 
      
def pm_st_query_show(event):
   try:
      pm_st_query.tk_popup(event.x_root, event.y_root, 0)
   finally:
      pm_st_query.grab_release() 

# root window
#root = tk.Tk()
root = ThemedTk(theme='scidblue')
root.title('MongoDB Demo')
root.resizable(tk.FALSE,tk.FALSE)
center_window(1180, 640)
#print(root.get_themes()) 
style = ttk.Style(root)
 
# create a notebook
s = ttk.Style()
s.configure('TNotebook.Tab', font=('Times','9' ) )
notebook = ttk.Notebook(root)
notebook.pack(pady=10, expand=True)
# create frames
frame2 = ttk.Frame(notebook, width=1160, height=630)
frame3 = ttk.Frame(notebook, width=1160, height=630)
frame4 = ttk.Frame(notebook, width=1160, height=630)
frame2.pack(fill='both', expand=True)
frame3.pack(fill='both', expand=True)
frame4.pack(fill='both', expand=True)
# add frames to notebook
notebook.add(frame3, text='  Server Info ')
notebook.add(frame2, text='  MQL Queries ')
notebook.add(frame4, text='  MongoDB Tools  ')
# End notebook section

""" -------  """
# First tab
#Server Info Frame
tab3_frame = tk.Frame(frame3, bd=1, relief=tk.SOLID, padx=5, pady=5 ) 
tab3_frame.place(x=5, y=5)
st_connection = scrolledtext.ScrolledText(tab3_frame, font=('Lucida Console', 9), width = 50, height = 10,background = '#243642',foreground = "white")
st_connection.grid(row=1, column=1, pady=2, padx=5   )
#End Server Info Frame

#DBS Frame inside tab3_frame
dbs_frame = tk.Frame(frame3, bd=0, relief=tk.SOLID, padx=5, pady=5)
dbs_frame.place(x=5, y=165)
dbs_tv = ttk.Treeview(dbs_frame, columns=(1), show='headings', height=19 )
dbs_tv.bind('<ButtonRelease-1>', selectItem_dbs)
 
header_font0 = tkfont.Font(family='TimesNewRoman', size=9,weight="bold") 
s1 = ttk.Style()
s1.configure("Treeview.Heading", font=header_font0, rowheight=int(12*2.5)) 
 
dbs_tv.pack(side=tk.LEFT)
dbs_tv.heading(1, text="Databases") ; dbs_tv.column(1, minwidth=0, width=110, stretch=tk.NO)
dbs_sb = tk.Scrollbar(dbs_frame, orient=tk.VERTICAL)
dbs_sb.pack(side=tk.RIGHT, fill=tk.Y)
dbs_tv.config(yscrollcommand=dbs_sb.set)
dbs_sb.config(command=dbs_tv.yview)
#End DBS Frame 

# Collection Frame inside tab3_frame
col_frame = tk.Frame(frame3, bd=0, relief=tk.SOLID, padx=2, pady=5)
col_frame.place(x=155, y=165)
col_tv = ttk.Treeview(col_frame, columns=(1), show='headings', height=19 )
col_tv.bind('<ButtonRelease-1>', selectItem_col)
col_tv.pack(side=tk.LEFT)
col_tv.heading(1, text="Collections")     ; col_tv.column(1, minwidth=0, width=120, stretch=tk.NO)
col_sb = tk.Scrollbar(col_frame, orient=tk.VERTICAL)
col_sb.pack(side=tk.RIGHT, fill=tk.Y)
col_tv.config(yscrollcommand=col_sb.set)
col_sb.config(command=col_tv.yview)
# End Collection Frame 

# MongoDB Tools frame
com_col_frame = tk.Frame(frame3, bd=1, relief=tk.SOLID, padx=5, pady=5)
com_col_frame.place(x=550, y=5)

com_col01_btn = tk.Button(com_col_frame, width=10, height=1 ,text='backup', font=('Lucida', 9,'bold'), command=lambda: Exe01_Command("6"))
CrearToolTip(com_col01_btn," Backup Instance ")
com_col01_btn.grid(row=1, column=1, pady=3, padx=5 )
#
com_col02_btn = tk.Button(com_col_frame, width=10, height=1 ,text='backup dbs', font=('Lucida', 9,'bold'), command=lambda: Exe01_Command("4"))
CrearToolTip(com_col02_btn," Backup DBS ")
com_col02_btn.grid(row=2, column=1, pady=3, padx=5 )
#
com_col03_btn = tk.Button(com_col_frame, width=10, height=1 ,text='backup col', font=('Lucida', 9,'bold'), command=lambda: Exe01_Command("10"))
CrearToolTip(com_col03_btn," Backup Collection ")
com_col03_btn.grid(row=3, column=1, pady=3, padx=5 )
#
com_col04_btn = tk.Button(com_col_frame, width=10, height=1 ,text='export col', font=('Lucida', 9,'bold'), command=lambda: Exe01_Command("7"))
CrearToolTip(com_col04_btn," Export Collection ")
com_col04_btn.grid(row=4, column=1, pady=3, padx=5 )
#
com_col05_btn = tk.Button(com_col_frame, width=10, height=1 ,text='restore', font=('Lucida', 9,'bold'), command=restore_instance)
CrearToolTip(com_col05_btn," Restore Instance ")
com_col05_btn.grid(row=1, column=2, pady=3, padx=5 )
#
com_col06_btn = tk.Button(com_col_frame, width=10, height=1 ,text='restore dbs', font=('Lucida', 9,'bold'), command=restore_db)
CrearToolTip(com_col06_btn," Restore DBS ")
com_col06_btn.grid(row=2, column=2, pady=3, padx=5 )
#
com_col07_btn = tk.Button(com_col_frame, width=10, height=1 ,text='restore col', font=('Lucida', 9,'bold'), command=restore_coll)
CrearToolTip(com_col07_btn," Restore Collection ")
com_col07_btn.grid(row=3, column=2, pady=3, padx=5 )
#
com_col08_btn = tk.Button(com_col_frame, width=10, height=1 ,text='import col', font=('Lucida', 9,'bold'), command=lambda: Exe01_Command("7"))
CrearToolTip(com_col08_btn," Restore Collection ")
com_col08_btn.grid(row=4, column=2, pady=3, padx=5 )
# End MongoDB Tools frame

# DB/Colls  frame
DB_col_frame = tk.Frame(frame3, bd=1, relief=tk.SOLID, padx=5, pady=5)
DB_col_frame.place(x=410, y=5)

DB_col_frame_btn00 = tk.Button(DB_col_frame, width=13, height=1 ,text='show dbs/colls', font=('Lucida', 9,'bold'),  command=lambda: Exe01_Command("2"))
CrearToolTip(DB_col_frame_btn00," show databases/collections ")
DB_col_frame_btn00.grid(row=0, column=0, pady=3, padx=5 )

DB_col_frame_btn01 = tk.Button(DB_col_frame, width=13, height=1 ,text='show db stats', font=('Lucida', 9,'bold'),  command=lambda: Exe01_Command("3"))
CrearToolTip(DB_col_frame_btn01," show databases/collections ")
DB_col_frame_btn01.grid(row=1, column=0, pady=3, padx=5 )

DB_col_frame_btn02 = tk.Button(DB_col_frame, width=13, height=1 ,text='show coll  stats', font=('Lucida', 9,'bold'),  command=lambda: Exe01_Command("1"))
CrearToolTip(DB_col_frame_btn02," show databases/collections ")
DB_col_frame_btn02.grid(row=2, column=0, pady=3, padx=5 )
# End DB/Colls frame

# Commands  frame
Commands_frame = tk.Frame(frame3, bd=1, relief=tk.SOLID, padx=5, pady=5)
Commands_frame.place(x=755, y=5)
Commands_frame_st = scrolledtext.ScrolledText(Commands_frame, font=('Lucida Console', 10), width = 40, height = 6,
                    background = '#243642',foreground = "white",insertbackground="red",cursor="plus")
Commands_frame_st.insert(tk.INSERT,'dbstats')
#Commands_frame_st.place(x=5, y=5) 
Commands_frame_st.grid(row=0, column=0, pady=3, padx=5 )
Commands_frame_btn00 = tk.Button(Commands_frame, width=5, height=1 ,text='Exec ', font=('Lucida', 9,'bold'), command=lambda: Exe01_Command("0"))
CrearToolTip(Commands_frame_btn00," execute command ")
Commands_frame_btn00.grid(row=1, column=0, pady=3, padx=5 )
# End Commnads frame

#Data Frame inside tab3_frame
data_frame = tk.Frame(frame3, bd=0, relief=tk.SOLID, padx=5, pady=5)
data_frame.place(x=305, y=165)
st_data = scrolledtext.ScrolledText(data_frame, font=('Lucida Console', 10), width =102, height = 31,background = '#3D4F58',foreground = "white")
st_data.grid(row=1, column=1, pady=0, padx=0 )
#End Data Frame 

# End First tab

""" ----------  """

# Second tab
tab2_frame = tk.Frame(frame2, bd=0, relief=tk.SOLID, padx=5, pady=5 ) 
tab2_frame.place(x=5, y=5,height=580, width=1150)
st_query = scrolledtext.ScrolledText(tab2_frame, font=('Lucida console', 10), width = 58, height = 36,
           background = "#243642",foreground = "white",insertbackground="red",cursor="plus")
"""
st_query.insert(tk.INSERT, 'find(\n'+
  '{  "address.country": { "$in": [ "Spain", "Brazil"] }}\n'+
  ',\n'+
  '{"address.country":1,"address.market":1 }\n'+
  ')')
"""
st_query.place(x=5, y=5)

MQL_file_label = tk.Label(tab2_frame,text="MQL file : ..." ,font=('Lucida', 9,'bold')) ; MQL_file_label.place(x=5, y=488)

db_col_label   = tk.Label(tab2_frame,text='db.col : ...'   ,font=('Lucida', 9,'bold')) ; db_col_label.place(x=5, y=510)

open_MQL_btn = tk.Button(tab2_frame, width=7, height=1 ,text='Open', font=('Lucida', 9,'bold'), command=open_file)
CrearToolTip(open_MQL_btn," Open MQL file ")
open_MQL_btn.place(x=5, y=540)

save_MQL_btn = tk.Button(tab2_frame, width=7, height=1 ,text='Save', font=('Lucida', 9,'bold'), command=save_file)
CrearToolTip(save_MQL_btn," Save MQL file ")
save_MQL_btn.place(x=75, y=540)

save_as_MQL_btn = tk.Button(tab2_frame, width=7, height=1 ,text='Save as', font=('Lucida', 9,'bold'), command=save_file_as)
CrearToolTip(save_as_MQL_btn," Save MQL file as ...")
save_as_MQL_btn.place(x=145, y=540)

find_one_btn = tk.Button(tab2_frame, width=7, height=1 ,text='find one', font=('Lucida', 9,'bold'), command=lambda: Exe01_Command("5"))
CrearToolTip(find_one_btn," find one ")
find_one_btn.place(x=340, y=540)

find_one_btn = tk.Button(tab2_frame, width=7, height=1 ,text='find one', font=('Lucida', 9,'bold'), command=lambda: Exe01_Command("5"))
CrearToolTip(find_one_btn," find one ")
find_one_btn.place(x=340, y=540)

query_btn = tk.Button(tab2_frame, width=5, height=1 ,text='Query', font=('Lucida', 9,'bold'), command=Exe_Query)
CrearToolTip(query_btn," Execute query ")
query_btn.place(x=405, y=540)

NR_entry = ttk.Entry(tab2_frame,width=6)
CrearToolTip(NR_entry," Number of documents retrieved ")
NR_entry.place(x=460, y=540)
 
st_query_result = scrolledtext.ScrolledText(tab2_frame, font=('Lucida Console', 10), width = 75, height = 43,
                  background = '#243642',foreground = "white",insertbackground="red",cursor="plus")
st_query_result.place(x=525, y=5) 

pm_st_query_result = tk.Menu(root, tearoff=0)
pm_st_query_result.add_command(label="Save JSON",command=save_json)
pm_st_query_result.add_command(label="Read JSON",command=read_json)
pm_st_query_result.add_separator()
pm_st_query_result.add_command(label="Copy to Clipboard",command=copy_JSON_clipboard)
st_query_result.bind("<Button-3>", pm_st_query_result_show)

pm_st_query = tk.Menu(root, tearoff=0)
pm_st_query.add_command(label="Open MQL",command=open_file)
pm_st_query.add_command(label="Save MQL",command=save_file)
pm_st_query.add_command(label="Save MQL as",command=save_file_as)
pm_st_query.add_separator()
pm_st_query.add_command(label="Copy to Clipboard",command=copy_MQL_clipboard)
st_query.bind("<Button-3>", pm_st_query_show)

# End Second tab

#Menu bar

menubar = tk.Menu(root)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Open MQL",        command=open_file)
filemenu.add_command(label="Save MQL",        command=save_file)
filemenu.add_command(label="Save MQL as ...", command=save_file_as)
filemenu.add_separator()
filemenu.add_command(label="Servers", command=Sel_Conn)
filemenu.add_separator()
filemenu.add_command(label="Exit",        command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)

adminmenu0 = tk.Menu(menubar, tearoff=0)
adminmenu0.add_command(label="Show dbs/cols",      command=lambda: Exe01_Command("2"))
adminmenu0.add_command(label="Show db stats",      command=lambda: Exe01_Command("3"))
adminmenu0.add_command(label="Show col stats",     command=lambda: Exe01_Command("1"))
adminmenu0.add_command(label="Show users",         command=lambda: Exe01_Command("14"))
adminmenu0.add_separator()
adminmenu0.add_command(label="Show logs",          command=lambda: Exe01_Command("15"))
menubar.add_cascade(label="DBInfo", menu=adminmenu0)

adminmenu1= tk.Menu(menubar, tearoff=0)
adminmenu1.add_command(label="Backup Instance",    command=lambda: Exe01_Command("6"))
adminmenu1.add_command(label="Backup dbs",         command=lambda: Exe01_Command("4"))
adminmenu1.add_command(label="Backup collection",  command=lambda: Exe01_Command("10"))
adminmenu1.add_separator()
adminmenu1.add_command(label="Restore Instance",   command=restore_instance)
adminmenu1.add_command(label="Restore dbs",        command=restore_db)
adminmenu1.add_command(label="Restore collection", command=restore_coll)
adminmenu1.add_separator()
adminmenu1.add_command(label="Export collection",  command=lambda: Exe01_Command("7"))
adminmenu1.add_command(label="Import collection",  command=lambda: Exe01_Command("13"))
menubar.add_cascade(label="DBBackup", menu=adminmenu1)

adminmenu2 = tk.Menu(menubar, tearoff=0)
adminmenu2.add_command(label="Create User",       command=lambda: Exe01_Command("2"))
adminmenu2.add_command(label="Create Database",   command=lambda: Exe01_Command("3"))
adminmenu2.add_command(label="Create Collection", command=lambda: Exe01_Command("1"))
adminmenu2.add_command(label="Create Index",      command=lambda: Exe01_Command("6"))
adminmenu2.add_separator()
menubar.add_cascade(label="DBAdmin", menu=adminmenu2)

utimenu = tk.Menu(menubar, tearoff=0)
utimenu.add_command(label="mongo",     command=lambda: Exe01_Command("8"))
utimenu.add_command(label="mongosh",   command=lambda: Exe01_Command("9"))
utimenu.add_separator()
utimenu.add_command(label="mongostat", command=lambda: Exe01_Command("11"))
utimenu.add_command(label="mongotop",  command=lambda: Exe01_Command("12"))
menubar.add_cascade(label="MongoDB Tools", menu=utimenu)

docmenu = tk.Menu(menubar, tearoff=0)
docmenu.add_command(label="MongoDB Docs",     command=lambda: Docs("0"))
docmenu.add_command(label="MongoDB Tools",    command=lambda: Docs("1"))
docmenu.add_command(label="MongoDB DB Tools", command=lambda: Docs("2"))
docmenu.add_separator()
docmenu.add_command(label="SQL to NoSQL",     command=lambda: Docs("3"))
docmenu.add_command(label="JSON Formatter",   command=lambda: Docs("4"))
menubar.add_cascade(label="Resources", menu=docmenu)

helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="Hints"     , command=lambda: Exe02_Command("0"))
helpmenu.add_command(label="About..."  , command=About)
menubar.add_cascade(label="Help"       , menu=helpmenu)

root.config(menu=menubar)

Sel_Conn()
  
root.mainloop()
