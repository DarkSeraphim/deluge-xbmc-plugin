import __future__

from future import standard_library
standard_library.install_aliases()

import urllib, urllib.parse, sys, os
import xbmcaddon, xbmcplugin, xbmcgui, xbmc

# Plugin constants
__addonname__ = "DelugeXBMCPlugin"
__addonid__   = "plugin.program.deluge"
__addon__     = xbmcaddon.Addon(id=__addonid__)
__language__  = __addon__.getLocalizedString
__cwd__       = xbmc.translatePath( __addon__.getAddonInfo('path') )#.decode('utf-8')
__profile__   = xbmc.translatePath( __addon__.getAddonInfo('profile') )#.decode('utf-8')
__icondir__   = os.path.join( __cwd__, 'resources', 'icons' )

# Shared resources
BASE_RESOURCE_PATH = os.path.join( __cwd__, 'resources', 'lib' )
sys.path.append (BASE_RESOURCE_PATH)

def log_info(message):
    xbmc.log(message, xbmc.LOGINFO)

from utilities import *
from DelugeWebUI import DelugeWebUI
from Filter import Filter
from States import States

UT_SECURE = __addon__.getSetting('secure')
UT_ADDRESS = __addon__.getSetting('ip')
UT_PORT = __addon__.getSetting('port')
UT_PATH = __addon__.getSetting('path')
UT_PASSWORD = __addon__.getSetting('pwd')

addon_handle = sys.argv[0]

def create_url(action, params={}):
    params.update({'action': action})
    return addon_handle + '?' + urllib.parse.urlencode(params)

protocol = 'https'
if (UT_SECURE != True and UT_SECURE != 'true'):
  protocol = 'http'

path = UT_PATH
if not path.endswith('/'):
    path += '/'
path += 'json'

url = protocol + '://' + UT_ADDRESS + ':' + UT_PORT + path
baseurl = url
log_info('Connecting to ' + url)

webUI = DelugeWebUI(url)

def isTorrentListable(torrent, stateName):
    if torrent.state == stateName:
        return True
    if stateName == States.All:
        return True
    if stateName == States.Finished and torrent.progress == 100:
        return True
    if stateName == States.Unfinished and torrent.progress > 0 and torrent.progress < 100:
        return True
    if stateName == States.Unstarted and torrent.progress == 0:
        return True
    if stateName == States.Active and (torrent.state == States.Downloading or torrent.state == States.Seeding):
        return True
    return False

def listTorrents(torrentList, stateName):
    restoreSession()
    mode = 1
    for torrentInfo in torrentList:
        if isTorrentListable(torrentInfo, stateName):
            if torrentInfo.state == States.Paused:
                thumb = os.path.join(__icondir__, 'deluge_paused.png')
            elif torrentInfo.state == States.Downloading:
                thumb = os.path.join(__icondir__, 'deluge_downloading.png')
            elif torrentInfo.state == States.Queued:
                thumb = os.path.join(__icondir__, 'deluge_queued.png')
            elif torrentInfo.state == States.Seeding:
                thumb = os.path.join(__icondir__, 'deluge_seeding.png')
            else:
                thumb = os.path.join(__icondir__, 'unknown.png')
            url = baseurl
            addTorrent(torrentInfo.name + " " + getTranslation(30001) + str(torrentInfo.progress)+"% "+getTranslation(30002) + torrentInfo.getStrSize() + " " + getTranslation(30003) + str(torrentInfo.downloadPayloadRate) + "Kb/s " + getTranslation(30004) + str(torrentInfo.uploadPayloadRate)+"Kb/s " + getTranslation(30005) + torrentInfo.getStrEta(), url, mode, thumb, torrentInfo.torrentId)
            mode = mode + 1

    #xbmc.executebuiltin('Container.SetViewMode(500)') # 55 - List;
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=False)

def performAction(selection):
    restoreSession()
    dialog = xbmcgui.Dialog()
    selectedAction = dialog.select(getTranslation(32001), [getTranslation(32011), getTranslation(32012), getTranslation(32002), getTranslation(32003), getTranslation(32007), getTranslation(32008), getTranslation(32019)])
    if selectedAction == 0:
        webUI.pauseAllTorrents()
    if selectedAction == 1:
        webUI.resumeAllTorrents()
    if selectedAction == 2:
        webUI.pauseTorrent(selection)
    if selectedAction == 3:
        webUI.resumeTorrent(selection)
    if selectedAction == 4:
        removeTorrent(selection, False)
    if selectedAction == 5:
        removeTorrent(selection, True)
    if selectedAction == 6:
        labels = webUI.getLabels()
        labelDialog = xbmcgui.Dialog()
        selectedLabel = labelDialog.select(getTranslation(32020), labels)
        if selectedLabel != -1:
            webUI.labelSetTorrent(selection, labels[selectedLabel])
    xbmc.executebuiltin('Container.Refresh')

def removeTorrent(selection, removeData):
    if __addon__.getSetting('confirmTorrentDeleting'):
        dialog = xbmcgui.Dialog()
        if dialog.yesno(getTranslation(32021), getTranslation(32022)):
            webUI.removeTorrent(selection, False)

def restoreSession():
    try:
        ret = webUI.checkSession()
        if not ret:
            if webUI.login(UT_PASSWORD):
                ret = webUI.connected()
                if not ret:
                    webUI.connectToFirstHost()
    except urllib2.URLError as err:
        log_info(str(err))
        dialog = xbmcgui.Dialog()
        ret = dialog.yesno(__addonname__ + ' ' + getTranslation(32100), getTranslation(32101), getTranslation(32102))
        if ret == True:
            __addon__.openSettings()
        sys.exit()

