import xbmc
import xbmcgui
import xbmcaddon

class AddTorrentMenu(xbmcgui.WindowXML):

    def __new__(cls):
        script_path = xbmcaddon.Addon().getAddonInfo('path')
        return xbmcgui.WindowXML.__new__(cls, 'add-torrent-menu.xml', script_path)

    def __init__(self):
        script_path = xbmcaddon.Addon().getAddonInfo('path')
        xbmcgui.WindowXML.__init__(self, 'add-torrent-menu.xml', script_path, defaultSkin='default', defaultRes='1080p', isMedia=False)

    def onInit(self):
        xbmc.executebuiltin('Container.SetViewMode(50)')
        self.setFocusId(self.getCurrentContainerId())
        # define a temporary list where we are going to add all the listitems to
        listitems = []
        # this will be the first item in the list. 'my first item' will be the label that is shown in the list
        listitem1 = xbmcgui.ListItem('my first item')
        # add this item to our temporary list
        listitems.append(listitem1)
        # let's create another item
        listitem2 = xbmcgui.ListItem('my second item')
        # and add it to the temporary list as well
        listitems.append(listitem2)
        # by default the built-in container already contains one item, the 'up' (..) item, let's remove that one
        self.clearList()
        # now we are going to add all the items we have defined to the (built-in) container
        self.addItems(listitems)
        # give kodi a bit of (processing) time to add all items to the container
        xbmc.sleep(100)
        print("Hello World")
