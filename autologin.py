import sys, os
from threading import Timer
from urllib import urlopen, urlencode
from getpass import getpass

# Globals (putting here just for reference):
welcome_message = \
'''
FOB Cobra Microtik Auto-Login
Created by mhweaver, 2011

Advanced usage (for shortcuts and stuff): autologin.exe [-u username] [-p password] [-i interval] [-fQ] [-fD]
  -u username | Microtik username
  -p password | Microtik password
  -i interval | Number of seconds between login attempts. If no interval is 
              |   provided, a default of 30 seconds is used.
  -fQ         | Keep attempting to log in after your daily bandwidth quota has
              |   been reached.
  -fD         | Keep attempting to log in after login has been denied to due a
              |   bad username/password.

To exit, press CTRL-Break or just close this window.

'''
username = ''
password = ''
interval = 0
debug_mode = False
quota_halt = True
denied_halt = True
timer_count = 0

def main():
	# Welcome screen/information
	os.system('cls')
	print welcome_message
	
	# Gather all required information and put it in the global scope.

	if '-u' in sys.argv:
		username_index = sys.argv.index('-u') + 1
		if len(sys.argv) >= username_index + 1:
			globals()['username'] = sys.argv[username_index]
			print 'Username: ' + username
		else:
			globals()['username'] = raw_input('Username: ')
	else:
		globals()['username'] = raw_input('Username: ')

	if '-p' in sys.argv:
		password_index = sys.argv.index('-p') + 1
		if len(sys.argv) >= password_index + 1:
			globals()['password'] = sys.argv[password_index]
			# This takes the password and gives you a '******' mask of the same length
			print 'Password: ' + ('*' * len(password))
		else:
			globals()['password'] = getpass('Password: ')
	else:
		globals()['password'] = getpass('Password: ')

	if '-i' in sys.argv:
		interval_index = sys.argv.index('-i') + 1
		if len(sys.argv) >= interval_index + 1:
			globals()['interval'] = sys.argv[interval_index]
			print 'Log in attempt interval: ' + str(interval) + ' seconds'
		else:
			globals()['interval'] = 30
			print 'Log in attempt interval: ' + str(interval) + ' seconds'
	else:
		globals()['interval'] = 30
	
	if '-fQ' in sys.argv:
		globals()['quota_halt'] = False
		print 'Will ignore exceeded bandwidth quota errors and continue.'
	if '-fD' in sys.argv:
		globals()['denied_halt'] = False
		print 'Will ignore invalid username/password errors and continue.'
	globals()['debug_mode'] = '--debug' in sys.argv

	
	globals()['timer_count'] = 0 # Used for debug mode

	print '\n\nRunning... Attempting to periodically log into microtik.\n'

	# Kick off the timer. Let's get this ball rolling!
	start_timer()
	

def check_login():
	# Check to see if you are logged in.
	# Returns True if logged in, otherwise False
	
	f = urlopen('http://www.mhweaver.com/')
	response = f.read(4096)
	lines = response.splitlines()

	if debug_mode: print response
	return not (len(lines) >= 11) and (lines[10].strip() == "<LoginURL>http://www.cobra.com/login?target=xml</LoginURL>")

	
def login(user, passwd):
	lines = []
	try:
		params = urlencode({'username': user, 'password': passwd, 'dst': '', 'popup': ''})
		f = urlopen('http://192.168.1.1/login', params)
		# cobra.com for aerostat, .net for room. WTF?!?!?
		response = f.read(4096)
		lines = response.splitlines()
	except:
		pass
	if debug_mode: 
		print response
		#print 'line 40 - ' + lines[84]
		
		#return True
	if len(lines) >= 85 and lines[84].strip() == '<br /><div style="color: #FF8080; font-size: 9px">invalid username or password</div>':
		return 'Username/Password'	
	if len(lines) >= 41 and lines[40].strip() == 'You are logged in':
		return 'Success'
	elif len(lines) >= 84 and lines[84].strip() == '<br /><div style="color: #FF8080; font-size: 9px">user mhweaver has reached traffic limit</div>':
		return 'Quota'
	else:
		return 'Failed'
	

def start_timer():
	
	globals()['timer_count'] = globals()['timer_count'] + 1
	if debug_mode: print 'Attempt #' + str(globals()['timer_count']) + ' starting.'
	
	
	success = login(username, password)
	halt = False
	if success == 'Success':
		print 'Log in attempt successful.'
	elif success == 'Failed':
		print 'Log in attempted failed, but not due to bad username/password. \nTrying again in ' + str(interval) + ' seconds.'
	elif success == 'Quota':
		print 'Log in attempt failed - bandwidth quota exceeded.'
		halt = halt or quota_halt
	elif success == 'Username/Password': 
		print 'Log in attempt failed due to bad username/password.'
		halt = halt or denied_halt
		
	if debug_mode: print '#' + str(globals()['timer_count'])
	
	if halt: # We don't want to keep trying/failing when we get rejected for these reasons.
		print '\n\nStopping. Press <ENTER> to exit.'
		getpass('') # Pause script
	
	else:
		t = Timer(int(interval), start_timer)
		t.start()

	
if __name__ == '__main__':
	main()