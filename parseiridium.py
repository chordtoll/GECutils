#from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import base64
from bs4 import BeautifulSoup


def decb64(b64):
		mul=1
		val=0
		for i in b64:
			if i==' ':
				continue
			if i=='+':
				cval=62
			elif i=='/':
				cval=63
			elif i<'A':
				cval=ord(i)-ord('0')+52
			elif i<'a':
				cval=ord(i)-ord('A')+0
			else:
				cval=ord(i)-ord('a')+26
			val+=cval*mul
			mul*=64
		return val

def dm2d(i):
  i/=1000000.0
  d=int(i)
  m=(i-d)*100
  return d+m/60.0


# Setup the Gmail API
SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('gmail', 'v1', http=creds.authorize(Http()))

# Call the Gmail API
unread_msgs = service.users().messages().list(userId='me',labelIds=['INBOX','UNREAD']).execute()
msg_list = unread_msgs['messages']
print ("Total unread messages in inbox: ", str(len(msg_list)))

for msg in msg_list:
  m_id = msg['id'] # get id of individual message
  message = service.users().messages().get(userId='me', id=m_id).execute()
  payld = message['payload']
  headr = payld['headers']
  #print(payld)
  if 'parts' not in payld:
      continue
  msg_parts = payld['parts'] # fetching the message parts
  part_one  = msg_parts[0] # fetching first element of the part
  part_body = part_one['body'] # fetching body of the message
  part_data = part_body['data'] # fetching data from the body
  clean_one = part_data.replace("-","+") # decoding from Base64 to UTF-8
  clean_one = clean_one.replace("_","/") # decoding from Base64 to UTF-8
  clean_two = base64.b64decode (str(clean_one)) # decoding from Base64 to UTF-8
  soup = BeautifulSoup(clean_two , "lxml" )
  messagecontent=soup.body.p.text.encode('utf8','replace')
  pack=messagecontent.split('\r\n')[9]
  bTime=pack[:9]
  bLati=pack[9:18]
  bLong=pack[18:28]
  bAlti=pack[28:33]
  #print bTime+':'+bLati+':'+bLong+':'+bAlti+':'+pack[33:]
  #print 'Time:%d(%s)'%(decb64(bTime),bTime.lstrip())
  #print 'Lati:%f(%s)'%(dm2d(decb64(bLati)),bLati.lstrip())
  #print 'Long:%f(%s)'%(dm2d(decb64(bLong)),bLong.lstrip())
  #print 'Alti:%f(%s)'%(decb64(bAlti)/10.0,bAlti.lstrip())
  #print 'Location:%f, -%f'%(dm2d(decb64(bLati)),dm2d(decb64(bLong)))
  print '%f, %f <green-dot>'%(dm2d(decb64(bLati)),-dm2d(decb64(bLong)))
  #print(soup.string.encode('utf8', 'replace'))


#service.users().messages().modify(userId=user_id, id=m_id,body={ 'removeLabelIds': ['UNREAD']}).execute()
