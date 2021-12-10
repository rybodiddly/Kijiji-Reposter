import json
import os
import re
import time
import urllib
import xmltodict

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

def picUpload(fileData, session):
	# Picture Upload to eBay Server before create payload
	url = 'https://api.ebay.com/ws/api.dll'
	headers={
		'Host':'api.ebay.com',
		'Content-Type':'multipart/form-data; boundary=----FormBoundary7MA4YWxkTrZu0gW',
		'Connection':'keep-alive',
		'X-EBAY-API-CALL-NAME':'UploadSiteHostedPictures',
		'Accept':'*/*',
		'Accept-Language':'en-ca',
		'Accept-Encoding':'gzip, deflate, br',
		'User-Agent':'Kijiji/35739.100 CFNetwork/1121.2.2 Darwin/19.3.0'
	}

	picPayloadTopFile = os.path.join(THIS_FOLDER, 'static/img_upload_top.txt')
	picPayloadBottomFile = os.path.join(THIS_FOLDER, 'static/img_upload_bottom.txt')
			
	with open(picPayloadTopFile, 'r') as top:
		picPayloadTop = top.read()

	with open(picPayloadBottomFile, 'r') as bottom:
		picPayloadBottom = bottom.read()
	
	picPayload = picPayloadTop.encode('utf-8') + fileData + picPayloadBottom.encode('utf-8')
			
	r = session.post(url, headers=headers, data = picPayload)
			
	if r.status_code == 200 and r.text != '':
		parsed = xmltodict.parse(r.text)
		picUrl = parsed['UploadSiteHostedPicturesResponse']['SiteHostedPictureDetails']['FullURL']
		return picUrl
	else:
		parsed = xmltodict.parse(r.text)
		print(parsed)


def loginFunction(session, email, password):
	userExists = False
	tokenExpired = False
	tokensFile = os.path.join(THIS_FOLDER, 'static/tokens.json')
	userID = ''
	userToken = ''

	with open(tokensFile, 'r') as jsonFile:
		data = json.load(jsonFile)
		
		for item in data['users']:
			if re.search(r"\b{}\b".format(email), item['email'], re.IGNORECASE) is not None:
				userExists = True
				now = int(time.time())

				if now >= item['token_expiry']:
					tokenExpired = True
				else:
					userID = item['userID']
					userToken = item['token']

	if userExists == False or tokenExpired == True:

		url = 'https://mingle.kijiji.ca/api/users/login'
		headers = {
			'content-type':'application/x-www-form-urlencoded',
			'accept':'*/*',
			'x-ecg-ver':'1.67',
			'x-ecg-ab-test-group':'',
			'accept-language':'en-CA',
			'accept-encoding':'gzip',
			'user-agent':'Kijiji 12.15.0 (iPhone; iOS 13.5.1; en_CA)'
			}

		payload = {'username': email, 'password':password, 'socialAutoRegistration': 'false'}

		r = session.post(url, headers = headers, data = payload)

		# if kijiji response valid attempt to parse response
		if r.status_code == 200 and r.text != '':
			parsed = xmltodict.parse(r.text)
			userID = parsed['user:user-logins']['user:user-login']['user:id']
			userToken = parsed['user:user-logins']['user:user-login']['user:token']
			expiryTime = int(time.time()) + (24 * 60 * 60)

			# Create user entry
			if userExists == False:
				addUser = {
					'email': email,
					'userID': userID,
					'token': userToken,
					'token_expiry': expiryTime,
				}

				with open(tokensFile, 'r') as json_file: 
					data = json.load(json_file) 
					update = data['users'] 
					update.append(addUser)

				with open(tokensFile,'w') as json_file: 
					json.dump(data, json_file, indent=4)
					

			if tokenExpired == True:
				with open(tokensFile, 'r') as json_file: 
					data = json.load(json_file) 
					for item in data['users']:
						if email == item['email']:
							item['token'] = userToken
							item['token_expiry'] = expiryTime

				with open(tokensFile,'w') as json_file: 
					json.dump(data, json_file, indent=4)

			return userID, userToken

		else:
			parsed = xmltodict.parse(r.text)
			print(parsed)
	else:
		return userID, userToken

