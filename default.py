#!/usr/bin/python
import sys, urllib, json, urlparse, re
import xbmc, xbmcgui
import xbmcplugin
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

def readContent(url):
	response = urllib.urlopen(url)
	content = response.read()
	response.close()
	return content

def getVideoLinks(url):
	print "Reading " + url
	content = readContent('http://www.indopia.com/'+url)
	url = url.replace('./showtime/watch/movie/','')
	id = re.sub(r'/.*', '', url)
	linksContainer = common.parseDOM(content, "div", attrs = { "class": "bw-cont"})
	linksList = common.parseDOM(linksContainer, "ul", attrs = {})
	links = common.parseDOM(linksList, "a", attrs = {}, ret = "href")
	titles = common.parseDOM(linksList, "a", attrs = {}, ret = "title")
	list = []
	print "Ready to prepare list. Links found:" + str(len(links))
	for x in xrange(len(links)):
		jsurl = re.compile("javascript").search(links[x])
		if jsurl is None:
			video = {}
			video["title"] = "Play " + titles[x] + " resolution"
			video["link"] = 'http://38.76.15.172/vod/_definsts_/mp4:mp4/'+titles[x].lower()+'/'+id+'.mp4/playlist.m3u8'
			list.append(video)
	return list

if mode is None:
	content = readContent(website + '/movies/')
	url = build_url({'mode': 'search'})
	li = xbmcgui.ListItem('Search', iconImage='DefaultVideo.png')
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
	urls = common.parseDOM(content, "a", attrs = { "class": "mainmenulnk" }, ret = "href")
	titles = common.parseDOM(content, "a", attrs = { "class": "mainmenulnk" })
	for x in xrange(len(urls)):
		title = titles[x].encode('utf-8')
		url = build_url({'mode': 'category', 'url': urls[x]})
		li = xbmcgui.ListItem(title, iconImage='DefaultVideo.png')
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
	xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'category':
	url = args['url'][0]
	content = readContent(url)
	titles = common.parseDOM(content, "h2", attrs = {}, ret = 'title')
	anchors = common.parseDOM(content, "div", attrs = { "class": "r" })
	urls = common.parseDOM(content, "a", attrs = {}, ret = 'href')

	for x in xrange(len(urls)):
		title = titles[x]
		url = build_url({'mode': 'listvideos', 'url': urls[x]})
		li = xbmcgui.ListItem(title, iconImage='DefaultVideo.png')
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
		li = xbmcgui.ListItem(name, iconImage='DefaultVideo.png')
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
	xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'listresolutions':
	url = args['url'][0]
	name = args['name'][0]
	list = getVideoLinks(url)
	for video in list:
		li = xbmcgui.ListItem(video["title"], iconImage='DefaultVideo.png')
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=video["link"], listitem=li)	
xbmcplugin.endOfDirectory(addon_handle)