def pauseAll():
    restoreSession()
    webUI.pauseAllTorrents()
    xbmc.executebuiltin('Container.Refresh')

def resumeAll():
    restoreSession()
    webUI.resumeAllTorrents()
    xbmc.executebuiltin('Container.Refresh')

def get_params():
    param={} # type: dict[str, str]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                    params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                    splitparams={}
                    splitparams=pairsofparams[i].split('=')
                    if (len(splitparams))==2:
                            param[splitparams[0]]=splitparams[1]

    return param

def getTranslation(translationId):
    return __language__(translationId)#.encode('utf8')

def addTorrent(name, url, mode, iconimage, hashNum):
    u = sys.argv[0]+"?"
    ok = True
    point = xbmcgui.ListItem(name,thumbnailImage=iconimage)
    rp = "XBMC.RunPlugin(%s?mode=%s)"
    point.addContextMenuItems([(getTranslation(32011), rp % (sys.argv[0], 1000)), (getTranslation(32012), rp % (sys.argv[0], 1001))], replaceItems=True)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=point,isFolder=False)

def addFilters(filter, mode, label):
    iconimage = ''
    if filter.name == '':
        displayName = getTranslation(30009) + '(' + str(filter.count) + ')'
    else:
        displayName = str(filter)
    u = sys.argv[0] + "?url=&mode=" + str(mode) + "&filterName=" + urllib.parse.quote_plus(filter.name) + "&filterCount=" + str(filter.count)
    if label:
        u = u + "&labelName=" + urllib.parse.quote_plus(label.name) + "&labelCount=" + str(label.count)
    ok = True
    liz = xbmcgui.ListItem(displayName, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels = {"Title": displayName} )
    rp = "XBMC.RunPlugin(%s?mode=%s)"
    liz.addContextMenuItems([(getTranslation(32011), rp % (sys.argv[0], 1000)), (getTranslation(32012), rp % (sys.argv[0], 1001))], replaceItems=True)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)

def addStateFilters(states, label):
    for state in states:
        if state.count > 0:
            addFilters(state, 7007, label)

def listFilters():
    xbmc.log('Listing filters...', xbmc.LOGINFO)
    restoreSession()
    xbmc.log('Session restored', xbmc.LOGINFO)
    addStateFilters(webUI.getStateFilters(), None)
    xbmc.log('StateFilters added', xbmc.LOGINFO)
    labels = webUI.getLabelsFilters()
    xbmc.log('Labels fetched', xbmc.LOGINFO)
    for label in labels:
        if label.count > 0:
            addFilters(label, 5005, label)

    # Start menu button
    #u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&hashNum="+str(hashNum)
    point = xbmcgui.ListItem('Add torrent')
    rp = "XBMC.RunPlugin(%s?mode=%s)"
    # point.addContextMenuItems([(getTranslation(32011), rp % (sys.argv[0], 1000)), (getTranslation(32012), rp % (sys.argv[0], 1001))], replaceItems=True)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=create_url('add_torrent'),listitem=point,isFolder=False)

    # End menu button


    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=False)

def getParams():
    global url, name, mode, hashNum, filterName, filterCount, labelName, labelCount
    try:
        url = urllib.parse.unquote_plus(params['url'])
    except:
        pass
    try:
        name = urllib.parse.unquote_plus(params['name'])
    except:
        pass
    try:
        mode = int(params['mode'])
    except:
        pass
    try:
        hashNum = urllib.parse.unquote_plus(params['hashNum'])
    except:
        pass
    try:
        filterName = urllib.parse.unquote_plus(params['filterName'])
    except:
        pass
    try:
        filterCount = int(urllib.parse.unquote_plus(params['filterCount']))
    except:
        pass
    try:
        labelName = urllib.parse.unquote_plus(params['labelName'])
    except:
        labelName = ''
    try:
        labelCount = int(urllib.parse.unquote_plus(params['labelCount']))
    except:
        labelCount = 0

xbmc.log( '-----------------------------------Deluge.Plugin-Started---', xbmc.LOGINFO )


log_info(' - '.join(sys.argv))

mode = -1
params = get_params()
url = None
name = None
hashNum = None
filterName = None

getParams()

ps = (lambda: urllib.parse.parse_qs(sys.argv[2][1:]))()
action = next(iter(ps.get('action', [])), None)
if action is None:
    log_info("No action, fall back to the old")
    mode = 0
else:
    if action == 'main':
        listFilters()
    elif action == 'add_torrent':
        log_info('Add torrent menu')
        listFilters()
    



xbmc.log('The mode was ' + str(mode), xbmc.LOGINFO )

if mode == 0:
    listFilters()

if mode == 7007:
    restoreSession()
    if labelCount > 0:
        torrents = webUI.getTorrentListByLabel(labelName)
    else:
        torrents = webUI.getTorrentList()
    listTorrents(torrents, filterName)

if mode == 5005:
    restoreSession()
    torrents = webUI.getTorrentListByLabel(filterName)
    states = webUI.getStateList(torrents)
    label = Filter(labelName, labelCount)
    if len(torrents) > int(__addon__.getSetting('torrentCountForStateGrouping')):
        addStateFilters(states, label)
    else:
        listTorrents(torrents, States.All)
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=False)


elif mode == 1000:
    pauseAll()

elif mode == 1001:
    resumeAll()

#elif mode == 1004:
#    limitSpeeds()

#elif mode == 1005:
#    addFiles()

elif 0 < mode < 1000:
    performAction(hashNum)

#TODO: To change mode from int to string. To add a enum class for mode.
