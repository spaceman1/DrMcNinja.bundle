from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

import string

from lxml import html

PLUGIN_PREFIX = '/photos/drmcninja'
PROVIDER_BASE = 'http://drmcninja.com'
PROVIDER_INDEX = PROVIDER_BASE + '/archive.html'

DAY = 86400
CACHE_TIME = DAY

####################################################################################################

def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, L('Dr. McNinja'), 'icon-default.png', 'art-default.png')
  
  Plugin.AddViewGroup('Details', viewMode='InfoList', mediaType='items')
  Plugin.AddViewGroup('Comic', viewMode='Coverflow', mediaType='items')
  
  MediaContainer.title1 = L('Dr. McNinja')
  MediaContainer.viewGroup = 'Details'
  MediaContainer.art = R('art-default.png')
  
  HTTP.SetCacheTime(CACHE_TIME)
  
####################################################################################################

def CreateDict():
  Dict.Set('archive', MediaContainer())
  Dict.Set('pages', dict())
  Dict.Set('current', MediaContainer())
  Dict.Set('currentURL', '')
  
def UpdateCache():
  dir = MediaContainer()
  archive = getIssues(dir)
  cachedArchive = Dict.Get('archive')
  cachedPages = Dict.Get('pages')
  
  cachedIssueURLs = list()
  for issue in cachedArchive:
    cachedIssueURLs.append(issue._Function__kwargs['key'])
  
  #Log(cachedIssueURLs)
  shouldUpdateCache = False
  for issue in archive:
    key = issue._Function__kwargs['key']

    if key not in cachedIssueURLs:
      dir = MediaContainer()
      cachedPages[key] = grabPages(dir, key)
      shouldUpdateCache = True

  if shouldUpdateCache:
    Dict.Set('archive', archive)
    Dict.Set('pages', cachedPages)
  
  # get current
  current = GetXML(PROVIDER_BASE + '/', True).xpath('//img[@src="images/frontpage_03.gif"]')[0]
  currentURL = current.xpath('parent::a')[0].get('href')
  pages = GetXML(currentURL, True).xpath('//td[@id="pages"]')[0].xpath('descendant::a')
  
  if currentURL != Dict.Get('currentURL'):
    # Here we have a brand new issue
    dir = MediaContainer()
    Dict.Set('current', grabPages(dir, currentURL))
    Dict.Set('currentURL', currentURL)
  else: 
    cachedCurrent = Dict.Get('current')
    for pageNum in range(len(cachedCurrent), len(pages)):

      # Update the current issue cache
      cachedCurrent.Append(grabPage(pages[pageNum]))
      Dict.Set('current', cachedCurrent)

####################################################################################################

def MainMenu():
  dir = MediaContainer()
  current = GetXML(PROVIDER_BASE + '/', True).xpath('//img[@src="images/frontpage_03.gif"]')[0]
  currentURL = current.xpath('parent::a')[0].get('href')
  dir.Append(Function(DirectoryItem(issuePages, title=L('Current Issue'), thumb=R('icon-current.jpg')), key=currentURL))
  return getIssues(dir)

####################################################################################################

def getIssues(dir):
  rows = GetXML(PROVIDER_INDEX, True).xpath('//table/tr')
  images = list()
  links = list()
  descriptions = list()
  names = list()
  for rowNum in range(0, len(rows), 3):
    images = images + rows[rowNum].xpath('child::td//img')
    names = names + rows[rowNum + 1].xpath('child::td')
    links = links + rows[rowNum + 1].xpath('child::td//a[1]')
    descriptions = descriptions + rows[rowNum + 2].xpath('child::td')

  issues = zip(images, links, descriptions, names)
  for issue in issues:
    description = html.tostring(issue[2], method='text', encoding="iso-8859-1")
    description = string.join(description.split(chr(160)),' ').strip()
    name = html.tostring(issue[3], method='text', encoding="iso-8859-1")
    name = string.join(name.split(chr(160)),' ').strip()
    url = issue[1].get('href')
    if not url.startswith('http://'):
      url = PROVIDER_BASE + url
    dir.Append(Function(DirectoryItem(issuePages, title=name, thumb=PROVIDER_BASE + issue[0].get('src'), summary=description), key=url))
    
  return dir

####################################################################################################

def issuePages(sender, key):
  archivedPages = Dict.Get('pages')
  if key == Dict.Get('currentURL'):
    dir = Dict.Get('current')
  elif key in archivedPages:
    dir = archivedPages[key]
  else:
    dir = MediaContainer()
    dir = grabPages(dir, key)
  dir.title2 = sender.itemTitle
  dir.viewGroup = 'Comic'
  return dir
  
def grabPages(dir, key):
  pages = GetXML(key, True).xpath('//td[@id="pages"]')
  if len(pages) != 0:
    pages = pages[0].xpath('descendant::a')
    for page in pages:
      dir.Append(grabPage(page))
  else:
    # issue 1/2 is just a series of images
    for image in GetXML(key, True).xpath('//img'):
      thumb = image.get('src')
      if thumb.startswith('mcdonalds'):
        thumb = PROVIDER_BASE + '/' + thumb
        url = thumb.replace('_thumb','')
        dir.Append(PhotoItem(url, thumb=thumb, title=''))
  return dir
  
def grabPage(page):
  image = GetXML(PROVIDER_BASE + page.get('href'), True).xpath('//table/tr[2]/td[3]/img')[0]
  title = image.get('title')
  thumb = PROVIDER_BASE + image.get('src')
  url = thumb.replace('_thumb','')
  return PhotoItem(url, thumb=thumb, title=title)

####################################################################################################
  
def GetXML(theUrl, use_html_parser=False):
  return XML.ElementFromString(HTTP.Request(url=theUrl, cacheTime=CACHE_TIME, encoding="iso-8859-1"), use_html_parser)

####################################################################################################
