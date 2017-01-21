#!/usr/bin/python
import sys, urllib, urllib2, json, urlparse, re
import xbmc, xbmcgui
import xbmcplugin
import xbmcaddon
import datetime
reload(sys)
sys.setdefaultencoding('utf8')
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson
import CommonFunctions
common = CommonFunctions
common.plugin = "Indopia"
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

website = 'http://www.indopia.com'
appicon = 'http://www.indopia.com/images/logo.jpg'
base_url = sys.argv[0]

addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'movies')

args = urlparse.parse_qs(sys.argv[2][1:])

mode = args.get('mode', None)


def build_url(query):
    url = base_url + '?' + urllib.urlencode(query)
    return url
xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def GUIEditExportName():
    exit = True
    while (exit):
        kb = xbmc.Keyboard('default', 'heading', True)
        kb.setDefault('')
        kb.setHeading('Search movies')
        kb.setHiddenInput(False)
        kb.doModal()
        if (kb.isConfirmed()):
            name = kb.getText()
            exit = False
    return(name)


def getMovies(postData):
    xbmc.executebuiltin('Notification(Status!, Requesting listing page., 500, appicon)')
    content = getMovieListingPage(postData)
    hahadiv = common.parseDOM(content, "div", attrs = { "class": "haha" })
    results = common.parseDOM(hahadiv, "div", attrs = { "style": "float:left;width:425px;margin:5px 0px;border:red solid 0px;" })
    return results


def getMovieListingPage(postData):
    url = 'http://www.indopia.com/movies/index/years/'
    data = urllib.urlencode(postData)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    return response.read()

def getCategories():
    url = 'http://www.indopia.com/movies/index/years/'
    content = readContent(url)
    categories = common.parseDOM(content, "select", attrs = { "name": "ygen"})
    return common.parseDOM(categories, "option")

def readContent(url):
    response = urllib.urlopen(url)
    content = response.read()
    response.close()
    return content


def getImage(url):
    content = readContent('http://www.indopia.com/'+url)
    thumbnail = common.parseDOM(content, "meta", attrs = { "property": "og:image"}, ret="content")
    return thumbnail[0]


def getLinkPrefix(content):
    match=re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", content)
    if match:
        return match[0]


def getVideoLinks(url, name):
    print "Reading " + url
    content = readContent('http://www.indopia.com/'+url)
    thumbnail = getImage(url)
    url = url.replace('./showtime/watch/movie/','')
    id = re.sub(r'/.*', '', url)
    indopiasettings = xbmcaddon.Addon('plugin.video.indopia')
    server = indopiasettings.getSetting('server')
    if server == 'Automatic':
        server = 'http://' + getLinkPrefix(content)
    linksContainer = common.parseDOM(content, "div", attrs = { "class": "bw-cont"})
    linksList = common.parseDOM(linksContainer, "ul", attrs = {})
    links = common.parseDOM(linksList, "a", attrs = {}, ret = "href")
    titles = common.parseDOM(linksList, "a", attrs = {}, ret = "title")
    list = []
    print "Ready to prepare list. Links found:" + str(len(links))
    for x in xrange(len(links)):
        index = len(links) - x - 1
        jsurl = re.compile("javascript").search(links[index])
        if jsurl is None:
            video = {}
            video["image"] = thumbnail
            video["title"] = name + " in " + titles[index] + " resolution"
            video["link"] = server+'/vod/_definsts_/mp4:mp4/'+titles[index].lower()+'/'+id+'.mp4/playlist.m3u8'
            list.append(video)
    return list

