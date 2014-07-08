'''
ttk_multicolumn_listbox2.py

Python31 includes the Tkinter Tile extension ttk.

Ttk comes with 17 widgets, 11 of which already exist in Tkinter:
Button, Checkbutton, Entry, Frame, Label, LabelFrame, Menubutton,
PanedWindow, Radiobutton, Scale and Scrollbar

The 6 new widget classes are:
Combobox, Notebook, Progressbar, Separator, Sizegrip and Treeview

For additional info see the Python31 manual:
http://gpolo.ath.cx:81/pydoc/library/ttk.html

Here the TreeView widget is configured as a multi-column listbox
with adjustable column width and column-header-click sorting.

Tested with Python 3.1.1 and Tkinter 8.5
'''

import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk

class McListBox():
    """use a ttk.TreeView as a multicolumn ListBox"""
    def __init__(self,master = None,table_header = None,table_list = None,height=200,width=150):
        self.table_header = table_header
        self.table_list = table_list
        self.tree = None
        self.height = height
        self.width = width
        self._setup_widgets(master = master)
        self._build_tree()

    def _setup_widgets(self,master = None):
        self.OuterFrame = ttk.Frame(master, height=self.height, width=self.width) 
        self.container = ttk.Frame(self.OuterFrame)
        self.container.pack_propagate(False)
        self.container.pack(fill='both',expand=False)
        # create a treeview with dual scrollbars
        self.tree = ttk.Treeview(self.container,displaycolumns = "#all",columns=self.table_header, show="headings")
        #self.tree.heading(1)
        self.vsb = ttk.Scrollbar(self.container,orient="vertical",
            command=self.tree.yview)
        self.hsb = ttk.Scrollbar(self.container,orient="horizontal",
            command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set,
            xscrollcommand=self.hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew')
        #self.tree.pack(fill='y')
        self.vsb.grid(column=1, row=0, sticky='ns')
        self.hsb.grid(column=0, row=1, sticky='ew')
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        self.OuterFrame.pack_propagate(False)
        self.OuterFrame.pack()
    def _build_tree(self):
        for col in self.table_header:
            self.tree.heading(col, text=col.title())#,
                #command=lambda c=col: self.sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.tree.column(col,
                             width=tkFont.Font().measure(col.title()))

        for item in self.table_list:
            self.tree.insert('', 'end', values=item)
            # adjust column's width if necessary to fit each value
            '''for ix, val in enumerate(item):
                col_w = tkFont.Font().measure(val)
                if self.tree.column(self.table_header[ix],width=None)<col_w:
                    self.tree.column(self.table_header[ix], width=col_w)'''

    def _rebuild_tree(self):
        self.tree.configure(columns=self.table_header,show="headings")
        self._build_tree()

    def _set_header(self,header = None):
        self.table_header = header

    def _set_list(self,list = None):
        self.table_list = list

    def updateTable(self,table_header=None,table_list=None):
        print(len(self.tree.get_children('')))
        elist = self.tree.get_children('')
        for x in elist:
            eylist = self.tree.get_children(x)
            for y in eylist:
                self.tree.delete(y)
        self._set_header(table_header)
        self._set_list(table_list)
        self._rebuild_tree()
        return True


    '''def sortby(self,tree, col, descending):
        """sort tree contents when a column header is clicked on"""
        # grab values to sort
        data = [(tree.set(child, col), child) \
            for child in tree.get_children('')]
        # if the data to be sorted is numeric change to float
        #data =  change_numeric(data)
        # now sort the data in place
        data.sort(reverse=descending)
        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)
        # switch the heading so it will sort in the opposite direction
        tree.heading(col, command=lambda col=col: self.sortby(tree, col, \
            int(not descending)))'''

if __name__ == "__main__" :
    # the test data ...
    car_header = ['car', 'repair']
    car_list = [
        ('Hyundai', 'brakes') ,
        ('Honda', 'light') ,
        ('Lexus', 'battery') ,
        ('Benz', 'wiper') ,
        ('Ford', 'tire') ,
        ('Chevy', 'air') ,
        ('Chrysler', 'piston') ,
        ('Toyota', 'brake pedal') ,
        ('BMW', 'seat')
    ]
    h = ['a','b','c']
    l=[
        ('f','6','7'),
        ('j','2','0'),
        ('k','4','9'),
        ('l','1','3')
    ]
    root = tk.Tk()
    root.wm_title("multicolumn ListBox")
    mc_listbox = McListBox(table_header=car_header,table_list=car_list,master = root)
    def update_table():
        #print(mc_listbox.tree.heading("#1"))
        for i in map(mc_listbox.tree.delete,mc_listbox.tree.get_children('')):
            pass
        #mc_listbox._set_header(header=h)
        #mc_listbox._set_list(list=list)
        mc_listbox._rebuild_tree()
        print(mc_listbox.tree.winfo_width())

    tk.Button(root,text="update",command=lambda :mc_listbox.updateTable(h,l)).pack()
    root.mainloop()
