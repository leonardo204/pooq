# -*- coding: utf-8 -*-
#__author__ = "Dong-gyun Ham"
#__email__ = "irow14@gmail.com"


import urllib, urllib2, cookielib
import os
#import xbmc, xbmcaddon
import json
from io import open

#__profile__ = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
CREDENTIALDATA = os.path.join( os.getcwd(), 'credential.dat')
LOCAL_PROGRAM_LIST = os.path.join( os.getcwd(), 'programlist.txt')


class Client( object ):
	def __init__( self, cookie=None ):
		self.MyCookie = cookielib.LWPCookieJar()
		self.MyCookieFile = cookie
		if self.MyCookieFile:
			try:
				self.MyCookie.load( self.MyCookieFile, ignore_discard=True )
			except:
				pass
		self.Opener = urllib2.build_opener( urllib2.HTTPCookieProcessor(self.MyCookie) )
		self.Opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7')]
		urllib2.install_opener(self.Opener)

	def AddHeaders( self, headers ):
		self.Opener.addheaders = headers

	def Request( self, url, postdata=None ):
		#print "::Request - url: %s" % url
		if postdata:
			req = self.Opener.open( url, postdata )
		else:
			req = self.Opener.open( url )
		response = req.read()
		req.close()
		return response

	def ClearCookie( self ):
		self.MyCookie.clear()

	def SaveCookie( self ):
		self.MyCookie.save( self.MyCookieFile, ignore_discard=True )

	def Login( self, url, data=None ):
		self.ClearCookie()
		req = self.Opener.open( url, data )
		data = req.read()
		req.close()
		self.SaveCookie()
		return data
		

