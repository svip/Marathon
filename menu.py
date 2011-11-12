from basic import Basic
from marathon import Marathon
from rss import RSS
import sys

class Menu(Basic):
	
	def menu(self, menu, default=None, doprint=True):
		i = 1
		tmp = {}
		tdefault = None
		disableds = {}
		for item in menu:
			d = ""
			disableds.update({item[0]: False})
			try:
				if item[2]:
					d = " (disabled)"
					disableds.update({item[0]: True})
			except IndexError:
				pass
			if doprint:
				print "%s: %s%s" % (i, item[1], d)
			tmp.update({i : item[0]})
			if default == item[0]:
				tdefault = i
			i += 1
		p = self.ii("Option%s: " % (" (%s)" % tdefault if default!=None else ""))
		try:
			w = int(p)
			if disableds[tmp[w]]:
				print "Option disabled, try again..."
				return self.menu(menu, default, False)
			return tmp[w]
		except (TypeError, ValueError):
			if p == None and default != None:
				if disableds[default]:
					print "Option disabled, try again..."
					return self.menu(menu, default, False)
				return default
			return p
		except KeyError:
			return p
	
	def rsscheck(self):
		if self.rss.check():
			print "There are new torrents available."
			print "Type :rss to see them."
	
	def ii(self, msg):
		self.m.c.autosave()
		opt = self.i(msg, True)
		self.rsscheck()
		print
		if opt == "SAVE":
			self.m.save()
			return None
		elif opt == "RSS":
			self.m.check_rss()
			return None
		elif opt == "LOAD":
			self.m.c.config_init()
			return None
		elif opt == "QUIT":
			print "Quit."
			self.m.save()
			sys.exit()
		else:
			return opt
	
	def browser_shows(self):
		print "Select show:"
		i = 0
		for show in self.m.get_shows():
			i += 1
			print "%s: %s (%s)" % (i, show, self.m.get_episode_amount(show))
		p = self.ii("Option: ")
		if not p:
			return False
		elif p == "RETURN":
			return True
		elif p == "TOP":
			return True
		else:
			try:
				self.m.set_currentshow(p)
			except (IndexError, ValueError, TypeError):
				print "Ununderstood option."
			return True
	
	def add_show(self):
		self.m.add_show()
		return True
	
	def check_rss(self):
		return True
	
	def settings(self):
		return True

	def run(self):		
		print "You have %s show(s) in your configuration." % self.m.get_show_count()
		print "Please select an option:"
		p = self.menu(
			[("SHOW", "Select a show to watch", self.m.get_show_count()==0),
			("ADD", "Add shows"),
			("RSS", "Check RSS feeds"),
			("SETTINGS", "Settings")], "SHOW")
		if p == "SHOW":
			if len(self.m.shows) == 0:
				print "No shows available, please add some."
			else:
				return self.browser_shows()
		elif p == "ADD":
			return self.add_show()
		elif p == "RSS":
			return self.check_rss()
		elif p == "SETTINGS":
			return self.settings()
		else:
			return self.run()

	def __init__(self, options):
		self.m = Marathon()
		if options.empty:
			self.m.c.empty()
		if options.fix:
			self.m.c.fix_config()
		self.rss = RSS(self.m.c.rssfeeds, self.m.c.showdata[0]['rsslastupdate'])
		while self.run():
			pass
		self.m.save()

