import sys, os
from threading import Timer
from urllib import urlopen, urlencode
from getpass import getpass
from argparse import ArgumentParser

# Globals (putting here just for reference):
welcome_message = \
'''
FOB Cobra Microtik Auto-Login
Created by mhweaver, 2011

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
    
    parser = ArgumentParser()
    parser.add_argument('-u', dest='username', action='store', type=str, metavar='<username>', default=None,
                        help='Microtik username')
    parser.add_argument('-p', dest='password', action='store', type=str, metavar='<password>', default=None,
                        help='Microtik password')
    parser.add_argument('-i', dest='interval', action='store', type=int, metavar='<seconds>', default=30,
                        help='Number of seconds between login attempts (default: 30)')
    parser.add_argument('--quota-ignore', dest='ignore_quota', action='store_true', 
                        help='Keep attempting to log in after daily bandwidth quota has been exceeded.')
    parser.add_argument('--ignore-bad-password', dest='ignore_denied', action='store_true',
                        help='Keep attempting to log in after login has been denied due to bad username/password.')
    parser.add_argument('--debug', dest='debug_mode', action='store_true', help='Show debug information.')
    options = parser.parse_args()
    
    if options.username:
        globals()['username'] = options.username
        print 'Username: %s' % (options.username)
    else:
        globals()['username'] = raw_input('Username: ')
    if options.password:
        globals()['password'] = options.password
        print 'Password: %s' % ('*' * len(password))
    else:
        globals()['password'] = getpass('Password: ') 
    globals()['interval'] = 30 if not options.interval else options.interval
    if options.ignore_quota:
        globals()['quota_halt'] = False
        print 'Will ignore exceeded bandwidth quota errors and continue.'
    if options.ignore_denied:
        globals()['denied_halt'] = False
        print 'Will ignore invalid username/password errors and continue.'
    globals()['debug_mode'] = True if options.debug_mode else False
    
    
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