def getAttributes(session, userID, token, attributeID):
	url = 'https://mingle.kijiji.ca/api/ads/metadata/{}'.format(attributeID)
	userAuth = 'id="{}", token="{}"'.format(userID, token)
	headers = {
		'accept':'*/*',
		'x-ecg-ver':'1.67',
		'x-ecg-authorization-user': userAuth,
		'x-ecg-ab-test-group':'',
		'user-agent':'Kijiji 12.15.0 (iPhone; iOS 13.5.1; en_CA)',
		'accept-language':'en-CA',
		'accept-encoding':'gzip'
		}

	r = session.get(url, headers = headers)

	if r.status_code == 200 and r.text != '':
		parsed = xmltodict.parse(r.text)
		return parsed
	else:
		parsed = xmltodict.parse(r.text)
		print(parsed)

def getCategories(session, userID, token):
	url = 'https://mingle.kijiji.ca/api/categories'
	userAuth = 'id="{}", token="{}"'.format(userID, token)
	headers = {
		'accept':'*/*',
		'x-ecg-ver':'1.67',
		'x-ecg-authorization-user': userAuth,
		'x-ecg-ab-test-group':'',
		'user-agent':'Kijiji 12.15.0 (iPhone; iOS 13.5.1; en_CA)',
		'accept-language':'en-CA',
		'accept-encoding':'gzip'
		}

	r = session.get(url, headers = headers)
	
	if r.status_code == 200 and r.text != '':
		parsed = xmltodict.parse(r.text)
		return parsed
	else:
		parsed = xmltodict.parse(r.text)
		print(parsed)

def getLocations(session, userID, token):
	url = 'https://mingle.kijiji.ca/api/locations'
	userAuth = 'id="{}", token="{}"'.format(userID, token)
	headers = {
		'accept':'*/*',
		'x-ecg-ver':'1.67',
		'x-ecg-authorization-user': userAuth,
		'x-ecg-ab-test-group':'',
		'user-agent':'Kijiji 12.15.0 (iPhone; iOS 13.5.1; en_CA)',
		'accept-language':'en-CA',
		'accept-encoding':'gzip'
		}

	r = session.get(url, headers = headers)
	
	if r.status_code == 200 and r.text != '':
		parsed = xmltodict.parse(r.text)
		return parsed
	else:
		parsed = xmltodict.parse(r.text)
		print(parsed)

def getAdList(session, userID, token):
	url = 'https://mingle.kijiji.ca/api/users/{}/ads?size=50&page=0&_in=id,title,price,ad-type,locations,ad-status,category,pictures,start-date-time,features-active,view-ad-count,user-id,phone,email,rank,ad-address,phone-click-count,map-view-count,ad-source-id,ad-channel-id,contact-methods,attributes,link,description,feature-group-active,end-date-time,extended-info,highest-price'.format(userID)
	userAuth = 'id="{}", token="{}"'.format(userID, token)
	headers = {
		'accept':'*/*',
		'x-ecg-ver':'1.67',
		'x-ecg-authorization-user': userAuth,
		'x-ecg-ab-test-group':'',
		'user-agent':'Kijiji 12.15.0 (iPhone; iOS 13.5.1; en_CA)',
		'accept-language':'en-CA',
		'accept-encoding':'gzip'
		}

	r = session.get(url, headers = headers)

	if r.status_code == 200 and r.text != '':
		parsed = xmltodict.parse(r.text)
		return parsed
	else:
		parsed = xmltodict.parse(r.text)
		print(parsed)

