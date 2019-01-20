from pooqCore import Pooq
from pooqCore import load_file
from pooqCore import write_file
import os
import time

NAME = 'pooq'
PREFIX = '/video/pooq'
ICON = 'icon-default.jpg'

####################################################################################################
def Start():
    ObjectContainer.title1 = NAME
    DirectoryObject.thumb = R(ICON)
    HTTP.CacheTime = CACHE_1HOUR


####################################################################################################
@handler(PREFIX, NAME, thumb=ICON)
def MainMenu(no_history=False, randomize=None):
	Log.Info('MainMenu: {} {}: {}'.format(randomize, Client.Product, Request.Method))
	Log.Info('    X-Plex-Container-Size: {}'.format(Request.Headers.get('X-Plex-Container-Size')))
	Log.Info('    X-Plex-Container-Start: {}'.format(Request.Headers.get('X-Plex-Container-Start')))
	oc = ObjectContainer()
	(pooq_id, pooq_pw) = get_settings_login_info()
	if pooq_id is None or pooq_pw is None:
		message = unicode('아이디/암호를 입력하세요                    ')
		oc.add(DirectoryObject(key = Callback(Label, message=message), title = message))
	else:
		(isLogin, e) = Pooq().GetCredential( pooq_id, pooq_pw )
		if not isLogin:
			message = unicode('로그인 실패')
			oc.add(DirectoryObject(key = Callback(Label, message=message), title = message))
			message = str(e)
			oc.add(DirectoryObject(key = Callback(Label, message=message), title = message))
		else:
			oc.add(DirectoryObject(key = Callback(Live, title=unicode('실시간 TV')), title = unicode('실시간 TV')))
			oc.add(DirectoryObject(key = Callback(VODCateList, type='VOD', title = unicode('방송 VOD')), title = unicode('방송 VOD')))
			oc.add(DirectoryObject(key = Callback(ProgramList, title = unicode('Watched')), title = unicode('Watched')))
			oc.add(DirectoryObject(key = Callback(VODCateList, type='Movie', title = unicode('영화')), title = unicode('영화')))

	return oc

####################################################################################################
@route(PREFIX + '/live')
def Live(title):
	oc = ObjectContainer(title2 = unicode(title))
	try:
		items = Pooq().GetLiveListGeneresort()

		for lists in items:
			for item in lists['list']:
				info = getInfo('Live',item)
				oc.add(DirectoryObject(
					key = Callback(LiveList, title=info['title'], subtitle=info['subtitle'], id=item['id'], img=info['img'], quality=info['quality'], isRadio=info['isRadio'], plot=info['plot']),
					title = unicode(info['title']),
					summary = unicode('['  + info['subtitle'] + ']' +info['plot']),
					thumb = Resource.ContentsOfURLWithFallback(info['img'])
				))
	except Exception as e:
		Log('init Live Exception: %s' % e)
		pass
	if len(oc) == 0:
		message = 'Empty'
		oc.add(DirectoryObject(key = Callback(Label, message=message), title = unicode(message)))
	return oc


####################################################################################################퀄리티 선택
@route(PREFIX + '/livelist')
def LiveList(title, subtitle, id, img, quality, isRadio, plot):
	oc = ObjectContainer(title2 = unicode(title))
	try:
		qualitys = quality.split('|')

		for quality in qualitys:
			(isPreview, surl) = Pooq().GetLiveStreamUrl(id, quality)
			if surl is not None:
				Log('LiveList %s' % surl)
				summary = unicode(subtitle)
				if Prefs['url_show'] == True: summary = summary + '\n' + surl
				#if isRadio == 'Y' and Client.Platform in ('Chrome', 'Firefox', 'Edge', 'Safari', 'Internet Explorer'):
				#if isRadio == 'Y' and Client.Platform in ('Chrome', 'Firefox'):
				#if isRadio == 'Y' and Client.Product == 'Plex Web':
				if isRadio == 'Y' and Client.Product != 'Plex for iOS':
					oc.add(CreateTrackObject(file_url=surl, title=unicode(title), summary=summary,  thumb=Resource.ContentsOfURLWithFallback(img)))
				else:
					oc.add(
						CreateVideoClipObject(
							url = surl,
							title = unicode(title + ' [' + quality) + ']',
							thumb = Resource.ContentsOfURLWithFallback(img),
							art = R('art-default.png'),
							summary = summary,
							include_container = False,
							c_protocol = 'hls',
							c_container = 'mpegts',
							c_video_codec = VideoCodec.H264,
							c_audio_codec = AudioCodec.AAC
						)
					)
	except Exception as e:
		Log('init LiveList Exception: %s' % e)
		pass
	if len(oc) == 0:
		message = 'Empty'
		oc.add(DirectoryObject(key = Callback(Label, message=message), title = unicode(message)))
	return oc


