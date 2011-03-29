PLUGIN_PREFIX = '/photos/drmcninja'
PROVIDER_BASE = 'http://drmcninja.com'

CACHE_1YEAR = 365 * CACHE_1DAY
CACHE_TIME = CACHE_1DAY
COVERS = [
'http://drmcninja.com/wp-content/uploads/mccover1.gif',
'http://drmcninja.com/wp-content/uploads/bunyancover.gif',
'http://drmcninja.com/wp-content/uploads/twocover.gif',
'http://drmcninja.com/wp-content/uploads/threecover.gif',
'http://drmcninja.com/wp-content/uploads/fourcover.gif',
'http://drmcninja.com/comics/2006-11-025p2.gif',
'http://drmcninja.com/wp-content/uploads/guest2cover1.jpg',
'http://drmcninja.com/wp-content/uploads/fivecover.jpg',
'http://drmcninja.com/comics/2007-08-019p1.png',
'http://drmcninja.com/comics/2007-11-0210p6.png',
'http://drmcninja.com/comics/2008-03-1711p4.png',
'http://drmcninja.com/wp-content/uploads/guest08cover1.gif',
'http://drmcninja.com/comics/2008-08-1113p2.jpg',
'http://drmcninja.com/comics/2008-12-1714p2.png',
'http://drmcninja.com/comics/2009-06-11-15p1.jpg',
'http://drmcninja.com/wp-content/uploads/guestweek09cover2.png',
'http://drmcninja.com/comics/2010-01-06-17p14.jpg',
None,# Judy gets a kitten
'http://drmcninja.com/comics/2010-07-26-19p1.jpg',
'http://drmcninja.com/comics/2010-08-11-20p2.jpg',
'http://drmcninja.com/comics/2011-03-09-21p08.jpg'
]

####################################################################################################

def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, L('Dr. McNinja'), 'icon-default.png', 'art-default.png')
  
  Plugin.AddViewGroup('_List', viewMode='List', mediaType='items')
  
  MediaContainer.title1 = L('Dr. McNinja')
  MediaContainer.viewGroup = '_List'
  MediaContainer.art = R('art-default.png')
  DirectoryItem.thumb = R('icon-default.png')
  
  HTTP.SetCacheTime(CACHE_TIME)
  
####################################################################################################

def MainMenu():
	dir = MediaContainer()
	index = 0
	for item in HTML.ElementFromURL(PROVIDER_BASE).xpath('//select[@name="series_select"]')[0].xpath('./option'):
		try: thumb = COVERS[index]
		except IndexError: thumb = R('icon-default.png')
		if thumb == None: thumb = R('icon-default.png')
		
		dir.Append(Function(DirectoryItem(IssueMenu, title=item.text, thumb=thumb), offset=index))
		index += 1
	return dir

def IssueMenu(sender, offset):
	dir = MediaContainer(title2=sender.itemTitle)
	seriesArray = JSON.ObjectFromString(HTTP.Request('http://drmcninja.com/mcninja-js.php?ver=1.0').content.split('series_arr = ')[1].split(';\n')[0])
	pageIndex = 1
	if offset == 18: # AxeCop Cross-over
		for i in range(1, 5):
			dir.Append(PhotoItem('http://axecop.com/images/uploads/axecopMC%i.png' % i, title='19p%i' % i))
		pageIndex = 6
	for item in seriesArray[offset]['posts']:
		comicURL = 'http://drmcninja.com/archives/comic/' + item
		title = 'p%i' % pageIndex
		pageIndex += 1
		dir.Append(Function(PhotoItem(GetPhotoItem, title=title, thumb=Function(GetPhotoItem, url=comicURL)), url=comicURL))
	return dir

def GetPhotoItem(url, sender=None):
	return Redirect(HTML.ElementFromURL(url).xpath('//div[@id="comic"]/img')[0].get('src'))