def getAd(session, userID, token, adID):
	url = 'https://mingle.kijiji.ca/api/users/{}/ads/{}'.format(userID, adID)
	userAuth = 'id="{}", token="{}"'.format(userID, token)
	headers = {
		'accept':'*/*',
		'x-ecg-ver':'1.67',
		'x-ecg-authorization-user': userAuth,
		'x-ecg-ab-test-group':'',
		'user-agent':'Kijiji 12.15.0 (iPhone; iOS 13.5.1; en_CA)',
		'accept-language':'en-CA',
		'accept-encoding':'gzip'
		}

	r = session.get(url, headers = headers)

	if r.status_code == 200 and r.text != '':
		parsed = xmltodict.parse(r.text)
		return parsed
	else:
		parsed = xmltodict.parse(r.text)
		print(parsed)

def getSearchedAd(session, userID, token, adID):
	url = 'https://mingle.kijiji.ca/api/ads/{}'.format(adID)
	userAuth = 'id="{}", token="{}"'.format(userID, token)
	headers = {
		'accept':'*/*',
		'x-ecg-ver':'1.67',
		'x-ecg-authorization-user': userAuth,
		'x-ecg-ab-test-group':'',
		'user-agent':'Kijiji 12.15.0 (iPhone; iOS 13.5.1; en_CA)',
		'accept-language':'en-CA',
		'accept-encoding':'gzip'
		}

	r = session.get(url, headers = headers)

	if r.status_code == 200 and r.text != '':
		parsed = xmltodict.parse(r.text)
		return parsed
	else:
		parsed = xmltodict.parse(r.text)
		print(parsed)


def adExists(session, userID, token, adID):
	url = 'https://mingle.kijiji.ca/api/users/{}/ads/{}'.format(userID, adID)
	userAuth = 'id="{}", token="{}"'.format(userID, token)
	headers = {
		'accept':'*/*',
		'x-ecg-ver':'1.67',
		'x-ecg-authorization-user': userAuth,
		'x-ecg-ab-test-group':'',
		'user-agent':'Kijiji 12.15.0 (iPhone; iOS 13.5.1; en_CA)',
		'accept-language':'en-CA',
		'accept-encoding':'gzip'
		}

	r = session.get(url, headers = headers)

	if r.status_code == 200:
		return True
	else:
		return False

def getProfile(session, userID, token):
	url = 'https://mingle.kijiji.ca/api/users/{}/profile'.format(userID)
	userAuth = 'id="{}", token="{}"'.format(userID, token)
	headers = {
		'accept':'*/*',
		'x-ecg-ver':'1.67',
		'x-ecg-authorization-user': userAuth,
		'x-ecg-ab-test-group':'',
		'user-agent':'Kijiji 12.15.0 (iPhone; iOS 13.5.1; en_CA)',
		'accept-language':'en-CA',
		'accept-encoding':'gzip'
		}

	r = session.get(url, headers = headers)

	if r.status_code == 200 and r.text != '':	
		parsed = xmltodict.parse(r.text)
		return parsed
	else:
		parsed = xmltodict.parse(r.text)
		print(parsed)

def submitFunction(session, userID, token, payload):
	url = 'https://mingle.kijiji.ca/api/users/{}/ads'.format(userID)
	userAuth = 'id="{}", token="{}"'.format(userID, token)
	headers={
		'content-type':'application/xml',
		'accept':'*/*',
		'x-ecg-ver':'1.67',
		'x-ecg-ab-test-group':'',
		'accept-encoding': 'gzip',
		'x-ecg-authorization-user': userAuth,
		'accept-language':'en-CA',
		'user-agent':'Kijiji 12.15.0 (iPhone; iOS 13.5.1; en_CA)'
		}
	r = session.post(url, headers=headers, data=payload)
	
	if r.status_code == 201 and r.text != '':
		parsed = xmltodict.parse(r.text)
		return parsed
	else:
		parsed = xmltodict.parse(r.text)
		print(parsed)

def deleteAd(session, userID, adID, token):
	url = 'https://mingle.kijiji.ca/api/users/{}/ads/{}'.format(userID, adID)
	userAuth = 'id="{}", token="{}"'.format(userID, token)
	headers = {
		'content-type':'application/xml',
		'x-ecg-ver':'1.67',
		'x-ecg-ab-test-group':'',
		'x-ecg-authorization-user': userAuth,
		'accept-encoding': 'gzip',
		'user-agent':'Kijiji 12.15.0 (iPhone; iOS 13.5.1; en_CA)'
		}

	r = session.delete(url, headers = headers)

	if r.status_code == 204:
		print('Ad ' + adID + ' Successfully Deleted')
	else:
		parsed = xmltodict.parse(r.text)
		print(parsed)