if mode is None:
    content = readContent(website + '/movies/')
    url = build_url({'mode': 'search'})
    li = xbmcgui.ListItem('Search', iconImage='DefaultVideo.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    urls = common.parseDOM(content, "a", attrs = { "class": "mainmenulnk" }, ret = "rel")
    print urls
    titles = common.parseDOM(content, "a", attrs = { "class": "mainmenulnk" })
    for x in xrange(len(urls)):
        title = titles[x].encode('utf-8')
        url = build_url({'mode': 'listyears', 'ylan': urls[x]})
        li = xbmcgui.ListItem(title, iconImage='DefaultVideo.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'listyears':
    ylan = args['ylan'][0]
    year = datetime.datetime.now().year
    for x in xrange(year, 1939, -1):
        year = str(x)
        url = build_url({'mode': 'listpages', 'ysel': year, 'ylan': ylan, 'showcategory': 1})
        li = xbmcgui.ListItem(year, iconImage='DefaultVideo.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'listpages':
    ylan = args['ylan'][0]
    ysel = args['ysel'][0]
    ygen = args.get('ygen', [0])[0]
    xbmc.log(msg="ygen is " + str(ygen) + '::ysel::' + str(ysel) + '::ylan::' + str(ylan))
    page = 0
    if ygen == 0:
        url = build_url({'mode': 'listcategories', 'ysel': ysel, 'ylan': ylan})
        categorylabel = xbmcgui.ListItem('Categories', iconImage='DefaultVideo.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=categorylabel, isFolder=True)
    xbmc.executebuiltin('Notification(Status!, Creating pagination, 500, appicon)')
    results = getMovies({'ysel' : ysel, 'ygen'  : ygen, 'ylan': ylan})
    for x in xrange(0, len(results), 10):
        name = ''
        last = x+9
        if last >= len(results):
            last = len(results) - 1
        for t in xrange(x, last):
            name = name + common.parseDOM(results[t], "a", attrs={})[0] + ' - '
        name = name + common.parseDOM(results[last], "a", attrs={})[0]
        url = build_url({'mode': 'listpaginatedmovies', 'page': str(page), 'name': name, 'ysel' : ysel, 'ylan': ylan, 'ygen': ygen})
        li = xbmcgui.ListItem(name, iconImage='DefaultVideo.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
        page += 1
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'listcategories':
    ylan = args['ylan'][0]
    ysel = args['ysel'][0]
    results = getCategories()
    xbmc.log(msg='Total count of options'+str(len(results)))
    for x in xrange(1, len(results)):
        name = results[x]
        url = build_url({'mode': 'listpages', 'ysel': ysel, 'ylan': ylan, 'ygen': x})
        li = xbmcgui.ListItem(name, iconImage='DefaultVideo.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'listpaginatedmovies':
    ylan = args['ylan'][0]
    ysel = args['ysel'][0]
    ygen = args.get('ygen', [0])[0]
    page = int(args['page'][0])
    xbmc.log(msg="listpaginatedmovies args " + str(ygen) + '::ysel::' + str(ysel) + '::ylan::' + str(ylan))
    results = getMovies({'ysel' : ysel, 'ygen'  : ygen, 'ylan': ylan})
    xbmc.executebuiltin('Notification(Status!, Fetching individual movie info)')
    start = page * 10
    end = start+10
    if end > len(results):
        end = len(results)
    for x in xrange(start, end):
        link = common.parseDOM(results[x], "a", attrs = { "title": "Play" }, ret = 'href')
        title = common.parseDOM(results[x], "a", attrs = {})
        name = title[0]
        url = build_url({'mode': 'listresolutions', 'url': link[0], 'name': name})
        li = xbmcgui.ListItem(name, iconImage=getImage(link[0]))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)


elif mode[0] == 'search':
    print 'Requesting kb'
    searchstr = GUIEditExportName()
    url = 'http://www.indopia.com/search/index.php?query='+searchstr+'&searchmodule=Movies&cpage=1&sort='
    content = readContent(url)
    results = common.parseDOM(content, "div", attrs = { "class": "jumbo" })
    for x in xrange(len(results)):
        link = common.parseDOM(results[x], "a", attrs = { "title": "Play" }, ret = 'href')
        title = common.parseDOM(results[x], "a", attrs = {})
        name = title[0]
        url = build_url({'mode': 'listresolutions', 'url': link[0], 'name': name})
        li = xbmcgui.ListItem(name, iconImage=getImage(link[0]))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'listresolutions':
    url = args['url'][0]
    name = args['name'][0]
    list = getVideoLinks(url, name)
    xbmc.executebuiltin('Notification(Info!, Fetching info for '+name+', 500, appicon)')
    for video in list:
        print "the video url is " + video["link"]
        li = xbmcgui.ListItem(video["title"], iconImage=video["image"])
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=video["link"], listitem=li)
xbmcplugin.endOfDirectory(addon_handle)
