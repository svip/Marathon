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
			return "QUIT"
		except KeyboardInterrupt:
			return None
		if p == ":quit" or p == ":q":
			return "QUIT"
		if anoption:
			if p == ":rss":
				return "RSS"
			if p == ":save" or p == ":s":
				return "SAVE"
			if p == ":load" or p == ":l":
				return "LOAD"
			if p == "..":
				return "RETURN"
			if p == "/":
				return "TOP"
		if p == "":
			return None
		return p