####################################################################################################
@route(PREFIX + '/vodcatelist')
def VODCateList(title, type):
	oc = ObjectContainer(title2 = unicode(title))
	try:
		if type == 'VOD':
			genres = Pooq().GetVODGenres()
			oc.add(DirectoryObject(key = Callback(VODList, type=type, ctitle='최신', genre='all', order='d', pageNo=1),title = unicode('최신')))
			oc.add(DirectoryObject(key = Callback(VODList, type=type, ctitle='인기', genre='all', order='h', pageNo=1),title = unicode('인기')))
			for item in genres:
				title = item['genreTitle'].encode('utf-8')
				genre = item['genreCode']
				oc.add(DirectoryObject(
					key = Callback(VODList, type=type, ctitle=title, genre=genre, order='h', pageNo=1),
					title = unicode(title),
				))
		else: 
			genres = Pooq().GetMovieGenres()
			oc.add(DirectoryObject(key = Callback(VODList, type=type, ctitle='PLAYY 업데이트순', genre='playy', order='d', pageNo=1),title = unicode('PLAYY 업데이트순')))
			oc.add(DirectoryObject(key = Callback(VODList, type=type, ctitle='PLAYY 개봉일순', genre='playy', order='r', pageNo=1),title = unicode('PLAYY 개봉일순')))
			oc.add(DirectoryObject(key = Callback(VODList, type=type, ctitle='PLAYY 인기순', genre='playy', order='h', pageNo=1),title = unicode('PLAYY 인기순')))
			oc.add(DirectoryObject(key = Callback(VODList, type=type, ctitle='추천', genre='recommend', order='', pageNo=1),title = unicode('추천')))
			oc.add(DirectoryObject(key = Callback(VODList, type=type, ctitle='인기', genre='all', order='h', pageNo=1),title = unicode('인기')))
			oc.add(DirectoryObject(key = Callback(VODList, type=type, ctitle='최신 개봉일순', genre='all', order='r', pageNo=1),title = unicode('최신 개봉일순')))
			oc.add(DirectoryObject(key = Callback(VODList, type=type, ctitle='최신 업데이트순', genre='all', order='d', pageNo=1),title = unicode('최신 업데이트순')))
			for item in genres:
				titme = ''
				title = item['genreName'].encode('utf-8')
				genre = item['genreCode']
				oc.add(DirectoryObject(
					key = Callback(VODList, type=type, ctitle=title, genre=genre, order='d', pageNo=1),
					title = unicode(title),
				))
	except Exception as e:
		Log('init VODCateList Exception: %s' % e)
		pass
	if len(oc) == 0:
		message = 'Empty'
		oc.add(DirectoryObject(key = Callback(Label, message=message), title = unicode(message)))
	return oc


