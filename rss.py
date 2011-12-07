import time, urllib
from xml.dom.minidom import parseString

class RSS:
	
	rssfeeds = []
	lastupdate = 0
	
	def __init__(self, feeds, lastupdate):
		self.update_feeds(feeds, lastupdate)
		for feed in feeds:
			self.rssfeeds.append({'feed' : feed, 'recentcheck' : False, 
				'lastresult' : False, 'lastupdate' : lastupdate})
	
	def update_feeds(self, feeds, lastupdate=0):
		for feed in feeds:
			self.rssfeeds.append({'feed' : feed, 'recentcheck' : False, 
				'lastresult' : False, 'lastupdate' : lastupdate})		
	
	def check_feed(self, feed):
		if feed['recentcheck']:
			return feed
		try:
			content = urllib.urlopen(feed['feed'])
		except IOError:
			print "Error reading `%s':" % feed['feed']
			print "Connection failed."
			return feed
		except KeyboardInterrupt:
			print "Cancelled..."
			return feed
		try:
			xml = parseString(content.read())
		except xml.parsers.expat.ExpatError:
			print "Error parsing content, server must be returning something wrong."
			return feed
		for item in xml.getElementsByTagName('item'):
			date = time.mktime(time.strptime(item.getElementsByTagName('pubDate')[0].childNodes[0].data, "%a, %d %b %Y %H:%M:%S +0000"))
			if date > feed['lastupdate']:
				feed['lastresult'] = True
				feed['recentcheck'] = True
				return feed
		feed['recentcheck'] = True
		return feed
	
	def check(self):
		i = 0
		for feed in self.rssfeeds:
			self.rssfeeds[i] = self.check_feed(feed)
			if self.rssfeeds[i]['lastresult']:
				return True
			i += 0
		return False
	
	def get_torrents_from_feed(self, i, feed):
		try:
			content = urllib.urlopen(feed['feed'])
		except IOError:
			print "Error reading `%s':" % feed['feed']
			print "Connection failed."
			return []
		try:
			xml = parseString(content.read())
		except xml.parsers.expat.ExpatError:
			print "Error parsing content, server must be returning something wrong."
			return []
		newest = 0
		items = []
		for item in xml.getElementsByTagName('item'):
			date = time.mktime(time.strptime(item.getElementsByTagName('pubDate')[0].childNodes[0].data, "%a, %d %b %Y %H:%M:%S +0000"))
			if date > feed['lastupdate']:
				if date > newest:
					newest = date
				title = item.getElementsByTagName('title')[0].childNodes[0].data
				url = item.getElementsByTagName('guid')[0].childNodes[0].data
				items.append({'title': title, 'url': url})
		feed['lastupdate'] = newest
		feed['recentcheck'] = False
		feed['lastresult'] = False
		self.rssfeeds[i] = feed
		return items	
			
	def get_torrents(self):
		items = []
		i = 0
		for feed in self.rssfeeds:
			items += self.get_torrents_from_feed(i, feed)
			i += 1
		return items