class Pooq( object ):
	def __init__( self ):
		self.API_DOMAIN = 'http://wapie.pooq.co.kr/'
		self.DEVICE_TYPE_ID = 'pc'
		self.MARKET_TYPE_ID = 'generic'
		self.DEVICE_MODEL_ID = 'none'
		self.DRM = 'WC'
		self.COUNTRY = 'KOR'
		self.API_ACCESS_CREDENTIAL = 'EEBE901F80B3A4C4E5322D58110BE95C'
		self.LIMIT = 30
		self.CLIENT = Client()

	def GetApiAccessCredential( self ):
		apiAccessCredential = ''
		try:
			url = 'http://www.pooq.co.kr/js/core.js'
			req = self.CLIENT.Request( url )
			aac_tmp = re.search(r'([A-F0-9]{32})', req)
			if aac_tmp: apiAccessCredential = aac_tmp.group()
		except:
			pass
		return apiAccessCredential

	def GetCredential( self, user_id, user_pw ):
		#Log('GetCredential START: %s %s' % (user_id, user_pw))
		e = 'Log'
		isLogin = False
		try:
			url_path = 'v1/login30/'
			params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
					   'marketTypeId' : self.MARKET_TYPE_ID,
					   'apiAccessCredential' : self.API_ACCESS_CREDENTIAL,
					   'drm' : self.DRM,
					   'country' : self.COUNTRY,
					   'credential' : 'none',
					   'mode' : 'id',
					   'id' : user_id,
					   'password' : user_pw }
			url = self.MakePooqServiceUrl( url_path, params )
			req = self.CLIENT.Request( url, ' ' )
			req_json = json.loads( req )
			credential = req_json['result']['credential']
			if credential: isLogin = True
		except Exception as e:
			Log('GetCredential Exception %s' % e)
			credential = 'none'
		Log('CREDENTIALDATA %s' % CREDENTIALDATA)
		Log('CREDENTIALDATA %s' % credential)
		write_file( CREDENTIALDATA, credential )
		return (isLogin, e)


	def GetGUID( self ):
		import hashlib
		m = hashlib.md5()

		def GenerateID( media ):
			from datetime import datetime
			requesttime = datetime.now().strftime('%Y%m%d%H%M%S')
			randomstr = GenerateRandomString(5)
			uuid = randomstr + media + requesttime
			return uuid

		def GenerateRandomString( num ):
			from random import randint
			rstr = ""
			for i in range(0,num):
				s = str(randint(1,5))
				rstr += s
			return rstr

		uuid = GenerateID("POOQ")
		m.update(uuid)

		return str(m.hexdigest())


	def GetLiveList( self ):
		try:
			url_path = 'v1/lives30/'
			params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
					   'marketTypeId' : self.MARKET_TYPE_ID,
					   'apiAccessCredential' : self.API_ACCESS_CREDENTIAL,
					   'deviceModelId' : self.DEVICE_MODEL_ID,
					   'drm' : self.DRM,
					   'country' : self.COUNTRY,
					   'offset' : 0,
					   'limit' : 100,
					   'orderby' : 'g', #'h',
					   'mode' : 'all',
					   'genere' : 'all',
					   'credential' : 'none' }
			url = self.MakePooqServiceUrl( url_path, params )
			req = self.CLIENT.Request( url )
			req_json = json.loads( req )
			result = req_json['result']['list']
			
		except:
			result = []
		return result


	def GetLiveListGeneresort( self ):
		try:
			url_path = 'v1/livesgenresort30/'
			params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
					   'marketTypeId' : self.MARKET_TYPE_ID,
					   'apiAccessCredential' : self.API_ACCESS_CREDENTIAL,
					   'drm' : self.DRM,
					   'country' : self.COUNTRY,
					   'authType' : 'cookie',
					   'orderby' : 'g', #'h',
					   'credential' : 'none' }
			url = self.MakePooqServiceUrl( url_path, params )
			req = self.CLIENT.Request( url )
			req_json = json.loads( req )
			result = req_json['result']['list']
			#Log('POOQ GetLiveListGeneresort URL: %s' % url)
		except Exception as e:
			Log('GetLiveListGeneresort Exception %s' % e)
			result = []
		return result


	def GetLiveInfo( self, channelID ):
		try:
			url_path = 'v1/lives30/%s' % channelID
			params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
					   'marketTypeId' : self.MARKET_TYPE_ID,
					   'apiAccessCredential' : self.API_ACCESS_CREDENTIAL,
					   'drm' : self.DRM,
					   'country' : self.COUNTRY,
					   'credential' : 'none' }
			url = self.MakePooqServiceUrl( url_path, params )
			req = self.CLIENT.Request( url )
			req_json = json.loads( req )
			result = req_json['result']
		except:
			result = None
		return result


	def GetLiveStreamUrl( self, channelID, quality ):
		result = None
		#credential = load_file( CREDENTIALDATA )
		credential = 'none' #안드로이드(핸드폰)에서 이용권상태에서는 안나와버린다
		isPreview = None
		surl = None
		try:
			url_path = 'v1/lives30/%s/url' % channelID
			params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
					   'marketTypeId' : self.MARKET_TYPE_ID,
					   'deviceModelId' : 'Macintosh',
					   'drm' : self.DRM,
					   'country' : self.COUNTRY,
					   'authType' : 'cookie',
					   'guid' : self.GetGUID(),
					   'lastPlayId' : 'none',
					   'credential' : credential,
					   'quality' : quality }
			url = self.MakePooqServiceUrl( url_path, params )
			req = self.CLIENT.Request( url )
			req_json = json.loads( req )
			surl = req_json['result']['signedUrl']
			if req_json['result']['isPreview'] == "Y": isPreview = True
			else: isPreview = False
			
		except Exception as e:
			Log('GetLiveStreamUrl Exception: %s' % e)
			pass
		#Log('isPreview %s' % isPreview)
		#Log('surl %s' % surl)
		return (isPreview, surl)

	def Search( self, vod_type, keyword, pageNo=1 ):
		try:
			url_path = 'v1/search30/%s/' % vod_type
			limit = (self.LIMIT * 10)
			offset = (pageNo - 1) * limit
			#kwd = urllib.quote_plus(keyword)
			params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
					   'marketTypeId' : self.MARKET_TYPE_ID,
					   'apiAccessCredential' : self.API_ACCESS_CREDENTIAL,
					   'drm' : self.DRM,
					   'country' : self.COUNTRY,
					   'offset' : offset,
					   'limit' : limit,
					   'orderby' : 'C',
					   'query' : keyword }
			url = self.MakePooqServiceUrl( url_path, params )
			req = self.CLIENT.Request( url )
			req_json = json.loads( req )
			#result = req_json['result']['list']
			result = req_json['result']
		except:
			result = []
		return result

	def GetVODGenres( self ):
		try:
			url_path = 'v1/vodgenres30/'
			params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
					   'marketTypeId' : self.MARKET_TYPE_ID,
					   'apiAccessCredential' : self.API_ACCESS_CREDENTIAL,
					   'key' : 'vodGenreList' }
			url = self.MakePooqServiceUrl( url_path, params )
			req = self.CLIENT.Request( url )
			req_json = json.loads( req )
			result = req_json['result']['list']
		except:
			result = []
		return result

	def GetVODList( self, genre, cate, pageNo ):
		try:
			url_path = 'v1/vods30/%s/' % genre
			offset = (pageNo - 1) * self.LIMIT
			params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
					   'marketTypeId' : self.MARKET_TYPE_ID,
					   'apiAccessCredential' : self.API_ACCESS_CREDENTIAL,
					   'offset' : offset,
					   'limit' : self.LIMIT,
					   'orderby' : cate,
					   'isFree' : 'all',
					   'channelId' : 'ANY' }
			url = self.MakePooqServiceUrl( url_path, params )
			req = self.CLIENT.Request( url )
			req_json = json.loads( req )
			#result = req_json['result']['list']
			result = req_json['result']
		except:
			result = []
		return result

	def GetVODInfo( self, programid, itemid, cornerid ):
		#Log('GetVODInfo START: %s %s %s' % (programid, itemid, cornerid))
		try:
			url_path = 'v1/vods30/all/%s/%s/%s' % ( programid, itemid, cornerid )
			params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
					   'marketTypeId' : self.MARKET_TYPE_ID,
					   'apiAccessCredential' : self.API_ACCESS_CREDENTIAL,
					   'drm' : self.DRM,
					   'country' : self.COUNTRY,
					   'credential' : 'none',
					   'programId' : programid }
			url = self.MakePooqServiceUrl( url_path, params )
			req = self.CLIENT.Request( url )
			req_json = json.loads( req )
			result = req_json['result']
			#Log('GetVODInfo URL: RES: %s REQ: %s' % (url,req_json) )
		except:
			result = None
		return result

	def GetMovieGenres( self ):
		try:
			url_path = 'v1/moviefilter30/'
			params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
					   'marketTypeId' : self.MARKET_TYPE_ID,
					   'apiAccessCredential' : self.API_ACCESS_CREDENTIAL,
					   'drm' : self.DRM,
					   'country' : self.COUNTRY }
			url = self.MakePooqServiceUrl( url_path, params )
			req = self.CLIENT.Request( url )
			req_json = json.loads( req )
			result = req_json['result']['genreList']
		except:
			result = []
		return result



	def GetMovieList( self, genre, cate, pageNo=1 ):
		try:
			url_path = ''
			params = {}
			offset = (pageNo - 1) * self.LIMIT
			if genre == 'recommend':
				url_path = 'v1/movies30/'
				params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
						   'marketTypeId' : self.MARKET_TYPE_ID,
						   'apiAccessCredential' : self.API_ACCESS_CREDENTIAL,
						   'drm' : self.DRM,
						   'country' : self.COUNTRY,
						   'offset' : offset,
						   'limit' : self.LIMIT,
						   'genreCode' : 'all',
						   'isDrm' : 'all' }
			elif genre == 'playy':
				url_path = 'v1/movieThemes30/10000/'
				params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
						   'marketTypeId' : self.MARKET_TYPE_ID,
						   'apiAccessCredential' : self.API_ACCESS_CREDENTIAL,
						   'drm' : self.DRM,
						   'country' : self.COUNTRY,
						   'offset' : offset,
						   'limit' : self.LIMIT,
						   'orderby' : cate,
						   'genreCode' : 'all',
						   'isFree' : 'all',
						   'isAdult' : 'auto',
						   'nationalCode' : 'all',
						   'isDrm' : 'all' }
			else:
				url_path = 'v1/movies30/%s/' % genre
				params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
						   'marketTypeId' : self.MARKET_TYPE_ID,
						   'apiAccessCredential' : self.API_ACCESS_CREDENTIAL,
						   'drm' : self.DRM,
						   'country' : self.COUNTRY,
						   'offset' : offset,
						   'limit' : self.LIMIT,
						   'orderby' : cate,
						   'isFree' : 'all',
						   'isAdult' : 'auto',
						   'nationalCode' : 'all',
						   'isDrm' : 'all' }
			url = self.MakePooqServiceUrl( url_path, params )
			req = self.CLIENT.Request( url )
			req_json = json.loads( req )
			#result = req_json['result']['list']
			result = req_json['result']
		except:
			result = []
		return result

	def GetMovieInfo( self, itemid ):
		try:
			url_path = 'v1/movies/all/%s' % itemid
			params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
					   'screenTypeId' : 'pc',
					   'marketTypeId' : self.MARKET_TYPE_ID,
					   'apiAccessCredential' : self.API_ACCESS_CREDENTIAL,
					   'drm' : self.DRM,
					   'country' : self.COUNTRY,
					   'credential' : 'none' }
			url = self.MakePooqServiceUrl( url_path, params )
			req = self.CLIENT.Request( url )
			req_json = json.loads( req )
			result = req_json['result']

		except:
			result = None
		return result

	def GetVODStreamUrl( self, vod_type, itemid, cornerid, quality ):
		#Log('POOQ GetVODStreamUrl: vod_type:%s itemid:%s cornerid:%s quality%s' % (vod_type, itemid, cornerid, quality))
		result = None
		isPreview = True
		credential = load_file( CREDENTIALDATA )
		
		try:
			message = ''
			url_path = 'v1/permission30'
			params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
					   'marketTypeId' : self.MARKET_TYPE_ID,
					   'deviceModelId' : 'Macintosh',
					   'drm' : self.DRM,
					   'country' : self.COUNTRY,
					   'authType' : 'cookie',
					   'guid' : self.GetGUID(),
					   'lastPlayId' : 'none',
					   'credential' : credential,
					   'quality' : quality,
					   'type' : vod_type,
					   'cornerId' : cornerid,
					   'id' : itemid,
					   'action' : 'stream' }
			url = self.MakePooqServiceUrl( url_path, params )
			
			req = self.CLIENT.Request( url )
			req_json = json.loads( req )
			#Log('GetVODStreamUrl URL: %s' % url)
			#Log('GetVODStreamUrl: %s' % req_json)
			#Log('GetVODStreamUrl MESSAGE: %s' % unicode(req_json['message']))
			message = unicode(req_json['message'])
			surl = req_json['result']['signedUrl']
			if req_json['result']['isPreview'] == "Y": isPreview = True
			else: isPreview = False
			savedata = '|'.join([isPreview, surl, message])
			write_file(Client.Product, savedata)

		except Exception as e:
			Log('GetVODStreamUrl Exception: %s' % e)
			pass
		return (isPreview, surl, message)

	##################################### 프로그램
	def GetProgramInfo( self, programid):
		#Log('GetProgramInfo START: %s' % programid)
		try:
			url_path = 'v1/programs30/all/'
			params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
					   'marketTypeId' : self.MARKET_TYPE_ID,
					   'apiAccessCredential' : self.API_ACCESS_CREDENTIAL,
					   'drm' : self.DRM,
					   'country' : self.COUNTRY,
					   'credential' : 'none',
					   'programId' : programid }
			url = self.MakePooqServiceUrl( url_path, params )
			req = self.CLIENT.Request( url )
			req_json = json.loads( req )
			result = req_json['result']
		except:
			result = None
		return result

	#################################
	def GetEpisodeList( self, channelId, programId, pageNo ):
		try:
			url_path = 'v1/vods30/%s/%s' % (channelId, programId)
			offset = (pageNo - 1) * self.LIMIT
			params = { 'deviceTypeId' : self.DEVICE_TYPE_ID,
					   'marketTypeId' : self.MARKET_TYPE_ID,
					   'apiAccessCredential' : self.API_ACCESS_CREDENTIAL,
					   'credential' : 'none',
					   'offset' : offset,
					   'limit' : self.LIMIT,
					   'orderby' : 'D',
					   'isFree' : 'all',
					   'dummy' : '' }
			url = self.MakePooqServiceUrl( url_path, params )
			req = self.CLIENT.Request( url )
			req_json = json.loads( req )
			#Log('GetEpisodeList RES:%s REQ:%s' % (url, req_json))
			#result = req_json['result']['list']
			result = req_json['result']
		except Exception as e:
			Log('GetEpisodeList Exception: %s' % e)
			result = []
		return result


	
	
	#################################
	def LoadProgramList( self ):
		try:
			f = open(LOCAL_PROGRAM_LIST, 'r', encoding='utf-8')
			result = f.readlines()
			f.close()
			return result
		except Exception as e:
			Log('LoadProgramList Exception: %s' % e)
			result = []
		return result



	#################################
	def SaveProgramList( self, data ):
		try:
			result = self.LoadProgramList()
			with open(LOCAL_PROGRAM_LIST, 'w', encoding='utf-8') as fw:
				data = unicode(data + '\n')
				fw.write(data)
				num = 1
				for line in result:
					if not line.startswith(data.split('|')[0]): 
						fw.write(line)
						num += 1
					if num == 100: break

		except Exception as e:
			Log('SaveProgramList Exception: %s' % e)
			pass
		return



	def MakePooqServiceUrl( self, path, params ):
		return makeurl( self.API_DOMAIN, path, urllib.urlencode( params ) )

	

def makeurl( domain, path, query=None ):
	import re
	url = ''
	if domain:
		if re.search(r'http[s]*://', domain): url += domain
		else: url += 'http://%s' % domain
		if path: 
			url += path
			if query: url += '?%s' % query
	return url


def load_file( filename ):
	try:
		with open(filename, "r", encoding='utf-8') as f:
			data = f.read()
		f.close()
	except:
		data = None
	return data


def write_file( filename, data ):
	try:
		with open(filename, "w", encoding='utf-8') as f:
			#f.write( str(data) )
			f.write( unicode(data) )
		f.close()
	except Exception, e:
		Log('Error1 write_file %s ' %  e)
		pass
		