####################################################################################################
@route(PREFIX + '/vodlist')
def VODList(type, ctitle, genre, order, pageNo):
	oc = ObjectContainer(title2 = unicode(ctitle + ' ' +pageNo +' 페이지'))
	try:
		if type == 'VOD':
			items = Pooq().GetVODList(genre, order, int(pageNo))
			count = int(items['count'])
			has_more = 'Y' if count > 30 else 'N'
			for item in items['list']:
				info = getInfo('VOD',item)
				pgm_nm = info['tvshowtitle']
				freq = info['episode']
				if freq: title = '%s %s회' % (pgm_nm, freq)
				else: title = pgm_nm
				isQvod = (item['isQvod'] == 'Y')
				if item['isFree'] == 'Y': title = '[무료]'+title
				oc.add(DirectoryObject(
					#key = Callback(VODQuality, type=type, title=title, programId=info['programId'], contentId=info['id'],  cornerId=info['cornerId'], img=info['img'], plot=info['plot'], isQvod=isQvod),
					key = Callback(EpisodeList, programId=info['programId'], pageNo=1),
					title = unicode(title),
					summary = unicode(info['plot']),
					thumb = Resource.ContentsOfURLWithFallback(info['img'])
				))
		else:
			items = Pooq().GetMovieList(genre, order, int(pageNo))
			count = int(items['count'])
			has_more = 'Y' if count > (30*int(pageNo)) else 'N'
			for item in items['list']:
				info = getInfo('Movie',item)
				oc.add(DirectoryObject(
					key = Callback(VODQuality, type=type, title=info['title'], programId=info['programId'], contentId=info['id'],  cornerId='1', img=info['img'], plot=info['plot'], isQvod=False),
					
					title = unicode(info['title']),
					summary = unicode(info['plot']),
					thumb = Resource.ContentsOfURLWithFallback(info['img'])
				))
		if pageNo != '1':
			oc.add(DirectoryObject(
				key = Callback(VODList, type=type, ctitle=ctitle, genre=genre, order=order, pageNo=str(int(pageNo)-1)),
				title = unicode('<< 이전 페이지')
			))
		if has_more == 'Y':
			oc.add(DirectoryObject(
				key = Callback(VODList, type=type, ctitle=ctitle, genre=genre, order=order, pageNo=str(int(pageNo)+1)),
				title = unicode('다음 페이지 >>')
			))
	except Exception as e:
		Log('init VODList Exception: %s' % e)
		pass
	if len(oc) == 0:
		message = 'Empty'
		oc.add(DirectoryObject(key = Callback(Label, message=message), title = unicode(message)))
	return oc


####################################################################################################퀄리티 선택
@route(PREFIX + '/vodquality')
def VODQuality(type, title, programId, contentId, cornerId, img, plot, isQvod):
	oc = ObjectContainer(title2 = unicode(title))
	try:
		if type == 'VOD':
			result = Pooq().GetVODInfo(programId, contentId, cornerId)
			if result is not None:
				qualitys = result['resolutions'][0]['resolution']
				for quality in qualitys:
					title2 = title
					oc.add(DirectoryObject( key = Callback(VODGetUrl, type=type, title=title, programId=programId, contentId=contentId, cornerId=cornerId, img=img, plot=plot, quality=quality, isQvod=isQvod), title = unicode(quality)))
				#방송
				oc.add(DirectoryObject( key = Callback(EpisodeList, programId=programId, pageNo=1), title = unicode('방송 프로그램으로 이동')))
		else:
			result = Pooq().GetMovieInfo(contentId)
			if result is None: return oc
			qualitys = result['resolutions'][0]['resolution']
			for quality in qualitys:
				title2 = title
				oc.add(DirectoryObject( key = Callback(VODGetUrl, type=type, title=title, programId=programId, contentId=contentId, cornerId=cornerId, img=img, plot=plot, quality=quality, isQvod=False), title = unicode(quality)))
	except Exception as e:
		Log('init VODQuality Exception: %s' % e)
		pass
	if len(oc) == 0:
		message = 'Empty'
		oc.add(DirectoryObject(key = Callback(Label, message=message), title = unicode(message)))
	return oc


