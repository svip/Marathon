#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from basic import Basic
from optparse import OptionParser
import re, os, sys, pickle, time, urllib
from rss import RSS
from config import Config

class Marathon(Basic):

	c = None
	rss = None
	shows = []
	currentshow = ''
	knownfileextensions = ["mpg", "avi", "mkv", "mp4"]
	
	MAIN, SHOW, SHOWS, ADDSHOWS, RSS, SETTINGS = range(6)
	
	def rsscheck(self):
		if self.rss.check():
			print "There are new torrents available."
			print "Type :rss to see them."
	
	def is_video(self, f):
		w = f.split(".")
		return w[len(w)-1] in self.knownfileextensions
	
	def analyse_filename(self, f, backupseason):
		try:
			t = re.search("s?([0-9][0-9]?) ?[xe]([0-9][0-9]?)", f, re.I)
			season = int(t.group(1))
			number = int(t.group(2))
		except AttributeError:
			print "File `%s' confused me..." % f
			try:
				if backupseason == None:
					season = int(self.i("Which season is this? "))
				else:
					season = backupseason
				number = int(self.i("Which number in the season is this? "))
			except ValueError:
				return self.analyse_filename(f, backupseason)
		print "Assuming season %s, episode %s for `%s'..." % (season, number, f)
		return (f, season, number)
	
	def obtain_episodes(self, episodes, top, d, backupseason):
		for r, d, files in os.walk(top + "/" + d):
			for f in files:
				if self.is_video(f):
					(filename, season, number) = self.analyse_filename(f, backupseason)
					try:
						t = episodes[season]
					except:
						episodes.update({season : {}})
					episodes[season].update({number : os.path.join(r, filename)})
		return episodes
	
	def season_guess(self, d):
		t = re.search("(season|s) ?([0-9][0-9]?)", d, re.I)
		try:
			season = int(t.group(2))
		except (ValueError, AttributeError):
			return None
		return season
	
	def known_episode(self, show, filename):
		for season in show['episodes']:
			for episode in show['episodes'][season]:
				if filename in show['episodes'][season][episode]:
					return True
		return False
	
	def add_files(self, title, show, ignoreknown=False):
		print "Where should I look for files of it?"
		path = self.i("Path: ")
		searchtitle = title.lower().replace(" ", "[ \._]")
		for r, dirs, files in os.walk(path):
			for d in dirs:
				if re.match(searchtitle, d, re.I):
					print "Found `%s'..." % d
					p = self.i("Should I include this directory for this show? (Y/n) ")
					if p == "" or p.lower() == "y":
						seasonguess = self.season_guess(d)
						s = self.i("Which season? (0 for more than one%s) " % (", blank for season %s" % seasonguess if seasonguess != None else ""))
						if s == "0":
							s = None
						elif s == "":
							if seasonguess == None:
								s = None
							else:
								s = seasonguess
						show['episodes'] = self.obtain_episodes(show['episodes'], path, d, s)
						print ""
			for f in files:
				if re.match(searchtitle, f, re.I):
					if ignoreknown and self.known_episode(show, f):
						print "Ignoring `%s' as I know it..." % f
					else:
						print "Found file `%s'..." % f
						p = self.i("Should I include this file for this show? (Y/n) ")
						if p == "" or p.lower() == "y":
							(filename, season, number) = self.analyse_filename(f, None)
							try:
								show['episodes'][season].update({number : {'file': os.path.join(r, filename), 'mplayersettings': ''}})
							except:
								show['episodes'].update({season : {number: {'file': os.path.join(r, filename), 'mplayersettings': ''}}})
							print ""
			break
				
		return show
	
	def add_show(self):
		print "Time to configure a new show..."
		show = {'episodes' : {}, 'mplayersettings': ''}
		title = self.i("Title: ")
		show.update({'title' : title, 'currentepisode' : (1, 1)})
		show = self.add_files(title, show)
		while True:
			p = self.i("Should we include another directory? (y/N) ")
			if p.lower() == "y":
				show = self.add_files(title, show)
			else:
				break
		self.c.showdata.update({title : show})
		if not title in self.shows:
			self.shows.append(title)
	
	def mplayer(self, filename, mplayersettings=None):
		if mplayersettings==None:
			s = os.system("mplayer %s \"%s\"" % (self.c.mplayerconfig, filename))
		else:
			s = os.system("mplayer %s \"%s\"" % (mplayersettings, filename))			
		return s == 0
	
	def watch(self, curep):
		ep = self.c.showdata[self.currentshow]['episodes'][curep[0]][curep[1]]
		try:
			s = self.c.showdata[self.currentshow]['mplayersettings']
			if s.strip() == '':
				s = None
		except KeyError:
			s = None
		if self.mplayer(ep, s):
			self.c.showdata[self.currentshow]['currentepisode'] = self.next_episode(self.c.showdata[self.currentshow]['episodes'], curep)
			return True
		else:
			return False
	
	def cwatch(self, curep):
		while True:
			if self.watch(curep):
				curep = self.c.showdata[self.currentshow]['currentepisode']
			else:
				break
	
	def get_episodes_left(self, showdata):
		try:
			curep = showdata['currentepisode']
		except:
			curep = (1,1)
		c = 0
		for season in showdata['episodes']:
			if season < curep[0]:
				continue
			for episode in showdata['episodes'][season]:
				if season == curep[0] and episode <= curep[1]:
					continue
				c += 1
		return c
	
	def seasonsort(self, x, y):
		return x[0] - y[0]
	
	def handle_episode(self, show, season, episode):
		print ""
		print "Episode: (S%sE%s)\n%s" % (self.z(season), self.z(episode), self.c.showdata[show]['episodes'][season][episode])
		p = self.menu([("WATCH", "Watch"),
			("CURRENT", "Set this to current"),
			("EDIT", "Edit"),
			("REMOVE", "Remove")], None)
		if p == "RETURN":
			return
		else:
			if p == "WATCH":
				pass
			elif p == "CURRENT":
				self.c.showdata[show]['currentepisode'] = (season, episode)
				print "Current episode to season %s, episode %s." % (season, episode)
			elif p == "EDIT":
				pass
			elif p == "REMOVE":
				self.c.showdata[show]['episodes'][season].pop(episode)
				print "Removed."
			self.handle_episode(show, season, episode)
	
	def browse_season(self, show, season):
		print ""
		print "Episodes of season %s:" % season
		tmp = []
		for episode in self.c.showdata[show]['episodes'][season]:
			t = self.c.showdata[show]['episodes'][season][episode]
			t = t.split("/")
			tmp.append((episode, t[len(t)-1]))
		tmp.sort(self.seasonsort)
		for episode in tmp:
			print "%s: %s" % episode
		p = self.i("Option: ", True)
		if p == "RETURN":
			return
		else:
			try:
				e = int(p)
				t = self.c.showdata[show]['episodes'][season][e]
				self.handle_episode(show, season, e)
			except (ValueError, KeyError):
				pass
			self.browse_season(show, season)
	
	def browse_show(self, show):
		print ""
		print "Known seasons:"
		tmp = []
		topop = []
		for season in self.c.showdata[show]['episodes']:
			try:
				int(season)
				tmp.append((season, len(self.c.showdata[show]['episodes'][season])))
			except ValueError:
				topop.append(season)
		for p in topop:
			self.c.showdata[show]['episodes'].pop(p)
		tmp.sort(self.seasonsort)
		for season in tmp:
			print "%s: (%s episodes)" % season
		p = self.i("Option: ", True)
		if p == "RETURN":
			return
		else:
			try:
				s = int(p)
				t = self.c.showdata[show]['episodes'][s]
				self.browse_season(show, s)
			except (ValueError, KeyError, TypeError):
				pass
			self.browse_show(show)
		
	def set_currentshow(self, s):
		self.currentshow = s
		try:
			self.c.showdata[0]['currentshow'] = self.currentshow
		except KeyError:
			try:
				self.c.showdata[0].update({'currentshow' : self.currentshow})
			except KeyError:
				self.c.showdata.update({0 : {'currentshow' : self.currentshow}})
	
	def menu(self, menu, default=None):
		i = 1
		tmp = {}
		tdefault = None
		for item in menu:
			print "%s: %s" % (i, item[1])
			tmp.update({i : item[0]})
			if default == item[0]:
				tdefault = i
			i += 1
		p = self.i("Option%s: " % (" (%s)" % tdefault if default!=None else ""), True)
		try:
			w = int(p)
			return tmp[w]
		except (TypeError, ValueError):
			if p == "" and default != None:
				return default
			return p
		except KeyError:
			return p
	
	def download_torrent(self, url, title):
		os.system("wget \"%s\" -O \"%s/%s.torrent\"" % (url, self.c.torrentwatchdir, title.replace(' ', '_')))
	
	def rssmenu(self):
		if len(self.rssfeeds) < 1:
			t = self.i("You have no feeds set, want to set one now? (Y/n)" )
			if t != 'y' and t != '':
				return
			if self.torrentwatchdir == '':
				directory = self.i("Please type the directory you want the torrents to be saved in (no trailing /):")
				self.torrentwatchdir = directory
			feed = self.i("Please type in the RSS feed URL:")
			self.rssfeeds = [feed]
			self.rss.update_feeds(self.rssfeeds)
		items = self.rss.get_torrents()
		if len(items) < 1:
			print "No new RSS items."
		else:
			fullbreak = False
			for item in items:
				print item['title']
				action = ''
				while True:
					action = self.i("Download? (Y/n) ")
					if action == None:
						fullbreak = True
						break
					if action == '':
						action = 'y'
					action = action.lower()
					if not action in ['y', 'n']:
						print "Not understood."
					else:
						break
				if fullbreak:
					break
				if action == 'y':
					self.download_torrent(item['url'], item['title'])
	
	def run(self):
		# this will eventually be more fluid and just a hackish
		# run loop like this.
		menu = self.MAIN
		while True:
			# main loop
			print ""
			if menu == self.MAIN:
				print "You have %s show(s) in your configuration." % len(self.shows)
				print "Please select an option:"
				p = self.menu([("SHOW", "Select a show to watch%s" % (" (disabled)" if len(self.shows)==0 else "")),
					("ADD", "Add shows"),
					("RSS", "Check RSS feeds"),
					("SETTINGS", "Settings")], "SHOW")
				if p == "SHOW":
					if len(self.shows) == 0:
						print "No shows available, please add some."
					else:
						menu = self.SHOWS
				elif p == "ADD":
					menu = self.ADDSHOWS
				elif p == "RSS":
					menu = self.RSS
				elif p == "SETTINGS":
					menu = self.SETTINGS
			elif menu == self.SHOWS:
				print "Select show:"
				i = 0
				for show in self.shows:
					i += 1
					print "%s: %s (%s left)" % (i, show, self.get_episodes_left(self.c.showdata[show]))
				p = self.i("Option: ", True)
				if p == "RETURN":
					menu = self.MAIN
				else:
					try:
						s = self.shows[int(p)-1]
						self.set_currentshow(s)
						menu = self.SHOW
					except IndexError:
						print "Ununderstood option."
						continue
					except ValueError:
						continue
					except TypeError:
						continue
			elif menu == self.SHOW:
				print "Selected `%s'..." % self.currentshow
				try:
					curep = self.c.showdata[self.currentshow]['currentepisode']
				except:
					self.c.showdata[self.currentshow]['currentepisode'] = (1, 1)
					curep = (1, 1)
				try:
					tep = self.c.showdata[self.currentshow]['episodes'][curep[0]][curep[1]]
				except KeyError:
					while True:
						curep = (curep[0], curep[1]-1)
						if curep[1] < 1:
							curep = (curep[0]-1, 1)
						if curep[0] < 1:
							tep = None
							break
						try:
							tep = self.c.showdata[self.currentshow]['episodes'][curep[0]][curep[1]]
							break
						except KeyError:
							continue
				if tep != None:
					t = tep.split("/")
					t = t[len(t)-1]
					print "Current episode: S%sE%s: %s" % (self.z(curep[0]), self.z(curep[1]), t)
					p = self.menu([("WATCH", "Watch current episode"),
						("CWATCH", "Continuesly watch without prompt (crash mplayer to stop)"),
						("ADD", "Add more/new episodes"),
						("BROWSE", "Browse show's files"),
						("MPLAYER", "MPlayer settings")], "WATCH")
					if p == "WATCH":
						self.watch(curep)
					elif p == "CWATCH":
						self.cwatch(curep)
					elif p == "ADD":
						self.c.showdata[self.currentshow] = self.add_files(self.currentshow, self.c.showdata[self.currentshow], True)
					elif p == "BROWSE":
						self.browse_show(self.currentshow)
					elif p == "MPLAYER":
						try:
							settings = self.c.showdata[self.currentshow]['mplayersettings']
						except:
							settings = ''
							self.c.showdata[self.currentshow].update({'mplayersettings':''})
						print ""
						print "Set mplayer settings for `%s':" % self.c.showdata[self.currentshow]['title']
						print settings
						print "Hit enter to make no chance; space and enter to clear."
						p = self.i(": ")
						if p != '':
							self.c.showdata[self.currentshow]['mplayersettings'] = p
					elif p == "RETURN":
						menu = self.SHOWS
					elif p == "TOP":
						menu = self.MAIN
				else:
					menu = self.SHOWS
			elif menu == self.ADDSHOWS:
				self.add_show()
				menu = self.MAIN
			elif menu == self.RSS:
				self.rssmenu()
				menu = self.MAIN
			elif menu == self.SETTINGS:
				print "Select settings to edit."
				p = self.menu([("MPLAYER", "mplayer options")], None)
				if p == "MPLAYER":
					print "Please write on one line, the options to pass to mplayer:"
					print "Current options: %s" % self.mplayerconfig
					print "Hit enter to make no chance; space and enter to clear."
					c = self.i(": ")
					if c != '':
						self.c.mplayerconfig = c
						self.c.showdata[0]['mplayerconfig'] = c
						print "Set mplayer option to: %s" % c
				elif p == "RETURN":
					menu = self.MAIN
	
	def next_episode(self, episodes, current):
		if current[0] > len(episodes):
			try:
				return (current[0]-1, len(episodes[current[1]])-1)
			except KeyError:
				return (1,1)
		try:
			t = episodes[current[0]][current[1]+1]
			return (current[0], current[1]+1)
		except:
			return self.next_episode(episodes, (current[0]+1, 0))
				
	def i(self, msg, anoption=False):
		try:
			p = raw_input(msg)
		except EOFError:
			print ""
			self.c.save()
			print "Quit."
			sys.exit()
		except KeyboardInterrupt:
			return None
		if p == ":quit" or p == ":q":
			self.c.save()
			print "Quit."
			sys.exit()
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
		self.c.autosave()
		self.rsscheck()
		return p
	
	def z(self, i):
		if i < 10:
			return "0%s" % i
		return i
	
	def dataerror(self):
		print "Data error.  Please run script with -f"
	
	def save(self):
		self.c.save()

	def __init__(self):
		parser = OptionParser()
		parser.add_option("-f", "--fix", dest="fix",
			action="store_true", help="Fix the configuration file if it contains error.")
		parser.add_option("-e", "--empty", dest="empty",
			action="store_true", help="Empty configuration file (not implemented).")
		(options, args) = parser.parse_args()
		self.c = Config()
		if options.empty:
			print "Not implemented."
			#self.empty()
		if options.fix:
			self.c.fix_config()
		self.run()

Marathon()
