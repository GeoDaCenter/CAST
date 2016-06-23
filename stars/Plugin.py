import wx

from yapsy.IPlugin import IPlugin

class IWindowPlugin(IPlugin):
    def __init__(self):
        IPlugin.__init__(self)
        self.menu_id = wx.NewId()
        self.button_id = wx.NewId()
        
    def get_icon(self):
        pass
    
    def get_icon_size(self):
        return (16,16)
    
    def __get_button_id(self):
        return self.button_id
    
    def __get_menu_id(self):
        return self.menu_id

    def get_label(self):
        pass

    def get_shortHelp(self):
        return ''

    def get_longHelp(self):
        return ''

    def get_toolbar_pos(self):
        return -1

    def get_parent_menu(self):
        pass

    def add_toolbar_item(self, toolbar):
        label = self.get_label()
        button_id = self.__get_button_id()
        if button_id == None:
            return None, None
        
        button_bmp = self.get_icon()
        button_size = self.get_icon_size()
        pos = self.get_toolbar_pos()
        shortHelp = self.get_shortHelp()
        longHelp = self.get_longHelp()

        if pos>0:
            toolbar.InsertLabelTool(pos,button_id,label,button_bmp,shortHelp=shortHelp,longHelp=longHelp)
        else:
            toolbar.AddLabelTool(button_id,label,button_bmp,shortHelp=shortHelp,longHelp=longHelp)

        toolbar.Realize()
        return button_id, self.show

    def add_menu_item(self, menu_dict):
        menu_id = self.__get_menu_id()
        if menu_id == None:
            return None, None
        
        label = self.get_label()
        shortHelp = self.get_shortHelp()

        parent_menu_name = self.get_parent_menu()
        menu = menu_dict[parent_menu_name]
        menu.Append(menu_id, label, shortHelp)

        return menu_id, self.show

    def show(self, event):
        pass


class IMapPlugin(IWindowPlugin):
    def __init__(self):
        IWindowPlugin.__init__(self)

    def show(self, event):
        pass


class IPlotPlugin(IWindowPlugin):
    def __init__(self):
        IWindowPlugin.__init__(self)
        
    def show(self, event):
        pass

class ITablePlugin(IWindowPlugin):
    def __init__(self):
        IWindowPlugin.__init__(self)
        
    def show(self, event):
        pass