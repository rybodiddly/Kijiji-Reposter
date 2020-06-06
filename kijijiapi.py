import time
import xmltodict

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

	picPayloadTopFile = 'static/img_upload_top.txt'
	picPayloadBottomFile = 'static/img_upload_bottom.txt'
			
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
	
	# Login Header
	headers = {
		'content-type':'application/x-www-form-urlencoded',
		'accept':'*/*',
		'x-ecg-ver':'1.63',
		'x-ecg-ab-test-group':'',
		'accept-language':'en-CA',
		'x-ecg-udid':'D1E2FB5C-5133-48CB-A2B7-618D4231CC33',
		'accept-encoding':'gzip',
		'x-threatmetrix-session-id':'6a7ad72d6e5c4ca2b40afa10577ce671',
		'user-agent':'Kijiji 12.6.0 (iPhone; iOS 13.3.1; en_CA)'
		}

	payload = {'username': email, 'password':password, 'socialAutoRegistration': 'false'}

	r = session.post('https://mingle.kijiji.ca/api/users/login', headers = headers, data = payload)

	# if kijiji response valid attempt to parse response
	if r.status_code == 200 and r.text != '':
		parsed = xmltodict.parse(r.text)
		userID = parsed['user:user-logins']['user:user-login']['user:id']
		userToken = parsed['user:user-logins']['user:user-login']['user:token']
		return userID, userToken
	else:
		parsed = xmltodict.parse(r.text)
		print(parsed)

def getAdList(session, userID, token):
	url = 'https://mingle.kijiji.ca/api/users/{}/ads?size=50&page=0&_in=id,title,price,ad-type,locations,ad-status,category,pictures,start-date-time,features-active,view-ad-count,user-id,phone,email,rank,ad-address,phone-click-count,map-view-count,ad-source-id,ad-channel-id,contact-methods,attributes,link,description,feature-group-active,end-date-time,extended-info,highest-price'.format(userID)
	userAuth = 'id="{}", token="{}"'.format(userID, token)
	headers = {
		'accept':'*/*',
		'x-ecg-udid':'D1E2FB5C-5133-48CB-A2B7-618D4231CC33',
		'x-ecg-ver':'1.63',
		'x-ecg-authorization-user': userAuth,
		'x-ecg-ab-test-group':'',
		'user-agent':'Kijiji 12.6.0 (iPhone; iOS 13.3.1; en_CA)',
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
		'x-ecg-udid':'D1E2FB5C-5133-48CB-A2B7-618D4231CC33',
		'x-ecg-ver':'1.63',
		'x-ecg-authorization-user': userAuth,
		'x-ecg-ab-test-group':'',
		'user-agent':'Kijiji 12.6.0 (iPhone; iOS 13.3.1; en_CA)',
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
		'x-ecg-udid':'D1E2FB5C-5133-48CB-A2B7-618D4231CC33',
		'x-ecg-ver':'1.63',
		'x-ecg-authorization-user': userAuth,
		'x-ecg-ab-test-group':'',
		'user-agent':'Kijiji 12.6.0 (iPhone; iOS 13.3.1; en_CA)',
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
		'x-ecg-udid':'D1E2FB5C-5133-48CB-A2B7-618D4231CC33',
		'x-ecg-ver':'1.63',
		'x-ecg-authorization-user': userAuth,
		'x-ecg-ab-test-group':'',
		'user-agent':'Kijiji 12.6.0 (iPhone; iOS 13.3.1; en_CA)',
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
		'x-ecg-ver':'1.63',
		'x-ecg-ab-test-group':'',
		'accept-encoding': 'gzip',
		'x-ecg-udid':'D1E2FB5C-5133-48CB-A2B7-618D4231CC33',
		'x-ecg-authorization-user': userAuth,
		'accept-language':'en-CA',
		'user-agent':'Kijiji 12.6.0 (iPhone; iOS 13.3.1; en_CA)'
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
		'x-ecg-ver':'1.63',
		'x-ecg-ab-test-group':'',
		'x-ecg-udid':'D1E2FB5C-5133-48CB-A2B7-618D4231CC33',
		'x-ecg-authorization-user': userAuth,
		'accept-encoding': 'gzip',
		'user-agent':'Kijiji 12.6.0 (iPhone; iOS 13.3.1; en_CA)'
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
		'x-ecg-udid':'D1E2FB5C-5133-48CB-A2B7-618D4231CC33',
		'x-ecg-ver':'1.67',
		'x-ecg-authorization-user': userAuth,
		'x-ecg-ab-test-group':'',
		'user-agent':'Kijiji 12.9.0 (iPhone; iOS 13.4.1; en_CA)',
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
	url = 'https://mingle.kijiji.ca/api/users/26377662/conversations/{}?tail=100'.format(conversationID)
	userAuth = 'id="{}", token="{}"'.format(userID, token)
	headers = {
		'accept':'*/*',
		'x-ecg-udid':'D1E2FB5C-5133-48CB-A2B7-618D4231CC33',
		'x-ecg-ver':'1.67',
		'x-ecg-authorization-user': userAuth,
		'x-ecg-ab-test-group':'',
		'user-agent':'Kijiji 12.9.0 (iPhone; iOS 13.4.1; en_CA)',
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
		'x-ecg-udid':'D1E2FB5C-5133-48CB-A2B7-618D4231CC33',
		'x-ecg-authorization-user': userAuth,
		'accept-encoding':'gzip',
		'user-agent':'Kijiji 12.9.0 (iPhone; iOS 13.4.1; en_CA)',		
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