def getConversations(session, userID, token, page):
	url = 'https://mingle.kijiji.ca/api/users/{}/conversations?size=25&page={}'.format(userID, page)
	userAuth = 'id="{}", token="{}"'.format(userID, token)
	headers = {
		'accept':'*/*',
		'x-ecg-ver':'1.67',
		'x-ecg-authorization-user': userAuth,
		'x-ecg-ab-test-group':'',
		'user-agent':'Kijiji 12.15.0 (iPhone; iOS 13.5.1; en_CA)',
		'accept-language':'en-CA',
		'accept-encoding':'gzip'
	}
	if page is not None and page != 'None':
		r = session.get(url, headers = headers)
	
		if r.status_code == 200 and r.text != '':
			parsed = xmltodict.parse(r.text)
			return parsed
		else:
			parsed = xmltodict.parse(r.text)
			print(parsed)

def getConversation(session, userID, token, conversationID):
	url = 'https://mingle.kijiji.ca/api/users/{}/conversations/{}?tail=100'.format(userID, conversationID)
	userAuth = 'id="{}", token="{}"'.format(userID, token)
	headers = {
		'accept':'*/*',
		'x-ecg-ver':'1.67',
		'x-ecg-authorization-user': userAuth,
		'x-ecg-ab-test-group':'',
		'user-agent':'Kijiji 12.15.0 (iPhone; iOS 13.5.1; en_CA)',
		'accept-language':'en-CA',
		'accept-encoding':'gzip'
	}
	r = session.get(url, headers = headers)
	
	if r.status_code == 200 and r.text != '':
		parsed = xmltodict.parse(r.text)
		return parsed
	else:
		parsed = xmltodict.parse(r.text)
		print(parsed)

def sendReply(session, userID, token, payload):
	url = 'https://mingle.kijiji.ca/api/replies/reply-to-ad-conversation'
	userAuth = 'id="{}", token="{}"'.format(userID, token)
	headers = {
		'content-type':'application/xml',
		'accept':'*/*',
		'x-ecg-ver':'1.67',
		'x-ecg-ab-test-group':'',
		'accept-language':'en-CA',
		'x-ecg-authorization-user': userAuth,
		'accept-encoding':'gzip',
		'user-agent':'Kijiji 12.15.0 (iPhone; iOS 13.5.1; en_CA)'		
	}

	r = session.post(url, headers = headers, data=payload)
	
	if r.status_code == 201 and r.text != '':
		parsed = xmltodict.parse(r.text)
		return parsed
	else:
		parsed = xmltodict.parse(r.text)
		print(parsed)

def createReplyPayload(adID, replyName, replyEmail, reply, conversationID, direction):
	replyPayload = {
		"reply:reply-to-ad-conversation": {
			"@xmlns:types": "http://www.ebayclassifiedsgroup.com/schema/types/v1", 
			"@xmlns:cat": "http://www.ebayclassifiedsgroup.com/schema/category/v1", 
			"@xmlns:loc": "http://www.ebayclassifiedsgroup.com/schema/location/v1", 
			"@xmlns:ad": "http://www.ebayclassifiedsgroup.com/schema/ad/v1", 
			"@xmlns:attr": "http://www.ebayclassifiedsgroup.com/schema/attribute/v1", 
			"@xmlns:pic": "http://www.ebayclassifiedsgroup.com/schema/picture/v1", 
			"@xmlns:user": "http://www.ebayclassifiedsgroup.com/schema/user/v1", 
			"@xmlns:rate": "http://www.ebayclassifiedsgroup.com/schema/rate/v1", 
			"@xmlns:reply": "http://www.ebayclassifiedsgroup.com/schema/reply/v1", 
			"@locale": "en-CA", 
			"reply:ad-id": adID, 
			"reply:reply-username": replyName, 
			"reply:reply-phone": None, 
			"reply:reply-email": replyEmail, 
			"reply:reply-message": reply, 
			"reply:conversation-id": conversationID, 
			"reply:reply-direction": {
				"types:value": direction}}}

	# Parse into XML
	payload = xmltodict.unparse(replyPayload, short_empty_elements=True, pretty=True)
	return payload