####################################################################################################Steam URL
@route(PREFIX + '/vodgeturl')
def VODGetUrl(type, title, programId, contentId, cornerId, img, plot, quality, isQvod):
	Log.Info('VODGetUrl: {}: {}'.format(Client.Product, Request.Method))
	Log.Info('    X-Plex-Container-Size: {}'.format(Request.Headers.get('X-Plex-Container-Size')))
	Log.Info('    X-Plex-Container-Start: {}'.format(Request.Headers.get('X-Plex-Container-Start')))
	Log('CLIENT %s' % Client.Product)
	Log('CLIENT %s' % Client.Platform)
	#if Client.Product in ['Plex for Android', 'Plex Home Theater'] and ('X-Plex-Container-Size' not in Request.Headers and
        #    'X-Plex-Container-Start' not in Request.Headers):
	#	Log.Info('SKIPPING REQUEST')
	#	oc = ObjectContainer(title2 = unicode(title))
	#	oc.add(DirectoryObject(key = Callback(Label, message=None), title = None))
	#	return oc
	#if Request.Headers.get('X-Plex-Container-Size') is not None and Request.Headers.get('X-Plex-Container-Start') is not None:
	#	Log.Info('SKIPPING REQUEST')
	#	oc = ObjectContainer(title2 = unicode(title))
	#	oc.add(DirectoryObject(key = Callback(Label, message=None), title = None))
	#	return oc

	oc = ObjectContainer(title2 = unicode(title))
	try:
		if type == 'VOD' :
			result = Pooq().GetVODInfo(programId, contentId, cornerId)
			summary = plot
		else:
			programId = None
			result = Pooq().GetMovieInfo(contentId)
			summary = result['description'] + '\n장르 : ' + result['genere'] + '\n평점 : ' + result['rating'] + '\n재생시간 : ' + result['runningTime'] + '\n개봉일자 : ' + result['releaseDate'] + '\n장르 : ' + result['genere'] + '\n연령 : ' + result['ageRestriction'] + '\n국가 : ' + result['nation'] + '\n감독 : ' + result['director'] + '\n출연자 : ' + result['starling']
		summary = unicode(summary)
		if result is None: return oc
		vod_type = type
		if isQvod == 'True': vod_type = 'qvod'
		
		filename = os.path.join( os.getcwd(), Client.Product + '.txt')
		if os.path.isfile(filename) and os.path.getctime(filename) > time.time()-3 and Request.Headers.get('X-Plex-Container-Size') is not None and Request.Headers.get('X-Plex-Container-Start') is not None:
			ctime = os.path.getctime(filename)
			Log('CTIME : %s' % ctime)
			savedata = load_file(filename).split('|')
			isPreview = True if savedata[0] == 'True' else False
			surl = savedata[1]
			message = savedata[1]
		else:
			(isPreview, surl, message) = Pooq().GetVODStreamUrl(vod_type, contentId, cornerId, quality)
			if os.path.isfile(filename): os.remove(filename)
			if surl is not None:
				savedata = '|'.join([str(isPreview), surl, message])
				write_file(filename, savedata)
		
		if surl is not None:
			title2 = title
			if isPreview == True: title2 = '[미리보기]' + title
			
			if Prefs['url_show'] == True: summary = summary + '\n' + surl
			oc.add(
				CreateVideoClipObject(
					url = surl,
					title = unicode(title2 + ' [' + quality) + ']',
					thumb = Resource.ContentsOfURLWithFallback(img),
					art = R('art-default.png'),
					summary = summary,
					include_container = False,
					programId = programId,
					c_protocol = 'hls',
					c_container = Container.MP4,
					c_video_codec = VideoCodec.H264,
					c_audio_codec = AudioCodec.AAC
				)
			)
		if len(oc) == 0:
			oc.add(DirectoryObject(
				key = Callback(Label, message=message),
				title = unicode(message)
			))
		Log('VODGetUrl %s %s %s' % (isPreview, surl, message))
	except Exception as e:
		Log('init VODGetUrl Exception: %s' % e)
		pass
	if len(oc) == 0:
		message = 'Empty'
		oc.add(DirectoryObject(key = Callback(Label, message=message), title = unicode(message)))
	return oc


####################################################################################################
@route(PREFIX + '/programlist')
def ProgramList(title):
	oc = ObjectContainer(title2 = unicode(title))
	try:
		items = Pooq().LoadProgramList()
		for item in items:
			data = item.split('|')
			oc.add(DirectoryObject(
				key = Callback(EpisodeList, programId=data[0], pageNo='1', channelId=data[1], programTitle=unicode(data[2])),
				title = unicode(data[2]),
				thumb = Resource.ContentsOfURLWithFallback(data[3])
			))
	except Exception as e:
		Log('init ProgramList Exception: %s' % e)
		pass
	if len(oc) == 0:
		message = 'Empty'
		oc.add(DirectoryObject(key = Callback(Label, message=message), title = unicode(message)))
	return oc


