import requests
import random
import json
import sys
import os, sys
import argparse
import sys, time
import collections
import re as r
import smtplib
import dns.resolver
userinfo={}
nu = "\033[0m"
re = "\033[1;31m"
gr = "\033[0;32m"
cy = "\033[0;36m"
wh = "\033[0;37m"
ye = "\033[0;34m"

su = f"\033[1;31m[\033[1;36m+\033[1;31m]{nu}"
fa = f"\033[1;31m[\033[1;31m!\033[1;31m]{nu}"
er = f"\033[1;31m[\033[1;34m?\033[1;31m]{nu}"

# 30-33, 48-50, 94-96, 195-210

def urlshortner(url):
    data = requests.get("http://tinyurl.com/api-create.php?url=" + url)
    return data.text

def write(stri):
    for char in stri:
        time.sleep(0.1)
        sys.stdout.write(char)
        sys.stdout.flush()

def sort_list(xlist):
    with_count = dict(collections.Counter(xlist))
    output = {k: v for k, v in sorted(with_count.items(), reverse=True, key=lambda item: item[1])}
    return output
    
def find(stri):
    exinfo = {}
    email = r.findall(r"[_a-z0-9-\.]+[＠@]{1}[a-z0-9]+\.[a-z0-9]+", stri.lower())
    exinfo['email'] = email

    #(?:^|\s)([＃|@]{1}[_a-zA-Z0-9\.\+-]+)
    tags = r.findall(r"[＃#]{1}([_a-zA-Z0-9\.\+-]+)", stri)
    exinfo['tags'] = tags

    mention = []
    raw_mention = r.findall(r"[＠@]([_a-zA-Z0-9\.\+-]+)", stri)
    for x in raw_mention:
        if x.endswith("."):
            x = x.strip(".")
        mention.append(x)
    exinfo['mention'] = mention

    return exinfo


useragent = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393'
'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
'Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4'
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
'Mozilla/5.0 (Linux; U; Android-4.0.3; en-us; Galaxy Nexus Build/IML74K) AppleWebKit/535.7 (KHTML, like Gecko) CrMo/16.0.912.75 Mobile Safari/535.7']

resp_js = None
is_private = False
total_uploads = 12

def proxy_session():
	session = requests.session()
	session.proxies = {
		'http':  'socks5://127.0.0.1:9050',
		'https': 'socks5://127.0.0.1:9050'
	}
	return session

def get_page(usrname):
	global resp_js
	session = requests.session()
	session.headers = {'User-Agent': random.choice(useragent)}
	resp_js = session.get('https://www.instagram.com/'+usrname+'/?__a=1').text
	return resp_js

def exinfo():

	def xprint(xdict, text):
		if xdict != {}:
			print("most used :" , text)
			i = 0
			for key, val in xdict.items():
				if len(mail) == 1:
					if key in mail[0]:
						continue
				print("_",(key, val))
				i += 1
				if i > 4:
					break
			print()
		else:
			pass
	
	raw = find(resp_js)

	mail = raw['email']
	tags = sort_list(raw['tags'])
	ment = sort_list(raw['mention'])

	if mail != []:
		if len(mail) == 1:
			print(f"{su} {re}email found : \n{gr}  %s" % mail[0])
			print()
		else:
			print(f"{su} {re}email found : \n{gr}  ")
			for x in range(len(mail)):
				print(mail[x])
			print()

	xprint(tags, "tags")
	xprint(ment, "mentions")
	
def user_info(usrname):

	global total_uploads, is_private
	resp_js = get_page(usrname)
	js = json.loads(resp_js)
	js = js['graphql']['user']
	
	if js['is_private'] != False:
		is_private = True
	
	if js['edge_owner_to_timeline_media']['count'] > 12:
		pass
	else:
		total_uploads = js['edge_owner_to_timeline_media']['count']

	usrinfo = {
		'username': js['username'],
		'user id': js['id'],
		'name': js['full_name'],
		'followers': js['edge_followed_by']['count'],
		'following': js['edge_follow']['count'],
		'posts img': js['edge_owner_to_timeline_media']['count'],
		'posts vid': js['edge_felix_video_timeline']['count'],
		'reels': js['highlight_reel_count'],
		'bio': js['biography'].replace('\n', ', '),
		'external url': js['external_url'],
		'private': js['is_private'],
		'verified': js['is_verified'],
		'profile img': urlshortner(js['profile_pic_url_hd']),
		'business account': js['is_business_account'],
		#'connected to fb': js['connected_fb_page'],  -- requires login
		'joined recently': js['is_joined_recently'],
		'business category': js['business_category_name'],
		'category': js['category_enum'],
		'has guides': js['has_guides'],
	}
	print("user info")
	for key, val in usrinfo.items():
		print((key, val))
	print("") 
	exinfo()
	global userinfo
	userinfo=usrinfo.copy()
