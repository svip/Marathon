from basic import Basic
from marathon import Marathon
from rss import RSS

class Menu(Basic):
	
	def browser_show(self):
		return True
	
	def add_show(self):
		return True
	
	def check_rss(self):
		return True
	
	def settings(self):
		return True

	def run(self):		
		print "You have %s show(s) in your configuration." % len(self.m.shows)
		print "Please select an option:"
		p = self.menu([("SHOW", "Select a show to watch%s" % (" (disabled)" if len(self.m.shows)==0 else "")),
			("ADD", "Add shows"),
			("RSS", "Check RSS feeds"),
			("SETTINGS", "Settings")], "SHOW")
		if p == "SHOW":
			if len(self.m.shows) == 0:
				print "No shows available, please add some."
			else:
				return self.browser_show()
		elif p == "ADD":
			return self.add_show()
		elif p == "RSS":
			return self.check_rss()
		elif p == "SETTINGS":
			return self.settings()

	def __init__(self, options):
		self.m = Marathon()
		if options.empty:
			self.m.c.empty()
		if options.fix:
			self.m.c.fix_config()
		self.rss = RSS(self.m.c.rssfeeds, self.m.c.showdata[0]['rsslastupdate'])
		while self.run():
			pass