def createReplyAdPayload(adID, replyName, replyEmail, reply):

	replyPayload = {
		"reply:reply-to-ad-conversation": {
			"@xmlns:types": "http://www.ebayclassifiedsgroup.com/schema/types/v1", 
			"@xmlns:cat": "http://www.ebayclassifiedsgroup.com/schema/category/v1", 
			"@xmlns:loc": "http://www.ebayclassifiedsgroup.com/schema/location/v1", 
			"@xmlns:ad": "http://www.ebayclassifiedsgroup.com/schema/ad/v1", 
			"@xmlns:attr": "http://www.ebayclassifiedsgroup.com/schema/attribute/v1", 
			"@xmlns:pic": "http://www.ebayclassifiedsgroup.com/schema/picture/v1", 
			"@xmlns:user": "http://www.ebayclassifiedsgroup.com/schema/user/v1", 
			"@xmlns:rate": "http://www.ebayclassifiedsgroup.com/schema/rate/v1", 
			"@xmlns:reply": "http://www.ebayclassifiedsgroup.com/schema/reply/v1", 
			"@locale": "en-CA", 
			"reply:ad-id": adID, 
			"reply:reply-username": replyName, 
			"reply:reply-phone": None, 
			"reply:reply-email": replyEmail, 
			"reply:reply-message": reply, 
			"reply:structured-msg-id": "1",
			"reply:reply-direction": {
				"types:value": "TO_OWNER"}}}

	# Parse into XML
	payload = xmltodict.unparse(replyPayload, short_empty_elements=True, pretty=True)
	return payload

def searchFunction(session, userID, token, longitude, latitude, size, postal_code, page, radius, category, criteria):
	criteria = urllib.parse.quote(criteria)
	topads = 'true'
	sort_type = 'DATE_DESCENDING'
	postal_code = urllib.parse.quote(postal_code)
	url = 'https://mingle.kijiji.ca/api/ads?ad-status=ACTIVE&includeTopAds={}&sortType={}&q={}&longitude={}&searchOptionsExactMatch=false&latitude={}&extension[origin]=SRP&size={}&address={}&page={}&distance={}&categoryId={}&_in=id,title,price,ad-type,locations,ad-status,category,pictures,start-date-time,features-active,view-ad-count,user-id,phone,email,rank,ad-address,phone-click-count,map-view-count,ad-source-id,ad-channel-id,contact-methods,attributes,link,description,feature-group-active,end-date-time,extended-info,highest-price,notice,has-virtual-tour-url'.format(topads, sort_type, criteria, longitude, latitude, size, postal_code, page, radius, category)
	headers = {
		'Host': 'mingle.kijiji.ca',
		'timestamp': str(int(time.time())),
		'X-ECG-VER': '3.6',
		'Accept-Language': 'en-CA',
		'X-ECG-Authorization-User': 'id="{}", token="{}"'.format(userID, token),
		'Accept-Encoding': 'gzip',
		'Accept': '*/*',
		'User-Agent': 'Kijiji 15.17.0 (iPhone; iOS 14.6; en_CA)',
		'Connection': 'keep-alive'
	}
	r = session.get(url, headers=headers)
	if r.status_code == 200 and r.text != '':
		parsed = xmltodict.parse(r.text)
		return parsed
	else:
		parsed = xmltodict.parse(r.text)
		print(parsed)

def checkPostalCodeLength(postal_code):
	if len(postal_code) == 6:
		section1 = postal_code[:3]
		section2 = postal_code[3:6]
		return section1 + ' ' + section2
	else:
		return postal_code