def highlight_post_info(i):

	postinfo = {}
	total_child = 0
	child_img_list = []

	x = json.loads(resp_js)
	js = x['graphql']['user']['edge_owner_to_timeline_media']['edges'][i]['node']

	# this info will be same on evry post
	info = {
		'comments': js['edge_media_to_comment']['count'],
		'comment disable': js['comments_disabled'],
		'timestamp': js['taken_at_timestamp'],
		'likes': js['edge_liked_by']['count'],
		'location': js['location'],
	}

	# if image dosen't have caption this key dosen't exist instead of null
	try:
		info['caption'] = js['edge_media_to_caption']['edges'][0]['node']['text']
	except IndexError:
		pass

	# if uploder has multiple images / vid in single post get info how much edges are
	if 'edge_sidecar_to_children' in js:
		total_child = len(js['edge_sidecar_to_children']['edges'])

		for child in range(total_child):
			js = x['graphql']['user']['edge_owner_to_timeline_media']['edges'][i]['node']['edge_sidecar_to_children']['edges'][child]['node']
			img_info = {
				'typename': js['__typename'],
				'id': js['id'],
				'shortcode': js['shortcode'],
				'dimensions': str(js['dimensions']['height'] + js['dimensions']['width']),
				'image url' : js['display_url'],
				'fact check overall': js['fact_check_overall_rating'],
				'fact check': js['fact_check_information'],
				'gating info': js['gating_info'],
				'media overlay info': js['media_overlay_info'],
				'is_video': js['is_video'],
				'accessibility': js['accessibility_caption']
			}

			child_img_list.append(img_info)

		postinfo['imgs'] = child_img_list
		postinfo['info'] = info

	else:
		info = {
			'comments': js['edge_media_to_comment']['count'],
			'comment disable': js['comments_disabled'],
			'timestamp': js['taken_at_timestamp'],
			'likes': js['edge_liked_by']['count'],
			'location': js['location'],
		}

		try:
			info['caption'] = js['edge_media_to_caption']['edges'][0]['node']['text']
		except IndexError:
			pass

		img_info = {
				'typename': js['__typename'],
				'id': js['id'],
				'shortcode': js['shortcode'],
				'dimensions': str(js['dimensions']['height'] + js['dimensions']['width']),
				'image url' : js['display_url'],
				'fact check overall': js['fact_check_overall_rating'],
				'fact check': js['fact_check_information'],
				'gating info': js['gating_info'],
				'media overlay info': js['media_overlay_info'],
				'is_video': js['is_video'],
				'accessibility': js['accessibility_caption']
			}
		
		child_img_list.append(img_info)
		
		postinfo['imgs'] = child_img_list
		postinfo['info'] = info

	return postinfo

def post_info():
	
	if is_private != False:
		print(f"{fa} {gr}cannot use -p for private accounts !\n")
		sys.exit(1)
	
	posts = []
	
	for x in range(total_uploads):
		posts.append(highlight_post_info(x))

	for x in range(len(posts)):
		# get 1 item from post list
		print(f"{su}{re} post %s :" % x)
		for key, val in posts[x].items():
			if key == 'imgs':
				# how many child imgs post has
				postlen = len(val)
				# loop over all child img
				print(f"{su}{re} contains %s media" % postlen) 
				for y in range(postlen):
					# print k,v of all child img in loop
					for xkey, xval in val[y].items():
						print(f"  {gr}%s : {wh}%s" % (xkey, xval))
			if key == 'info':
				print(f"{su}{re} info :")
				for key, val in val.items():
					print(f"  {gr}%s : {wh}%s" % (key, val))
				print("")	


def validate_mail(mail):
	regex = r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$"
	match = r.match(regex, mail)
	if match == None:
		print('regex : fail')
	else:
		print('regex : success')
	splitAddress = mail.split('@')
	domain = str(splitAddress[1])
	records = dns.resolver.resolve(domain, 'MX')
	mxr = records[0].exchange
	mxr = str(mxr)
	print('mx :', mxr.lower())
	fromaddr = 'no-reply@gmail.com'
	connect = smtplib.SMTP()
	connect.set_debuglevel(0)
	connect.connect(mxr)
	connect.helo(connect.local_hostname)
	connect.mail(fromaddr)
	code, message = connect.rcpt(str(mail))
	connect.quit()
	if code == 250:
		print('smtp : success')
	else:
		print('smtp : fail')

user_info("aymalkhalid")
print(userinfo)
