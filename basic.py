import sys

class Basic(object):
	
	YES, NO = range(2)

	def yesno(self, msg, default=None):
		if default == None:
			default = self.YES
		if default == self.YES:
			dmsg = "Y/n"
			default = self.YES
		else:
			dmsg = "y/N"
			default = self.NO
		opt = self.i("%s (%s) " % (msg, dmsg))
		if opt == None:
			return default == self.YES
		elif opt.lower() == "y":
			return True
		elif opt.lower() == "n":
			return False
		else:
			return self.yesno(msg, default)
	
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
		if p == "":
			return None
		return p
