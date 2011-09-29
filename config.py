import re, os, sys, pickle
from basic import Basic

class Config(Basic):

	configfile = "./config"
	mplayerconfig = ""
	showdata = {}
	rssfeeds = []
	torrentwatchdir = ''
	knownfileextensions = ["mpg", "avi", "mkv", "mp4"]
		
	def config_init(self):
		try:
			f = open(self.configfile)
			self.showdata = pickle.load(f)
			self.shows = []
			f.close()
			print "Data loaded."
		except IOError:
			print "No configuration file found..."
			print "Creating configuration `%s'..." % self.configfile
			self.showdata = {0 : {'mplayerconfig': '', 'currentshow':None,
				'torrentwatchdir': '', 'rssfeeds' : [], 'rsslastupdate' : 0.0}}
			f = open(self.configfile, "w")
			pickle.dump(self.showdata, f)
			f.close()
		for s in self.showdata:
			if s == 0:
				continue
			self.shows.append(s)
		try:
			self.mplayerconfig = self.showdata[0]['mplayerconfig']
		except KeyError:
			self.dataerror()
			self.mplayerconfig = ''
	
	def dataerror(self):
		print "Data error.  Please run script with -f"
	
	def fix_config(self):
		# test settings
		print "Attempting to fix the showdata..."
		try:
			t = self.showdata[0]
		except KeyError:
			self.showdata.update({0: {}})
		try:
			t = self.showdata[0]['mplayerconfig']
		except KeyError:
			self.showdata[0].update({'mplayerconfig' : ''})
		try:
			t = self.showdata[0]['currentshow']
		except KeyError:
			self.showdata[0].update({'currentshow' : None})
		topop = []
		for show in self.showdata:
			if show == 0:
				continue
			try:
				t = self.showdata[show]['currentepisode']
			except KeyError:
				self.showdata[show].update({'currentepisode' : (1, 1)})
			try:
				t = self.showdata[show]['episodes']
				if len(t) == 0:
					# empty?  Delete this show!
					print "`%s' contained no episodes; deleting..." % show
					topop.append(show)
					continue
			except KeyError:
				# no episodes?  Better delete this show.
				print "`%s' contained no episodes; deleting..." % show
				topop.append(show)
				continue
			curep = self.showdata[show]['currentepisode']					
			while True:
				try:
					season = self.showdata[show]['episodes'][curep[0]]
					try:
						episode = self.showdata[show]['episodes'][curep[0]][curep[1]]
						curep = (curep[0], curep[1])
						break
					except KeyError:
						curep = (curep[0], curep[1]+1)
				except KeyError:
					curep = (curep[0]+1, 1)
			self.showdata[show]['currentepisode'] = curep
		for pop in topop:
			self.showdata.pop(pop)
		print "Fixed."
		self.save()				

	def empty(self):
		print "This will empty all your configuration files."
		print "ALL YOUR SETTINGS WILL BE LOST."
		r = None
		while r == None:
			r = raw_input("Are you sure you want to do this? (y/N) ")
			if r == "" or r.lower() == "n":
				w = False
			elif r.lower() == "y":
				w = True
			else:
				r = None
		if w:
			print "Emptying configuration file...",
			f = open(self.configfile, "w")
			f.write("")
			f.close()
			print "done"
		else:
			print "Not emptying configuration file..."	
	
	def autosave(self):
		if time.time() - os.stat(self.configfile).st_mtime > 60*30:
			print "Configuration file not saved for 30 minutes..."
			print "Autosaving..."
			self.save()
	
	def save(self):
		f = open(self.configfile, "w")
		self.showdata[0].update({'rsslastupdate' : self.rss.lastupdate})
		self.showdata[0].update({'rssfeeds' : self.rssfeeds})
		self.showdata[0].update({'torrentwatchdir' : self.torrentwatchdir})
		pickle.dump(self.showdata, f)
		f.close()
		print "Saved."
	
	def __init__(self):
		self.config_init()
		if options.fix:
			self.fix_config()
		try:
			self.rssfeeds = self.showdata[0]['rssfeeds']
			self.rss = RSS(self.rssfeeds, self.showdata[0]['rsslastupdate'])
		except KeyError:
			self.rss = RSS([], 0)
		try:
			self.torrentwatchdir = self.showdata[0]['torrentwatchdir']
		except KeyError:
			self.torrentwatchdir = ''
