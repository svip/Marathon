from basic import Basic
from marathon import Marathon

class Menu(Basic):

	def __init__(self, options):
		self.m = Marathon()
		if options.empty:
			self.m.c.empty()
		if options.fix:
			self.m.c.fix_config()
		self.rss = RSS(self.c.rssfeeds, self.c.showdata[0]['rsslastupdate'])
		self.run()