####################################################################################################방송프로그램
@route(PREFIX + '/episodelist')
def EpisodeList(programId, pageNo, channelId=None, programTitle=None):
	oc = ObjectContainer()
	try:
		if channelId == None: 
			result = Pooq().GetProgramInfo(programId)
			channelId = result['channelId'] if result is not None and 'channelId' in result else programId
			#channelId = result['channelId']
			programTitle = result['programTitle'] if result is not None and 'programTitle' in result else 'VOD'
		oc.title2 = unicode(programTitle + ' ' +pageNo +' 페이지')
		result_episodeList = Pooq().GetEpisodeList(channelId, programId, int(pageNo))
		count = int(result_episodeList['count'])
		has_more = 'Y' if count > 30 else 'N'
		for item in result_episodeList['list']:
			info = getInfo('VOD',item)
			pgm_nm = item['episodeTitle']
			freq = info['episode']
			if freq: title = '%s회 %s' % (freq,pgm_nm)
			else: title = pgm_nm
			isQvod = (item['isQvod'] == 'Y')
			if item['isFree'] == 'Y': title = '[무료]'+title
			oc.add(DirectoryObject(
				key = Callback(VODQuality, type='VOD', title=title, programId=info['programId'], contentId=info['id'],  cornerId=info['cornerId'], img=info['img'], plot=info['plot'], isQvod=isQvod),
				title = unicode(title),
				summary = unicode(info['plot']),
				thumb = Resource.ContentsOfURLWithFallback(info['img'])
			))
		if pageNo != '1':
			oc.add(DirectoryObject(
				key = Callback(EpisodeList, programId=programId, pageNo=str(int(pageNo)-1)),
				title = unicode('<< 이전 페이지')
			))
		if has_more == 'Y':
			oc.add(DirectoryObject(
				key = Callback(EpisodeList, programId=programId, pageNo=str(int(pageNo)+1)),
				title = unicode('다음 페이지 >>')
			))
	except Exception as e:
		Log('init EpisodeList Exception: %s' % e)
		pass
	if len(oc) == 0:
		message = 'Empty'
		oc.add(DirectoryObject(key = Callback(Label, message=message), title = unicode(message)))
	return oc


####################################################################################################
@route(PREFIX + '/createvideoclipobject', include_container = bool)
def CreateVideoClipObject(url, title, thumb, art, summary,
                          c_audio_codec, c_video_codec,
                          c_container, c_protocol,
                          c_user_agent = None, optimized_for_streaming = True,
                          include_container = False, programId = None, *args, **kwargs):
    Log('CreateVideoClipObject: %s' % url)
    if url.find('chunklist.m3u8') != -1:
	c_protocol = 'hls'
	c_container = 'mpegts'
	c_video_codec = VideoCodec.H264
	c_audio_codec = AudioCodec.AAC
    Log('CreateVideoClipObject2: c_audio_codec:%s c_video_codec:%s  c_container:%s  c_protocol:%s programId:%s' % (c_audio_codec, c_video_codec,
                          c_container, c_protocol, programId))
    vco = VideoClipObject(
        key = Callback(CreateVideoClipObject,
                       url = url, title = title, thumb = thumb, art = art, summary = summary,
                       c_audio_codec = c_audio_codec, c_video_codec = c_video_codec,
                       c_container = c_container, c_protocol = c_protocol,
                       c_user_agent = c_user_agent, optimized_for_streaming = optimized_for_streaming,
                       include_container = True, programId = programId),
        rating_key = url,
        title = title,
        thumb = thumb,
        art = art,
        summary = summary,
        items = [
            MediaObject(
                parts = [
                    PartObject(
                        key = HTTPLiveStreamURL(Callback(PlayVideo, url = url, programId=programId,c_user_agent = c_user_agent))
                    )
                ],
                audio_codec = c_audio_codec,
                video_codec = c_video_codec,
                container = c_container,
                protocol = c_protocol,
		audio_channels = 2,
                optimized_for_streaming = True
            )
        ]
    )

    if include_container:
        return ObjectContainer(objects = [vco], user_agent = c_user_agent)
    else:
        return vco

