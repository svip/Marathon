import sys

class Basic(object):
	
	def i(self, msg, anoption=False):
		try:
			p = raw_input(msg)
		except EOFError:
			print ""
			self.save()
			print "Quit."
			sys.exit()
		except KeyboardInterrupt:
			return None
		if p == ":quit" or p == ":q":
			self.save()
			print "Quit."
			sys.exit()
		"""
		if anoption:
			if p == ":rss":
				self.rssmenu()
				return None
			if p == ":save" or p == ":s":
				self.save()
				return None
			if p == ":load" or p == ":l":
				self.config_init()
				return None
			if p == "..":
				return "RETURN"
			if p == "/":
				return "TOP"
		self.autosave()
		self.rsscheck()
		"""
		return p
