from optparse import OptionParser
from datetime import datetime, timedelta
from time import sleep
from os import system
import threading
import requests
import instapy_cli
from facebook import GraphAPI
import configparser

x=datetime.now()
vid_plus_time=list()



parser = OptionParser()
parser.add_option("--time_to_publish", action="append")
parser.add_option("--title", action="append")
parser.add_option("--video_name", action="append")
parser.add_option("--description", action="append")
parser.add_option("--thumbnail", action="append")
parser.add_option("--config_file")
parser.add_option("--every_other_day", default="None")
parser.add_option("--everyday", default="None")
parser.add_option("--tomorrow", default="None")
parser.add_option("--to_facebook", default="False")
parser.add_option("--to_instagram", default="False")
parser.add_option("--to_youtube", default="False")

config = configparser.ConfigParser()
config.sections()


(options, args) = parser.parse_args()

missing_mandatory_options=0
for mandatory_options in ["time_to_publish", "title", "video_name", "description", "thumbnail", "config_file"]:
	if options.__dict__[mandatory_options] == None:
		missing_mandatory_options+=1
		print("missing --%s" % mandatory_options)

if missing_mandatory_options <= 6 and not missing_mandatory_options == 0:
	print("please add missing information")
	exit()

config.read(options.config_file)

def create_time_to_publish():
	tomorrow_lock=0
	second, microsecond = 0, 0
	hour_, minute_ = 0, 0
	time_to_publish=datetime.now()
	for a, b in zip(options.video_name, options.time_to_publish):																												#
		if options.tomorrow == "True":																																			#
			if tomorrow_lock != 1:																																				#
				time_to_publish+=timedelta(days=1)																																#
				tomorrow_lock=1																																					#
		if options.everyday == "True":																																			#
			time_to_publish+=timedelta(days=1)																																	#
		if options.every_other_day == "True":																																	#
			time_to_publish+=timedelta(days=2)																																	#
		if b.count("am") == True:																																				#  if it is AM
			c=b.split("am")[0]																																					#   split the string and give me the first result
			if c.count(":") == 1:																																				#   if the result contains a colon
				hour_, minute_=c.split(":")																																		#    split it into two results, the hour and the minute
				hour_, minute_=int(hour_), int(minute_)																															#    then represent the hour and minute as integers
			else:																																								#   if it doesn't contain a colon
				hour_=int(c)																																					#    give me the hour
				minute_=0																																						#    and set the minute setting to zero
		if b.count("pm") == True:																																				#  if it is PM
			c=b.split("pm")[0]																																					#   split the string and give me the first result
			if c.count(":") == 1:																																				#   if the result contains a colon
				hour_, minute_=c.split(":")																																		#    split it into two results, the hour and the minute
				hour_, minute_=int(hour_), int(minute_)																															#    then represent the hour and minute as integers
			else:																																								#   if it doesn't contain a colon
				hour_=int(c)																																					#    give me the hour
				minute_=0																																						#    and set the minute setting to zero
			if hour_ != 12:																																						#   if the hour is after [12 pm]
				hour_+=12																																						#    add 12
		vid_plus_time.append(a+" "+time_to_publish.replace(hour=hour_, minute=minute_, second=second, microsecond=microsecond).strftime("%Y-%m-%dT%H:%M:%S.%fZ"))				#
	return vid_plus_time


def publish_video_to_instagram(video_file, time_to_sleep, title, description):
	sleep(time_to_sleep)
	with instapy_cli.client(username, password) as cli:
		cli.upload(video_file, "Title: "+title+"\nDescription: "+description)

def publish_to_instagram(title, video_name_plus_time_to_publish, description, thumbnail):
	vid_file, time = video_name_plus_time_to_publish.split()
	threading.Thread(target=publish_video_to_instagram, args=(vid_file, round((datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ')).timestamp()-datetime.now().timestamp()),title,description)).start()
	with instapy_cli.client(username, password) as cli:
		cli.upload(thumbnail, "Title: "+repr(title)+" comes out on "+str(datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%m/%d/%Y @ %I:%M %p'))+"\nDescription: "+description)

def publish_to_youtube(title, video_name_plus_time_to_publish, description, thumbnail):
	vid_file, time = video_name_plus_time_to_publish.split()
	system("youtube-upload --title="+repr(title)+"--description="+repr(description)+" --publish-at="+repr(time)+" --credentials-file="+repr(config['youtube']['credentials'])+" --client-secrets="+repr(config['youtube']['client-secrets'])+" --thumbnail="+repr(thumbnail)+" "+vid_file)

fb_pub=GraphAPI(access_token=config['facebook']['token'], version="8.0")

def publish_video_to_facebook(video_file, time_to_sleep, title, description):
	sleep(time_to_sleep)
	requests.post("https://graph-video.facebook.com/v12.0/"+config['facebook']['page_id']+'/feed?token_access='+config['facebook']['token'], {'name': '%s' %(title), 'description': '%s' %(description), 'source': '%s' %(vid_file)})

def publish_to_facebook(title, video_name_plus_time_to_publish, description, thumbnail):
	vid_file, time = video_name_plus_time_to_publish.split()
	fb_pub.put_object(image=open(thumbnail, 'rb'), message="Title: "+repr(title)+" comes out on "+str(datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%m/%d/%Y @ %I:%M %p'))+"\nDescription: "+description)
	threading.Thread(target=publish_video_to_facebook, args=(vid_file, round((datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ')).timestamp()-datetime.now().timestamp()),title,description)).start()

if options.to_youtube == "True":
	list(map(publish_to_youtube, options.title, create_time_to_publish(), options.description, options.thumbnail))

if options.to_instagram == "True":
	list(map(publish_to_instagram, options.title, create_time_to_publish(), options.description, options.thumbnail))

if options.to_facebook == "True":
	list(map(publish_to_facebook, options.title, create_time_to_publish(), options.description, options.thumbnail))


## http://www.alexonlinux.com/pythons-optparse-for-human-beings#support_for_mandatory_(required)_options.
## https://stackabuse.com/converting-strings-to-datetime-in-python/
## https://stackoverflow.com/questions/12468823/python-datetime-setting-fixed-hour-and-minute-after-using-strptime-to-get-day/12468869
## https://stackoverflow.com/questions/7852855/in-python-how-do-you-convert-a-datetime-object-to-seconds
## https://www.linuxjournal.com/content/threading-python
## https://stackoverflow.com/questions/30914038/python-facebook-upload-video-from-external-link
## https://console.cloud.google.com/apis/credentials
## https://developers.google.com/youtube/registering_an_application
## https://github.com/tokland/youtube-upload
## https://github.com/b3nab/instapy-cli/blob/master/examples/
## https://developers.facebook.com/tools/explorer/
## https://developers.facebook.com/docs/video-api/guides/publishing
## https://facebook-sdk.readthedocs.io/en/latest/install.html
## https://stackoverflow.com/questions/68218421/how-can-i-upload-a-video-on-instagram-using-python
## 