####################################################################################################
@route(PREFIX + '/createtrackobject', include_container = bool)
def CreateTrackObject(file_url, title, summary, thumb, include_container=False, *args, **kwargs):
	#container = 'mp3'
	#audio_codec = AudioCodec.MP3
	#else:
	container = Container.MP4
	audio_codec = AudioCodec.AAC

	track_object = TrackObject(
		key = Callback(CreateTrackObject, file_url=file_url, title=title, summary=summary, thumb=thumb, include_container=True),
		rating_key = file_url,
		title = title,
		summary = summary,
		items = [
			MediaObject(
				parts = [
					PartObject(key=file_url)
				],
				container = container,
				audio_codec = audio_codec,
				audio_channels = 2
			)
		], 
		thumb = Resource.ContentsOfURLWithFallback(thumb)
	)

	if include_container:
		return ObjectContainer(objects=[track_object])
	else:
		return track_object



####################################################################################################퀄리티 선택
@route(PREFIX + '/label')
def Label(message):
	oc = ObjectContainer(title2 = unicode(message))
	oc.add(DirectoryObject(
		key = Callback(Label, message=message),
		title = unicode(message)
	))
	return oc

####################################################################################################
def get_settings_login_info():
	uid = Prefs['id']
	pwd = Prefs['pw']
	return (uid, pwd)


def getInfo( c_type, i ):
	import re
	info = {}

	#common
	ageRestriction = i['ageRestriction'].encode('utf8')
	if ageRestriction in ['12','15', '18']: info['mpaa'] = '%s세 관람가' % ageRestriction
	else: info['mpaa'] = '전체 관람가'

	
	info['plot'] =''
	try:
		description =''
		if i['description'] is not None:
			description = i['description'].encode('utf8').replace('<br>','').replace('</br>','').replace('<b>','[B]').replace('</b>','[/B]')

		info['plot'] = description
		info['plotoutline'] = description
	except Exception as e:
		pass

	info['id'] = i['id']

	# individual
	if c_type == 'Live':
		info['subtitle'] = i['title'].encode('utf8')
		info['title'] = i['channelTitle'].encode('utf8')
		info['img'] = i['image']
		info['isRadio'] = i['isRadio']
		if i['isLicenceAvaliable'] == 'X': info['id'] = ''
		info['quality'] = "|".join(i['qualityList'][0]['quality'])
		info['programId'] = i['programId']

	elif c_type == 'VOD':
		info['tvshowtitle'] = i['title'].encode('utf8')
		try:
			info['title'] = i['episodeTitle'].encode('utf8')
		except:
			info['title'] = info['tvshowtitle']
		info['img'] = i['image'].replace('.jpg','_11.jpg')
		info['aired'] = i['airDate']
		info['programId'] = i['programId']
		info['cornerId'] = i['cornerId']
		try:
			info['cast'] = i['starling'].split(',')
		except:
			pass
		try:
			info['episode'] = int(i['episodeNo'])
		except:
			info['episode'] = None

	elif c_type == 'Movie':
		info['programId'] = ''
		title = i['title'].encode('utf8')
		info['title'] = re.sub(r'\[.*\] ?', '', title)
		info['img'] = i['image'].replace('.jpg','_210.jpg')
		try:
			info['genre'] = i['genere']
			info['cast'] = i['starling'].split(', ')
		except:
			pass

	return info

####################################################################################################
@indirect
@route(PREFIX + '/playvideo.m3u8')
def PlayVideo(url, programId, c_user_agent = None):
	try:
		result = Pooq().GetProgramInfo(programId)
		data = '|'.join([programId, result['channelId'], result['programTitle'].encode('utf-8'), result['imageUrl']])
		Pooq().SaveProgramList(data)
	except Exception as e:
		Log('Exception %s' % e)
		pass

	# Custom User-Agent string
	if c_user_agent:
		HTTP.Headers['User-Agent'] = c_user_agent
	return IndirectResponse(VideoClipObject, key = url)