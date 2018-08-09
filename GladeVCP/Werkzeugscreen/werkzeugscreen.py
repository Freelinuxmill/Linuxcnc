import glib
import gtk
import gobject
import linuxcnc
import hal

#Momentan muss noch Pocket 1-6 nacheinander in der Werkzeugtabelle stehen -> sonst Fehler
#Pfad anpassen von Werkzeugtabelle --> siehe untenS
class HandlerClass:
    
    def __init__(self, halcomp,builder,useropts):
        self.halcomp = halcomp
        self.builder = builder
	self.tool_table_read()
	self.combobox()
	self.status = linuxcnc.stat()
	self.command = linuxcnc.command()
	self.ok_for_mdi()

    def on_button_reload_pressed(self,widget,data=None):
	self.tool_table_read()
	self.combobox()	
    
    def on_button_offset_pressed(self,widget,data=None):
	pass

    def on_button_change_pressed(self,widget,data=None):
	if self.ok_for_mdi():
   		self.command.mode(linuxcnc.MODE_MDI)
   		self.command.wait_complete() # wait until mode switch executed
   		self.command.mdi("M6 "+str(self.toolchose))
		self.led_shine()

				
    def on_button_rename_pressed(self,widget,data=None):
	if self.ok_for_mdi():
   		self.command.mode(linuxcnc.MODE_MDI)
   		self.command.wait_complete() # wait until mode switch executed
   		self.command.mdi("M61 Q"+str(self.toolchose[1:]))
		self.led_shine()

    def on_hal_checkbutton1_toggled(self,widget,data=None):
	if widget.get_active():
		self.halcomp["hal_table1"] = True
        else:
		self.halcomp["hal_table1"] = False
		
    def led_shine(self):
	if self.pocketchose == 0:
		for i in range(1,7):
			self.halcomp["hal_led"+str(i)] = False		
	else:		
		for i in range(1,7):
			if int(self.pocketchose) == i:
				self.halcomp["hal_led"+str(self.pocketchose)] = True
			else:
				self.halcomp["hal_led"+str(i)] = False
	
    def combobox(self,data=None):
	self.cb1 = self.builder.get_object('combobox1')
	self.cb1.clear()
	self.furry_list = gtk.ListStore(int,str)
	#self.furry_list.clear()
	self.furry_list.append([0,"T0"])
        self.furry_list.append([1,"T"+str(self.tool[0])])
    	self.furry_list.append([2,"T"+str(self.tool[1])])
    	self.furry_list.append([3,"T"+str(self.tool[2])])
    	self.furry_list.append([4,"T"+str(self.tool[3])])
	self.furry_list.append([5,"T"+str(self.tool[4])])
	self.furry_list.append([6,"T"+str(self.tool[5])])
	self.cell = gtk.CellRendererText()
    	self.cb1.set_model(self.furry_list)
    	self.cb1.pack_start(self.cell, True)
    	self.cb1.add_attribute(self.cell, 'text', 1)
    	self.cb1.set_active(0)

    def on_combobox1_changed(self,widget,data=None):
	tree_iter = self.cb1.get_active_iter()
        model = self.cb1.get_model()
        self.toolchose = model[tree_iter][1]
	self.pocketchose = model[tree_iter][0]
	
    def ok_for_mdi(self):
    	self.status.poll()
    	return not self.status.estop and self.status.enabled and self.status.homed and (self.status.interp_state == linuxcnc.INTERP_IDLE)

    def tool_table_read(self,data=None):
	self.tool = []
	self.string = []
	#Diesen Pfad an jeweilige Maschine Individuell anpassen!
	with open("/home/xpertmill/linuxcnc/configs/Simulator/sim_mm.tbl", "r") as datei:
		#For schleife durchsucht jede Zeile nach Pockets und speichert toolnumber und toolcomment in self.tool und self.string
		pocket = 1
		for line in datei:
		        if line.find("P"+str(pocket)) != -1 and pocket <=6 :                                          
		            self.tool.append(line[1:line.find(" ")+1])                      
		            self.string.append(line[line.find(";")+1: len(line)-1])      
			    self.builder.get_object("labelT"+str(pocket)).set_label("T %d" %int(self.tool[pocket-1]))
			    self.builder.get_object("labelC"+str(pocket)).set_label(self.string[pocket-1])
			    pocket = pocket+1
		datei.close()

def get_handlers(halcomp,builder,useropts):
    return [HandlerClass(halcomp,builder,useropts)]
