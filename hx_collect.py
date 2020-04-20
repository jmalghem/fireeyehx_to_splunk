# This script get your FireEye HX Alerts and print it to stdout in json format.
# Last polled index is stored in the file 'fireeye_hx_last_id.txt' stored with the script
# Author : jmalghem@gmail.com
from __future__ import division
import requests, json, math, sys, os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

iMinID=0
iPageSize=5
# Replace XXXXXX by base64 encoded username:password
headers={ 'Authorization' : 'Basic XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' }
# Replace by the URL of your Cloud HX Controller
HXController = 'YYYYYYYY'
# Path to the file containing the last recorded event
last_eventid_filepath = os.path.dirname(os.path.abspath(__file__)) + '/fireeye_hx_last_id.txt' 

# Open file containing the last event ID and get the last record read
if os.path.isfile(last_eventid_filepath):
    try:
        last_eventid_file = open(last_eventid_filepath,'r')
        iMinID = int(last_eventid_file.readline())
        last_eventid_file.close()
    # Catch the exception. Real exception handler would be more robust    
    except IOError:
        sys.stderr.write('Error: failed to read last eventid file, ' + last_eventid_filepath + '\n')
        sys.exit(2)
else:
    sys.stderr.write('Error: ' + last_eventid_filepath + ' file not found! Starting from zero. \n')

## AUTH
try:
	r = requests.get('https://' + HXController + '/hx/api/v3/token', headers=headers, verify=False)
	tok = r.headers.get('X-FeApi-Token')
	authHeader = { 'X-FeApi-Token' : tok }
except:
	sys.stderr.write("FIREEYEHX - AUTHENTICATION : Unexpected error:", sys.exc_info()[0])
	sys.exit(2)

## Get last generated id & calculate number of pages based on the page size
try:
	rA = requests.get('https://' + HXController + '/hx/api/v3/alerts?limit=1&sort=_id%2Bdesc', 	headers=authHeader, verify=False)
	iLastID = rA.json()["data"]["entries"][0]["_id"]
	iPageNumber = int(math.ceil((iLastID - iMinID) / iPageSize))
except:
	sys.stderr.write("FIREEYEHX - COLLECT LAST ALERT ID : Unexpected error:", sys.exc_info()[0])
	sys.exit(2)

## Iterate iPageNumber times to collect data

for i in range(iMinID,iLastID+1,iPageSize):
	rA = requests.get('https://' + HXController + '/hx/api/v3/alerts?min_id='+str(i)+'&limit='+str(iPageSize)+'&sort=_id%2Basc', headers=authHeader, verify=False)
	for each in rA.json()["data"]["entries"]:
		print(json.dumps(each))

if iLastID > 0:
   try:
     sys.stderr.write('Write to file the last ID : ' + str(iLastID))
     last_eventid_file = open(last_eventid_filepath,'w')
     last_eventid_file.write(str(iLastID))
     last_eventid_file.close()
   # Catch the exception. Real exception handler would be more robust    
   except IOError:
     sys.stderr.write('Error writing last_eventid to file: ' + last_eventid_filepath + '\n')
     sys.exit(2)

