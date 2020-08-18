import atexit
import datetime
import httpx
import json
import os
import time
import urllib3
import xmltodict
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify, send_file, render_template, session, redirect, url_for, send_from_directory, Markup
from flask_wtf import FlaskForm, Form
from flask_wtf.file import FileField, FileRequired, FileAllowed
from kijijiapi import *
from wtforms.fields.html5 import DateField, TimeField
from wtforms import SelectField, TextField, TextAreaField, validators, StringField, SubmitField, FieldList, FormField, BooleanField, IntegerField
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Set Absolute Path
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Class Declarations:
# Persistent Forms used when Posting Ad
class PostForm(FlaskForm):
	class Meta:
		csrf = False
	adtitle = TextField(id='adtitle', label= 'Ad Title', validators=[validators.DataRequired(), validators.Length(max=64)])
	adtype = SelectField(id='adtype', label='Ad Type', choices=[])
	cat1 = SelectField(id='cat1', label='Category')
	cat2 = SelectField(id='cat2')
	cat3 = SelectField(id='cat3')
	description = TextAreaField(id='description', label='Description', validators=[validators.DataRequired()])
	loc1 = SelectField(id='loc1', label='Location')
	loc2 = SelectField(id='loc2')
	loc3 = SelectField(id='loc3')
	price = TextField(id='price', label='Price')
	pricetype = SelectField(id='pricetype', label='Price Type', choices = ['SPECIFIED_AMOUNT', 'PLEASE_CONTACT', 'SWAP_TRADE', 'FREE'])
	postalcode = TextField(id='postalcode',label='Postal Code', validators=[validators.DataRequired()])
	phone = TextField(id='phone', label='Phone')
	file1 = FileField(id='file1', label='Pictures', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
	file2 = FileField(id='file2', label='Pictures', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
	file3 = FileField(id='file3', label='Pictures', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
	file4 = FileField(id='file4', label='Pictures', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
	file5 = FileField(id='file5', label='Pictures', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
	file6 = FileField(id='file6', label='Pictures', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
	file7 = FileField(id='file7', label='Pictures', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
	file8 = FileField(id='file8', label='Pictures', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
	file9 = FileField(id='file9', label='Pictures', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
	file10 = FileField(id='file10', label='Pictures', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
	repost = BooleanField(id='repost', label='Repost')
	time1 = TimeField(id='time1', label='Time')
	time2 = TimeField(id='time2', label='Time')
	time3 = TimeField(id='time3', label='Time')
	time4 = TimeField(id='time4', label='Time')
	time5 = TimeField(id='time5', label='Time')
	time6 = TimeField(id='time6', label='Time')
	time7 = TimeField(id='time7', label='Time')
	time8 = TimeField(id='time8', label='Time')
	password = TextField(id='password', label='Password')

class ConversationForm(FlaskForm):
	class Meta:
		csrf = False
	reply = TextAreaField(id='reply', label='Reply', validators=[validators.DataRequired()])

# Functions:
def getXML(filename):
	#retrievs parsed xml file
	with open(filename, 'r') as f:
		content = f.read()
		f.close()
	parsed = xmltodict.parse(content)
	return parsed

def timeValidator(time):
	# reformats timestamp into valid / usable format
	if time != None and time != '':
		validTime = time.strftime("%H:%M")
		return validTime
	else:
		return None

def timeSubtractor(time):
	if time != None and time != '':
		delta = datetime.timedelta(minutes=3)
		converted = datetime.datetime.strptime(time,"%H:%M")
		minus = (converted - delta).strftime("%H:%M")
		return minus
	else:
		return None

def chooseCategory(cat1, cat2, cat3):
	if cat3 != None and cat3 != '':
		return cat3
	elif (cat3 is None or cat3 == '') and (cat2 != None and cat2 != ''):
		return cat2
	else:		
		if cat1 == 'Kijiji Village':
			return '36611001'
		elif cat1 == 'Buy & Sell':
			return '10'
		elif cat1 == 'Cars & Vehicles':
			return '27'
		elif cat1 == 'Real Estate':
			return '34'
		elif cat1 == 'Jobs':
			return '45'
		elif cat1 == 'Services':
			return '72'
		elif cat1 == 'Pets':
			return '112'
		elif cat1 == 'Community':
			return '1'
		elif cat1 == 'Vacation Rentals':
			return '800'
		elif cat1 == 'Free Stuff':
			return '17220001'

def chooseLocation(loc1, loc2, loc3):
	if loc3 != None and loc3 != '':
		return loc3
	elif (loc3 is None or loc3 == '') and (loc2 != None and loc2 != ''):
		return loc2
	elif (loc3 is None or loc3 == '') and (loc2 is None or loc2 == '') and (loc1 != None and loc1 != ''):
		return loc1
	else:
		# default to Canada '0'
		return '0'

def picLink(data, session):
	if  data != None and data != '' and data != b'':
		file = data
		fileData = file.read()
		picLink = picUpload(fileData, session)
		return picLink
	else:
		return None

def testListInstance(data):
	if isinstance(data,list):
		return True

def reposter():
	#delete then repost
	writeActivate = False

	scheduleFile = os.path.join(THIS_FOLDER, 'static/schedules.json')
	with open(scheduleFile, 'r') as jsonFile:
		data = json.load(jsonFile)
		for item in data['schedules']:
			# Time Calcualtions
			now = datetime.datetime.now()
			current_time = now.strftime("%H:%M") #"%H:%M:%S"

			try:
				# Delete Ad 3 Minutes Before Repost Time
				if (timeSubtractor(item['time1']) == current_time) or (timeSubtractor(item['time2']) == current_time) or (timeSubtractor(item['time3']) == current_time) or (timeSubtractor(item['time4']) == current_time) or (timeSubtractor(item['time5']) == current_time) or (timeSubtractor(item['time6']) == current_time) or (timeSubtractor(item['time7']) == current_time) or (timeSubtractor(item['time8']) == current_time):

					email = item['useremail']
					password = item['userpassword']
					adID = item['current_ad_id']

					# Retry 20 times if exception raised
					tries = 20
					for i in range(tries):
						try:
							# Login
							userID, userToken = loginFunction(kijijiSession, email, password)

							# Delete Old Ad
							deleteAd(kijijiSession, userID, adID, userToken)
							print('3 minute delay until repost ', now)

						except:
							print('Error: Deletion Failed at: ', now)
							print('Retry Attempt:', i)
							if i < tries - 1: # i is zero indexed
								time.sleep(5)
								continue

						else:
							# exit loop if successful
							break

				# Repost at current time
				# Check if Deleted
				if (item['time1'] == current_time) or (item['time2'] == current_time) or (item['time3'] == current_time) or (item['time4'] == current_time) or (item['time5'] == current_time) or (item['time6'] == current_time) or (item['time7'] == current_time) or (item['time8'] == current_time):
					#repost
					
					email = item['useremail']
					password = item['userpassword']
					adFile = item['ad_file']
					adID = item['current_ad_id']

					# Retry 20 times if exception raised
					tries = 20
					for i in range(tries):
						try:
							# Login
							userID, userToken = loginFunction(kijijiSession, email, password)

							# Check if Ad exists, if not, then deletion was successful
							exists = adExists(kijijiSession, userID, userToken, adID)
							if exists == False:

								# Open file / Get payload
								with open(adFile, 'r') as f:
									payload = f.read()

								# Post Ad
								parsed = submitFunction(kijijiSession, userID, userToken, payload)
								new_adID = parsed['ad:ad']['@id']

								# Edit ad id in json file to match new ad id
								item['current_ad_id'] = new_adID
								writeActivate = True
								print('Reposting Completed at: ', now)

						except:
							print('Error: Reposting Failed at: ', now)
							print('Retry Attempt:', i)
							if i < tries - 1: # i is zero indexed
								time.sleep(5)
								continue
						
						else:
							# exit loop if successful
							break
			except:
				print('No Valid Schedules Found')
	
	# Write updates to json file if successful reposting has occurred
	if writeActivate == True:
		print('Updating Schedules')
		with open(scheduleFile, 'w') as jsonFile:
			json.dump(data, jsonFile, indent=4)					


def messageAutoReplier():

	#print('Message Auto Replier: Checking Messages')

	messageFile = os.path.join(THIS_FOLDER, 'static/messages.json')

	with open(messageFile, 'r') as jsonFile:

		data = json.load(jsonFile)
		if len(data['users']) != 0:

			for user in data['users']:

				if len(user['rules']) != 0:

					email = user['useremail']
					password = user['userpassword']
					page = '0' #0 = first 25

					# Retry 20 times if exception raised
					tries = 20
					for i in range(tries):
						try:
							# Login
							userID, userToken = loginFunction(kijijiSession, email, password)
							# Get 25 Most recent Conversations
							conversations = getConversations(kijijiSession, userID, userToken, page)
						except:
							now = datetime.datetime.now()
							print('Error Auto Replier Unable to Login or Get Conversations at:', now)
							print('Retry Attempt:', i)
							if i < tries - 1: # i is zero indexed
								time.sleep(5)
								continue
						else:
							for rule in user['rules']:

								if 'user:user-conversation' in conversations['user:user-conversations']:

									# Initialize Reply Variables
									direction = ''
									replyName = ''
									replyEmail = ''
									content = ''
									conversationID = ''
									adID = ''
									unread = False

									isList = testListInstance(conversations['user:user-conversations']['user:user-conversation'])

									# only 1 conversation
									if isList == False:

										for key, value in conversations['user:user-conversations']['user:user-conversation'].items():							
											sendMessage = False
												
											if key == '@uid':
												conversationID = value

											if key == 'user:num-unread-msg':

												if value != '0':
													unread = True

													conversation = getConversation(kijijiSession, userID, userToken, conversationID)

													adID = conversation['user:user-conversation']['user:ad-id']
													ownerUserID = conversation['user:user-conversation']['user:ad-owner-id']
													ownerEmail = conversation['user:user-conversation']['user:ad-owner-email']
													ownerName = conversation['user:user-conversation']['user:ad-owner-name']
													replierUserID = conversation['user:user-conversation']['user:ad-replier-id']
													replierEmail = conversation['user:user-conversation']['user:ad-replier-email']
													replierName = conversation['user:user-conversation']['user:ad-replier-name']
														
													# Calculate Message Direction
													if ownerUserID == userID:
														replyName = ownerName
														replyEmail = ownerEmail
														direction = 'TO_BUYER'

													elif replierUserID == userID:
														replyName = replierName
														replyEmail = replierEmail
														direction = 'TO_OWNER'

											if key == 'user:user-message':
												for element, attribute in value.items():
													if element == 'user:msg-content':
														content = attribute

											for index, message in rule.items():

												if message in content and unread == True:
													sendMessage = True

												if index == 'response' and sendMessage == True:
													reply = message
													finalPayload = createReplyPayload(adID, replyName, replyEmail, reply, conversationID, direction)
													sendReply(kijijiSession, userID, userToken, finalPayload)

													# Reset Variables for next iteration
													sendMessage = False
													unread = False
													direction = ''
													replyName = ''
													replyEmail = ''
													content = ''
													conversationID = ''
													adID = ''

									# multiple conversations
									else:
										for item in conversations['user:user-conversations']['user:user-conversation']:							
											sendMessage = False
												
											conversationID = item['@uid']

											if item['user:num-unread-msg'] != '0':

												unread = True

												conversation = getConversation(kijijiSession, userID, userToken, conversationID)

												adID = conversation['user:user-conversation']['user:ad-id']
												ownerUserID = conversation['user:user-conversation']['user:ad-owner-id']
												ownerEmail = conversation['user:user-conversation']['user:ad-owner-email']
												ownerName = conversation['user:user-conversation']['user:ad-owner-name']
												replierUserID = conversation['user:user-conversation']['user:ad-replier-id']
												replierEmail = conversation['user:user-conversation']['user:ad-replier-email']
												replierName = conversation['user:user-conversation']['user:ad-replier-name']
														
												# Calculate Message Direction
												if ownerUserID == userID:
													replyName = ownerName
													replyEmail = ownerEmail
													direction = 'TO_BUYER'

												elif replierUserID == userID:
													replyName = replierName
													replyEmail = replierEmail
													direction = 'TO_OWNER'

											for element, attribute in item['user:user-message'].items():
												if element == 'user:msg-content':
													content = attribute

											for index, message in rule.items():

												if message in content and unread == True:
													sendMessage = True

												if index == 'response' and sendMessage == True:
													reply = message
													finalPayload = createReplyPayload(adID, replyName, replyEmail, reply, conversationID, direction)
													sendReply(kijijiSession, userID, userToken, finalPayload)

													# Reset Variables for next iteration
													sendMessage = False
													unread = False
													direction = ''
													replyName = ''
													replyEmail = ''
													content = ''
													conversationID = ''
													adID = ''
							break

# Create Session with Http2.0 compatability for Kijiji separate from Flask local session
# SSL verification disabled to avoid ConnectionPool Max retries exception
# Need to impliment this in future (httpx module still in alpha)
urllib3.disable_warnings()
timeout = httpx.Timeout(15.0, connect_timeout=30.0)
kijijiSession = httpx.Client(verify=False, timeout=timeout)

# Routes:

# http://localhost:5000/ - this will be the login page, we need to use both GET and POST requests
@app.route('/', methods=['GET', 'POST'])
def login():
	# Initialize output message if something goes wrong...
	msg = ''
	# Check if "email" and "password" POST requests exist (user submitted form)
	if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
		
		# Create variables for easy access
		email = request.form['email']
		password = request.form['password']
		
		try:
			userID, userToken = loginFunction(kijijiSession, email, password)
			# Create local session data accessible to other routes
			session['loggedin'] = True
			session['user_id'] = userID
			#session['user_email'] = userEmail #redundant
			session['user_email'] = email
			session['user_token'] = userToken
			# Redirect to home page
			return redirect(url_for('home'))
		except:
			# Account doesnt exist or email/password incorrect
			msg = 'Unable to Access Kijiji Account'
			print('Login Error: Unable to Access Kijiji Account')
			return render_template('index.html', msg=msg)
	else:
		# Show the login form with message (if any)
		return render_template('index.html', msg=msg)

# http://localhost:5000/logout - this will be the logout page
@app.route('/logout')
def logout():
	# Remove session data, this will log the user out
	session.pop('loggedin', None)
	session.pop('user_id', None)
	session.pop('user_email', None)
	session.pop('user_token', None)
	# Redirect to login page
	return redirect(url_for('login'))


# http://localhost:5000/home - this will be the home page, only accessible for loggedin users
@app.route('/home')
def home():
	# Check if user is loggedin
	if 'loggedin' in session:
		# Retrieve Current Ad List
		userID = session['user_id']
		token = session['user_token']
		parsed = getAdList(kijijiSession, userID, token)
		# User is loggedin show them the home page
		return render_template('home.html', email = session['user_email'], data=parsed) #, profileData=profileData)
	else:
		# User is not loggedin redirect to login page
		return redirect(url_for('login'))


# http://localhost:5000/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile():
	# Check if user is loggedin
	if 'loggedin' in session:
		# Retrieve Profile Data
		userID = session['user_id']
		token = session['user_token']
		parsed = getProfile(kijijiSession, userID, token)
		# Show the profile page with account info
		return render_template('profile.html', data=parsed)
	else:
		# User is not loggedin redirect to login page
		return redirect(url_for('login'))


# http://localhost:5000/ad
@app.route('/ad/<adID>')
def ad(adID):
	# Check if user is loggedin
	if 'loggedin' in session:
		# View Ad from kijiji account
		userID = session['user_id']
		token = session['user_token']
		parsed = getAd(kijijiSession, userID, token, adID)
		# Show the profile page with account info
		return render_template('ad.html', data=parsed, adID=adID)
	else:
		# User is not loggedin redirect to login page
		return redirect(url_for('login'))

# http://localhost:5000/post
@app.route('/post', methods=['GET', 'POST'])
def post():
	# Check if user is loggedin
	if 'loggedin' in session:
		# Post An Ad - Stage 1 - Select Category
		xmlfile = os.path.join(THIS_FOLDER, 'static/categories.xml')
		categoriesData = getXML(xmlfile)
		choiceList = []
	
		for x in categoriesData['cat:categories']['cat:category']['cat:category']:
			choiceList.append(x['cat:id-name'])

		form = PostForm()
		form.cat1.choices = choiceList
		
		return render_template('post.html', form=form)
	else:
		# User is not loggedin redirect to login page
		return redirect(url_for('login'))


@app.route('/submit', methods=['GET', 'POST'])
def submit():
	if 'loggedin' in session:
		# Submit Ad for Posting - Final Stage
		# Need to get name from profile
		userID = session['user_id']
		token = session['user_token']
		parsed = getProfile(kijijiSession, userID, token)
		session['user_displayname'] = parsed['user:user-profile']['user:user-display-name']
		
		# Process Form Data
		form = PostForm()
		
		attributes = {}
		attributesPayload = {}
		picturesPayload = {}
		remainders = {}
		locChoice = chooseLocation(form.loc1.data, form.loc2.data, form.loc3.data)
	
		# get submitted form items
		f = request.form
		for key in f.keys():
			for value in f.getlist(key):
				# gather attributes (AttributeForm items)
				# filter out persistent form items to determine dynamic attributes
				if key != 'adtype' and key != 'adtitle' and key != 'cat1' and key != 'cat2' and key != 'cat3' and key != 'description' and key != 'pricetype' and key != 'price' and key != 'loc1' and key != 'loc2' and key != 'postalcode' and key != 'phone' and key != 'file1' and key != 'file2' and key != 'file3' and key != 'file4' and key != 'file5' and key != 'file6' and key != 'file7' and key != 'file8' and key != 'file9' and key != 'file10' and key != 'repost' and key != 'time1' and key != 'time2' and key != 'time3' and key != 'time4' and key != 'time5' and key != 'time6' and key != 'time7' and key != 'time8' and key != 'password':
					attributes[key] = value
				# gathter PostForm items
				else:
					remainders[key] = value


		# Build Attributes Payload
		if len(attributes) != 0:
			attributesPayload = {'attr:attributes':{'attr:attribute': []}}
			for key, value in attributes.items():
				# Correct BOOLEAN Attritubes into correct formatting for kijiji
				if value == True or value == 'y':
					attributesPayload['attr:attributes']['attr:attribute'].append({'@type': '', '@localized-label': '', '@name': key, 'attr:value': 'true'})

				# If above conditions do not apply, and value is not None, append attribute		
				if (value != True or value != 'y') and (value != False or value != 'n') and (value != None and value != ''):
					attributesPayload['attr:attributes']['attr:attribute'].append({'@type': '', '@localized-label': '', '@name': key, 'attr:value': value})

				# set xml type variable for Date based attributes
				if 'date' in key:
					attributesPayload['attr:attributes']['attr:attribute'].append({'@type': 'DATE', '@localized-label': '', '@name': key, 'attr:value': value+'T00:00:00Z'})

		# Collect items from remainders
		#Variable initialization
		adtitle = ''
		description = ''
		adtype = ''
		postalcode = ''
		fulladdress = ''
		pricetype = ''
		price = ''
		fileData1 = b''
		fileData2 = b''
		fileData3 = b''
		fileData4 = b''
		fileData5 = b''
		fileData6 = b''
		fileData7 = b''
		fileData8 = b''
		fileData9 = b''
		fileData10 = b''
		pic1Link = ''
		pic2Link = ''
		pic3Link = ''
		pic4Link = ''
		pic5Link = ''
		pic6Link = ''
		pic7Link = ''
		pic8Link = ''
		pic9Link = ''
		pic10Link = ''
		adID = ''

		# put remainig form data into appropriate variables
		for key, value in remainders.items():
			if key == 'adtitle':
				adtitle = value
			elif key == 'description':
				description = value
			elif key == 'adtype':
				adtype = value
			elif key == 'postalcode':
				postalcode = value
			elif key == 'fulladdress': # still yet to be implimented
				fulladdress = value
			elif key == 'pricetype':
				pricetype = value
			elif key == 'price':
				price = value

		# Begin assembling entire Payload
		responsePayload = {
			'ad:ad': {
				'@xmlns:types': 'http://www.ebayclassifiedsgroup.com/schema/types/v1', 
				'@xmlns:cat': 'http://www.ebayclassifiedsgroup.com/schema/category/v1', 
				'@xmlns:loc': 'http://www.ebayclassifiedsgroup.com/schema/location/v1', 
				'@xmlns:ad': 'http://www.ebayclassifiedsgroup.com/schema/ad/v1', 
				'@xmlns:attr': 'http://www.ebayclassifiedsgroup.com/schema/attribute/v1', 
				'@xmlns:pic': 'http://www.ebayclassifiedsgroup.com/schema/picture/v1', 
				'@xmlns:user': 'http://www.ebayclassifiedsgroup.com/schema/user/v1', 
				'@xmlns:rate': 'http://www.ebayclassifiedsgroup.com/schema/rate/v1', 
				'@xmlns:reply': 'http://www.ebayclassifiedsgroup.com/schema/reply/v1', 
				'@locale': 'en-CA'}}

		
		if adtitle != None and adtitle != '':
			responsePayload['ad:ad'].update({'ad:title': adtitle})
			
		if description != None and description != '':
			responsePayload['ad:ad'].update({'ad:description': description})
			
		if locChoice != None and locChoice != '':
			responsePayload['ad:ad'].update({'loc:locations': {'loc:location': {'@id': locChoice}}})
			
		if adtype != None and adtype != '':
			responsePayload['ad:ad'].update({'ad:ad-type': {'ad:value': adtype}})
			
		if session['cat'] != None and session['cat'] != '':
			responsePayload['ad:ad'].update({'cat:category': {'@id': session['cat']}})
			
		if session['user_email'] != None and session['user_email'] != '':
			responsePayload['ad:ad'].update({'ad:email': session['user_email']})
			
		if session['user_displayname'] != None and session['user_displayname'] != '':
			responsePayload['ad:ad'].update({'ad:poster-contact-name': session['user_displayname']})
			
		if session['user_id'] != None and session['user_id'] != '':
			responsePayload['ad:ad'].update({'ad:account-id': session['user_id']})
			
		if (postalcode != None and postalcode != '') or (fulladdress != None and fulladdress != ''):
			responsePayload['ad:ad'].update({'ad:ad-address': {}})
			
			if postalcode != None and postalcode != '':
				responsePayload['ad:ad']['ad:ad-address'].update({'types:zip-code': postalcode})
				
			if fulladdress != None and fulladdress != '':
				responsePayload['ad:ad']['ad:ad-address'].update({'types:full-address': fulladdress})

		if (pricetype != None and pricetype != '') or (price != None and price != ''):
			responsePayload['ad:ad'].update({'ad:price': {}})

			if pricetype != None and pricetype != '':
				responsePayload['ad:ad']['ad:price'].update({'types:price-type':{'types:value': pricetype}})
				
			if price != None and price != '':
				responsePayload['ad:ad']['ad:price'].update({'types:amount': price})

		# add attributes payload if attributes payload exist
		if len(attributesPayload) != 0:
			responsePayload['ad:ad'].update(attributesPayload)

		# Verify and Upload Pictures
		# Retreive Uploaded Picure Link
		# picLink function calls #picUpload function
		if (form.file1.data != None and form.file1.data != '' and form.file1.data != b'') or (form.file2.data != None and form.file2.data != '' and form.file2.data != b'') or (form.file3.data != None and form.file3.data != '' and form.file3.data != b'') or (form.file4.data != None and form.file4.data != '' and form.file4.data != b'') or (form.file5.data != None and form.file5.data != '' and form.file5.data != b'') or (form.file6.data != None and form.file6.data != '' and form.file6.data != b'') or (form.file7.data != None and form.file7.data != '' and form.file7.data != b'') or (form.file8.data != None and form.file8.data != '' and form.file8.data != b'') or (form.file9.data != None and form.file9.data != '' and form.file9.data != b'') or (form.file10.data != None and form.file10.data != '' and form.file10.data != b''):
			
			pic1Link = picLink(form.file1.data, kijijiSession)
			pic2Link = picLink(form.file2.data, kijijiSession)
			pic3Link = picLink(form.file3.data, kijijiSession)
			pic4Link = picLink(form.file4.data, kijijiSession)
			pic5Link = picLink(form.file5.data, kijijiSession)
			pic6Link = picLink(form.file6.data, kijijiSession)
			pic7Link = picLink(form.file7.data, kijijiSession)
			pic8Link = picLink(form.file8.data, kijijiSession)
			pic9Link = picLink(form.file9.data, kijijiSession)
			pic10Link = picLink(form.file10.data, kijijiSession)

		# Create Picture Payload
		if (pic1Link != None and pic1Link != '') or (pic2Link != None and pic2Link != '') or (pic3Link != None and pic3Link != '') or (pic4Link != None and pic4Link != '') or (pic5Link != None and pic5Link != '') or (pic6Link != None and pic6Link != '') or (pic7Link != None and pic7Link != '') or (pic8Link != None and pic8Link != '') or (pic9Link != None and pic9Link != '') or (pic10Link != None and pic10Link != ''):
			picturesPayload = {'pic:pictures':{'pic:picture': []}}

			if pic1Link != None and pic1Link != '':
				picturesPayload['pic:pictures']['pic:picture'].append({'pic:link': { '@rel': 'saved', '@href': pic1Link}})
				
			if pic2Link != None and pic2Link != '':
				picturesPayload['pic:pictures']['pic:picture'].append({'pic:link': { '@rel': 'saved', '@href': pic2Link}})
				
			if pic3Link != None and pic3Link != '':
				picturesPayload['pic:pictures']['pic:picture'].append({'pic:link': { '@rel': 'saved', '@href': pic3Link}})
				
			if pic4Link != None and pic4Link != '':
				picturesPayload['pic:pictures']['pic:picture'].append({'pic:link': { '@rel': 'saved', '@href': pic4Link}})
				
			if pic5Link != None and pic5Link != '':
				picturesPayload['pic:pictures']['pic:picture'].append({'pic:link': { '@rel': 'saved', '@href': pic5Link}})
				
			if pic6Link != None and pic6Link != '':
				picturesPayload['pic:pictures']['pic:picture'].append({'pic:link': { '@rel': 'saved', '@href': pic6Link}})
				
			if pic7Link != None and pic7Link != '':
				picturesPayload['pic:pictures']['pic:picture'].append({'pic:link': { '@rel': 'saved', '@href': pic7Link}})
				
			if pic8Link != None and pic8Link != '':
				picturesPayload['pic:pictures']['pic:picture'].append({'pic:link': { '@rel': 'saved', '@href': pic8Link}})
				
			if pic9Link != None and pic9Link != '':
				picturesPayload['pic:pictures']['pic:picture'].append({'pic:link': { '@rel': 'saved', '@href': pic9Link}})
				
			if pic10Link != None and pic10Link != '':
				picturesPayload['pic:pictures']['pic:picture'].append({'pic:link': { '@rel': 'saved', '@href': pic10Link}})
				

		# add attributes payload if attributes payload exist
		if len(picturesPayload) != 0:
			responsePayload['ad:ad'].update(picturesPayload)

		# Parse final payload into XML
		finalPayload = xmltodict.unparse(responsePayload, short_empty_elements=True, pretty=True)

		# Debug Option to evaluate Submissions
		# if debugMode = True, will not submit final payload
		# and instead prints to console for evaluation
		debugMode = False

		if debugMode == True:
			print(finalPayload)
		
		if debugMode == False:
			# Submit Final Payload
			parsed = submitFunction(kijijiSession, userID, token, finalPayload)
			# Retreive Ad ID# for newly posted Ad
			adID = parsed['ad:ad']['@id']
			
			# Create Repost Data
			if form.repost.data == True:
				# check if user path exists
				# if not create it
				# write ad file to user directory
				path = 'user/' + session['user_id']
				userDir = os.path.exists(path)
				if userDir == True:
					# write ad to file
					with open(path + '/' + adID + '.xml', 'w') as w:
						w.write(finalPayload)
				else:
					#create directory
					os.makedirs(path)
					#write ad to file
					with open(path + '/' + adID + '.xml', 'w') as w:
						w.write(finalPayload)
				
				# Update schedules.json with repost information
				useremail = session['user_email']
				userpassword = form.password.data
				ad_file = path + '/' + adID + '.xml'
				ad_id = adID

				newSchedule = {
					'time1': timeValidator(form.time1.data),
					'time2': timeValidator(form.time2.data),
					'time3': timeValidator(form.time3.data),
					'time4': timeValidator(form.time4.data),
					'time5': timeValidator(form.time5.data),
					'time6': timeValidator(form.time6.data),
					'time7': timeValidator(form.time7.data),
					'time8': timeValidator(form.time8.data),
					'useremail': useremail, 
					'userpassword': userpassword,
					'ad_file': ad_file,
					'current_ad_id': ad_id
					}

				jsonFile = 'static/schedules.json'

				with open(jsonFile, 'r') as json_file: 
					data = json.load(json_file) 
					update = data['schedules'] 
					update.append(newSchedule)

				with open(jsonFile,'w') as json_file: 
					json.dump(data, json_file, indent=4)

		return redirect(url_for('home'))
	else:
		return redirect(url_for('login'))

@app.route('/cat/<choice>')
def category_choice(choice):

	xmlfile = os.path.join(THIS_FOLDER, 'static/categories.xml')
	categoriesData = getXML(xmlfile)
	choiceList = []
	for x in categoriesData['cat:categories']['cat:category']['cat:category']:
		try:
			if x['cat:id-name'] == choice:
				for y in x['cat:category']:
					choiceObj = {}
					choiceObj['id'] = y['@id']
					choiceObj['name'] = y['cat:id-name']
					choiceList.append(choiceObj)
		except:
			choiceObj = {}
			choiceObj['id'] = ''
			choiceObj['name'] = ''
			choiceList.append(choiceObj)		

	return jsonify(choiceList)


@app.route('/cat2/<choice>')
def category_choice2(choice):
	split = choice.split('~')

	xmlfile = os.path.join(THIS_FOLDER, 'static/categories.xml')
	categoriesData = getXML(xmlfile)
	choiceList = []
	
	for x in categoriesData['cat:categories']['cat:category']['cat:category']:
		if x['cat:id-name'] == split[0]:
			try:
				for y in x['cat:category']:
					try:
						if y['@id'] == split[1]:
							for z in y['cat:category']:
								choiceObj = {}
								choiceObj['id'] = z['@id']
								choiceObj['name'] = z['cat:id-name']
								choiceList.append(choiceObj)
					except:
						choiceObj = {}
						choiceObj['id'] = ''
						choiceObj['name'] = ''
						choiceList.append(choiceObj)
			except:
				print('No Sub-Categories')
	
	return jsonify(choiceList)

@app.route('/loc/<choice>')
def location_choice(choice):

	xmlfile = os.path.join(THIS_FOLDER, 'static/locations.xml')
	locationData = getXML(xmlfile)
	choiceList = []
	for x in locationData['loc:locations']['loc:location']['loc:location']:
		try:
			if x['loc:localized-name'] == choice:
				for y in x['loc:location']:
					choiceObj = {}
					choiceObj['id'] = y['@id']
					choiceObj['name'] = y['loc:localized-name']
					choiceObj['long'] = y['loc:longitude']
					choiceObj['lat'] = y['loc:latitude']
					choiceList.append(choiceObj)
		except:
			choiceObj = {}
			choiceObj['id'] = ''
			choiceObj['name'] = ''
			choiceObj['long'] = ''
			choiceObj['lat'] = ''
			choiceList.append(choiceObj)		

	return jsonify(choiceList)

@app.route('/loc2/<choice>')
def location_choice2(choice):
	split = choice.split('~')
	xmlfile = os.path.join(THIS_FOLDER, 'static/locations.xml')
	locationData = getXML(xmlfile)
	choiceList = []
	
	for x in locationData['loc:locations']['loc:location']['loc:location']:
		try:
			if x['loc:localized-name'] == split[0]:
				for y in x['loc:location']:
					if y['@id'] == split[1]:
						for z in y['loc:location']:
							choiceObj = {}
							choiceObj['id'] = z['@id']
							choiceObj['name'] = z['loc:localized-name']
							choiceObj['long'] = z['loc:longitude']
							choiceObj['lat'] = z['loc:latitude']
							choiceList.append(choiceObj)

		except:
			choiceObj = {}
			choiceObj['id'] = ''
			choiceObj['name'] = ''
			choiceObj['long'] = ''
			choiceObj['lat'] = ''
			choiceList.append(choiceObj)		

	return jsonify(choiceList)


@app.route('/attributes', methods=['GET', 'POST'])
def attributes():
	if 'loggedin' in session:

		postForm = PostForm()
		catChoice = chooseCategory(postForm.cat1.data, postForm.cat2.data, postForm.cat3.data)

		# create session variable to pass category choice to stage2.html
		session['cat'] = catChoice 
		
		# Location Options
		xmlfile = os.path.join(THIS_FOLDER, 'static/locations.xml')
		locationsData = getXML(xmlfile)
		locationList = []

		try:
			for y in locationsData['loc:locations']['loc:location']['loc:location']:
				locationList.append(y['loc:localized-name'])
		except:
			locationList.append(locationsData['loc:locations']['loc:location']['loc:localized-name'])

		postForm.loc1.choices = locationList

		attributesFile = os.path.join(THIS_FOLDER, 'static/attributes/' + catChoice)
		with open(attributesFile, 'r') as f:
			file = f.read()
			parsed = xmltodict.parse(file)

		# Update Ad Type Choices based on xml items
		# Currently static, but allows for future flexibility
		try:
			items = [(x['#text'], x['@localized-label']) for x in parsed['ad:ad']['ad:ad-type']['ad:supported-value']]
			postForm.adtype.choices = items
		except:
			print('No Ad Types Available')
		
		# Begin Parsing Attributes xml for selected category
		# Initialize Attribute Containers
		enumDict = {'enums':[]}
		stringDict = {'strings':[]}
		integerDict = {'integers':[]}
		dateDict = {'dates':[]}
		boolDict = {'bools':[]}
		exceptDict = {'excepts':[]}

		if 'attr:attribute' in parsed['ad:ad']['attr:attributes']:

			try:

				for x in parsed['ad:ad']['attr:attributes']['attr:attribute']:

					# Parse ENUM Types
					if x['@deprecated'] == 'false' and x['@write'] != 'unsupported' and x['@type'] == 'ENUM':

						newitem = { 
							'label': {
								x['@name']: x['@localized-label']
								},
							'choices': {}
							}

						if 'attr:supported-value' in x:		
							for y in x['attr:supported-value']:

								newitem['choices'].update({y['#text']: y['@localized-label']})

						enumDict['enums'].append(newitem)

					# Parse STRING Types
					if x['@deprecated'] == 'false' and x['@write'] != 'unsupported' and x['@type'] == 'STRING':
									
						newitem = { 
							'label': {
								x['@name']: x['@localized-label']
								}
							}

						stringDict['strings'].append(newitem)

					# Parse INTEGER Types
					if x['@deprecated'] == 'false' and x['@write'] != 'unsupported' and x['@type'] == 'INTEGER':
									
						newitem = { 
							'label': {
								x['@name']: x['@localized-label']
								}
							}

						integerDict['integers'].append(newitem)
					
					# Parse DATE Types
					if x['@deprecated'] == 'false' and x['@write'] != 'unsupported' and x['@type'] == 'DATE':
									
						newitem = { 
							'label': {
								x['@name']: x['@localized-label']
								}
							}

						dateDict['dates'].append(newitem)

					# Parse BOOLEAN Types
					if x['@deprecated'] == 'false' and x['@write'] != 'unsupported' and x['@type'] == 'BOOLEAN':

						newitem = { 
							'label': {
								x['@name']: x['@localized-label']
								}
							}

						boolDict['bools'].append(newitem)
			except:
				print('No Standard Attributes Found, Attempting Defaults')
				# Attempt Default Parsing - Assumes ENUM Type
				name = ''
				label = ''
				choices = []
				for key, value in parsed['ad:ad']['attr:attributes']['attr:attribute'].items():
					
					if key == '@localized-label':
						label = value
					if key == '@name':
						name = value
					if key == 'attr:supported-value':

						newitem = { 
							'label': {
								name: label
								},
							'choices': {}
							}

						for item in value:

							newitem['choices'].update({item['#text']: item['@localized-label']})

						exceptDict['excepts'].append(newitem)

		# Dynamic Forms for Attributes (temporary class)
		class AttributeForm(FlaskForm):
			class Meta:
				csrf = False

		# Create Dyname Form Attributes / Elements
		# Create ENUM Type Attributes
		for item in enumDict['enums']:

			labels = []
			choices = []
				
			for labelAttribute in item['label'].items():
				labels.append(labelAttribute)
				fieldID = labelAttribute[0]
				title = labelAttribute[1]
					
				for choiceAttribute in item['choices'].items():
					choices.append(choiceAttribute)

			setattr(AttributeForm, fieldID, SelectField(title, choices=choices))
			choices = []

		# Create STRING Type Attributes
		for item in stringDict['strings']:
			for labelAttribute in item['label'].items():
				fieldID = labelAttribute[0]
				title = labelAttribute[1]
				setattr(AttributeForm, fieldID, TextField(title))

		# Create INTEGER Type Attributes
		for item in integerDict['integers']:
			for labelAttribute in item['label'].items():
				fieldID = labelAttribute[0]
				title = labelAttribute[1]
				setattr(AttributeForm, fieldID, IntegerField(title))

		# Create DATE Type Attributes
		for item in dateDict['dates']:
			for labelAttribute in item['label'].items():
				fieldID = labelAttribute[0]
				title = labelAttribute[1]
				setattr(AttributeForm, fieldID, DateField(title))

		# Create BOOLEAN Type Attributes
		for item in boolDict['bools']:
			for labelAttribute in item['label'].items():
				fieldID = labelAttribute[0]
				title = labelAttribute[1]
				setattr(AttributeForm, fieldID, BooleanField(title))

		# Create Attributes for Anything Caught by Exceptions during attributes xml parsing
		# Assumes ENUM Type
		for item in exceptDict['excepts']:

			labels = []
			choices = []
				
			for labelAttribute in item['label'].items():
				labels.append(labelAttribute)
				fieldID = labelAttribute[0]
				title = labelAttribute[1]
					
				for choiceAttribute in item['choices'].items():
					choices.append(choiceAttribute)

			setattr(AttributeForm, fieldID, SelectField(title, choices=choices))
			choices = []
		
		# Initialize Dynamic Form at the End, after elements have been generated
		attribForm = AttributeForm()
		
		return render_template('stage2.html', postForm=postForm, attribForm=attribForm, attrib=catChoice)
	else:
		return redirect(url_for('login'))

@app.route('/make/<choice>', methods=['GET', 'POST'])
def make_choice(choice):

	split = choice.split('~')

	attributesFile = os.path.join(THIS_FOLDER, 'static/attributes/' + split[1])
	attributeData = getXML(attributesFile)
	choiceList = []

	for x in attributeData['ad:ad']['attr:dependent-attributes']['attr:dependent-attribute']['attr:dependent-supported-value']:
		try:

			if x['attr:supported-value']['#text'] == split[0]:

				for y in x['attr:dependent-attribute']['attr:supported-value']:
					choiceObj = {}
					choiceObj['name'] = y['@localized-label']
					choiceObj['id'] = y['#text']
					choiceList.append(choiceObj)
		except:
			print('error')
			choiceObj = {}
			choiceObj['name'] = ''
			choiceObj['id'] = ''
			choiceList.append(choiceObj)		

	return jsonify(choiceList)


# http://localhost:5000/delete
@app.route('/delete/<adID>')
def delete(adID):
	# Check if user is loggedin
	if 'loggedin' in session:
		# delete ad from kijiji account
		userID = session['user_id']
		token = session['user_token']
		deleteAd(kijijiSession, userID, adID, token)

		# Remove Schedule associated with ad
		scheduleFile = os.path.join(THIS_FOLDER, 'static/schedules.json')
		with open(scheduleFile, 'r') as f:
			data = json.load(f)

		for item in range(len(data['schedules'])):
			if data['schedules'][item]['current_ad_id'] == adID:
				del data['schedules'][item]
				break

		with open(scheduleFile,'w') as f:
			json.dump(data, f, indent=4)
		
		return redirect(url_for('home'))
	else:
		# User is not loggedin redirect to login page
		return redirect(url_for('login'))

@app.route('/schedule/<adID>', methods=['GET', 'POST'])
def schedule(adID):

	if 'loggedin' in session:
		
		scheduleFile = os.path.join(THIS_FOLDER, 'static/schedules.json')
		with open(scheduleFile, 'r') as f:
			data = json.load(f)
			schedules = []
			for item in data['schedules']:
				if item['current_ad_id'] == adID:
					times = [item['time1'],item['time2'],item['time3'],item['time4'],item['time5'],item['time6'],item['time7'],item['time8']]
					schedules.extend(times)

		return render_template('schedule.html', schedules=schedules, adID=adID)
	else:
		return redirect(url_for('login'))			

@app.route('/reschedule', methods=['GET', 'POST'])
def reschedule():
	# variable initialization
	time1 = ''
	time2 = ''
	time3 = ''
	time4 = ''
	time5 = ''
	time6 = ''
	time7 = ''
	time8 = ''
	adID = ''
	r = request.form
	for key, value in r.items():
		if key == 'time1':
			time1 = value
		elif key == 'time2':
			time2 = value
		elif key == 'time3':
			time3 = value
		elif key == 'time4':
			time4 = value
		elif key == 'time5':
			time5 = value
		elif key == 'time6':
			time6 = value
		elif key == 'time7':
			time7 = value
		elif key == 'time8':
			time8 = value
		elif key == 'adID':
			adID = value

	scheduleFile = os.path.join(THIS_FOLDER, 'static/schedules.json')
	with open(scheduleFile, 'r') as f:
		data = json.load(f)
		for item in data['schedules']:
			if item['current_ad_id'] == adID:

				if time1 == 'NONE':
					item['time1'] = None
				elif time1 != '' and time1 != None:
					item['time1'] = time1

				if time2 == 'NONE':
					item['time2'] = None
				elif time2 != '' and time2 != None:
					item['time2'] = time2
					
				if time3 == 'NONE':
					item['time3'] = None
				elif time3 != '' and time3 != None:
					item['time3'] = time3
					
				if time4 == 'NONE':
					item['time4'] = None
				elif time4 != '' and time4 != None:
					item['time4'] = time4
					
				if time5 == 'NONE':
					item['time5'] = None
				elif time5 != '' and time5 != None:
					item['time5'] = time5
					
				if time6 == 'NONE':
					item['time6'] = None
				elif time6 != '' and time6 != None:
					item['time6'] = time6
					
				if time7 == 'NONE':
					item['time7'] = None
				elif time7 != '' and time7 != None:
					item['time7'] = time7
					
				if time8 == 'NONE':
					item['time8'] = None
				elif time8 != '' and time8 != None:
					item['time8'] = time8	

	with open(scheduleFile, 'w') as f:
			json.dump(data, f, indent=4)
					
	return redirect(url_for('home'))

@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.template_filter('convert')
def unix_timestamp_to_string_date(unix_time):
	try:
		cut_time = unix_time.replace('Z', '')
		converted = datetime.datetime.strptime(cut_time, '%Y-%m-%dT%H:%M:%S.%f')
		return converted
	except:
		return None

# Grabs first thumbnail image for each ad in users ad list for home page
@app.template_filter('imgparse')
def parse(data):
	try:
		for p in data['pic:pictures']['pic:picture']:
			try:
				for x in p['pic:link']:
					parsed = x['@href']
					return parsed
			except:
				for x in data['pic:pictures']['pic:picture']['pic:link']:
					parsed = x['@href']
					return parsed
		
	except:
		print('Error Parsing Images or No Image to Return')
		return None

# Builds a list of image urls for individual ad page
@app.template_filter('imglist')
def buildImgList(data):
	image_list = []
	try:
		for p in data['pic:pictures']['pic:picture']:
			try:
				for x in p['pic:link']:
					image_list.append(x['@href'])
			except:
				for x in data['pic:pictures']['pic:picture']['pic:link']:
					image_list.append(x['@href'])
		
	except:
		print('Error Parsing Images or No Image to Return')
		empty = ''
		return empty
	return image_list

@app.template_filter('checkSchedule')
def checkSchedule(adID):

	scheduleFile = os.path.join(THIS_FOLDER, 'static/schedules.json')
	with open(scheduleFile, 'r') as f:
		data = json.load(f)

		for item in data['schedules']:
			if item['current_ad_id'] == adID:
				return True

# if list, then more than one ad
@app.template_filter('testlist')
def testlist(data):
	if isinstance(data['ad:ads']['ad:ad'],list):
		return True

# if list, then more than one ad
@app.template_filter('testreplylist')
def testreplylist(conversation):
	if isinstance(conversation['user:user-conversation']['user:user-message'],list):
		return True

# Force Post
@app.route('/force', methods=['GET', 'POST'])
def force():

	if 'loggedin' in session:

			return render_template('force.html')
	else:
		return redirect(url_for('login'))


@app.route('/forcepost', methods=['GET', 'POST'])
def forcepost():

	if 'loggedin' in session:

		now = datetime.datetime.now()

		try:
			
			# Variable Initialization
			file = ''
			email = ''
			password = ''

			# Get Form Data
			r = request.form
			for key, value in r.items():
				if key == 'file':
					file = value
				elif key == 'email':
					email = value
				elif key == 'password':
					password = value
		
			# Login
			userID, userToken = loginFunction(kijijiSession, email, password)

			# Open file / Get payload
			with open(file, 'r') as f:
				payload = f.read()

			# Post Ad
			parsed = submitFunction(kijijiSession, userID, userToken, payload)

			print('Forced Reposting Completed at: ', now)

		except:
			print('Error: Forced Reposting Failed at: ', now)
	
		return redirect(url_for('force'))
	else:
		return redirect(url_for('login'))


# Conversations
@app.route('/conversations/<page>', methods=['GET', 'POST'])
def conversations(page):

	if 'loggedin' in session:

		# Get Credentials
		userID = session['user_id']
		token = session['user_token']
		# Fetch Mail
		conversations = getConversations(kijijiSession, userID, token, page)
			
		return render_template('conversations.html', conversations = conversations, page=page)
	else:
		return redirect(url_for('login'))

@app.template_filter('increment')
def increment(page):
	if page is not None and page != 'None':
		newpage = (int(page) + 1)
		link = '/conversations/' + str(newpage)
		return link

@app.route('/conversation/<conversationID>', methods=['GET', 'POST'])
def conversation(conversationID):

	if 'loggedin' in session:

		# Get Credentials
		userID = session['user_id']
		token = session['user_token']
		#Set form
		form = ConversationForm()
		# Fetch Mail
		conversation = getConversation(kijijiSession, userID, token, conversationID)
		
		return render_template('conversation.html', conversation = conversation, form=form)
	else:
		return redirect(url_for('login'))

@app.route('/reply/<info>', methods=['GET', 'POST'])
def reply(info):

	if 'loggedin' in session:

		# Get Credentials
		userID = session['user_id']
		token = session['user_token']
		#Set form
		form = ConversationForm()
		#Get Reply Data
		reply = form.reply.data
		# Split data elements from info variable
		data = info.split('~')
		conversationID = data[0]
		adID = data[1]
		ownerUserID = data[2]
		ownerEmail = data[3]
		ownerName = data[4]
		replierUserID = data[5]
		replierEmail = data[6]
		replierName = data[7]
		# Initialize Reply Variables
		direction = ''
		replyName = ''
		replyEmail = ''
		if ownerUserID == userID:
			replyName = ownerName
			replyEmail = ownerEmail
			direction = 'TO_BUYER'

		elif replierUserID == userID:
			replyName = replierName
			replyEmail = replierEmail
			direction = 'TO_OWNER'

		# Create final payload
		finalPayload = createReplyPayload(adID, replyName, replyEmail, reply, conversationID, direction)

		# Send Reply
		sendReply(kijijiSession, userID, token, finalPayload)
		
		# Refresh Conversation
		time.sleep(2)
		return redirect(url_for('conversation', conversationID=conversationID))
	else:
		return redirect(url_for('login'))

# Message Auto Replier
@app.route('/autoreplier', methods=['GET', 'POST'])
def autoreplier():

	if 'loggedin' in session:

		messagesFile = os.path.join(THIS_FOLDER, 'static/messages.json')
		
		# Get Credentials
		userID = session['user_id']
		userEmail = session['user_email']
		
		with open(messagesFile, 'r') as f:
			data = json.load(f)
			rules = {}
			for item in data['users']:
				if item['user'] == userID:
					rules = item
			
		return render_template('autoreplier.html', userID=userID, userEmail = userEmail, rules=rules)
	else:
		return redirect(url_for('login'))

# Add New Rule to Auto Replier
@app.route('/updatereplier', methods=['GET', 'POST'])
def updatereplier():

	if 'loggedin' in session:
		
		# Variable Initialization
		userID = ''
		userEmail = ''
		password = ''
		rule = ''
		response = ''

		# Retrieve Form Data
		r = request.form

		for key, value in r.items():
			if key == 'userID':
				userID = value
			elif key == 'userEmail':
				userEmail = value
			elif key == 'rule':
				rule = value
			elif key == 'response':
				response = value
			elif key == 'password':
				password = value

		messagesFile = os.path.join(THIS_FOLDER, 'static/messages.json')
		
		# search to see if user exists
		# if not, use complete 
		# if user does exist, just append basic
		
		newRuleComplete = {
			"user": userID,
			"useremail": userEmail,
			"userpassword": password,
			"rules": [
				{
					"rule": rule,
					"response": response
				}
			]
		}

		newRuleBasic = {
			"rule": rule,
			"response": response
		}
		
		with open(messagesFile, 'r') as json_file: 
			data = json.load(json_file) 
			
			if len(data['users']) != 0:
				for item in data['users']:
					if item['user'] == userID:
						update = item['rules']
						update.append(newRuleBasic)

				for item in data['users']:
					if item['user'] != userID:
						update = data['users']
						update.append(newRuleComplete)
			else:
				update = data['users']
				update.append(newRuleComplete)

		
		with open(messagesFile,'w') as json_file: 
			json.dump(data, json_file, indent=4)

		# Retreive Updated rules to send to autoreplier page
		with open(messagesFile, 'r') as f:
			data = json.load(f)
			rules = {}
			for item in data['users']:
				if item['user'] == userID:
					rules = item

		return redirect(url_for('autoreplier', userID=userID, userEmail = userEmail, rules=rules))	
	else:
		return redirect(url_for('login'))

# Run Scheduler as Daemon in Background
sched = BackgroundScheduler(daemon=True)
sched.add_job(reposter,'cron',minute='*') # every minute
sched.add_job(messageAutoReplier,'cron',minute='*/25') # every 25 minutes
sched.start()
atexit.register(lambda: sched.shutdown())

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', use_reloader=False) # disable reloader, messes with apscheduler
