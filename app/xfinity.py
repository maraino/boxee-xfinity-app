import mc
import re
import urllib
import urllib2
import xml.dom.minidom
import html5lib
from html5lib import treebuilders
import myhttp

def login(user, passw):
    """
    Login in fancast using comcast SSO.
    Returns a dictionary with the authentication cookies.
    Not working at this moment.
    """
    auth = {'user': user, 'passwd': passw, 'remember': 1,
            'pf_sp': 'www.fancast.com', 'rm': 2,
            'deviceAuthn': 'false', 'forceAuthn': 'false',
            's': 'sso-pf', 'r': 'comcast.net',
            'continue': 'https://idp.comcast.net/idp/resumeSAML20/idp/startSSO.ping?response=1',
            'lang': 'en'}

    http = myhttp.MyHttp()

    # Step 1: Go to fancast
    http.Get('http://www.fancast.com/')

    # Step 2: SSO Ping
    data = http.Get('https://idp.comcast.net/idp/startSSO.ping?PartnerSpId=www.fancast.com&CID=fancast_header_signin&TARGET=%2F')

    # Step 3: Comcast Login
    data = http.Post('https://login.comcast.net/login', urllib.urlencode(auth))

    # Step 4: SSO Ping to Fancast
    dom = xml.dom.minidom.parseString(data)
    forms = dom.getElementsByTagName('form')
    if len(forms) > 0:
        dom = forms[0]
        action = str(dom.attributes['action'].value)
        inputs = dom.getElementsByTagName('input')
        form = {}
        for el in inputs:
            if el.attributes.get('name', False):
                form[el.attributes['name'].value] = el.attributes['value'].value

        http.Post(action, urllib.urlencode(form))
        print http.GetHttpHeader('Set-Cookie')

    # Step 5: Go to fancast
    http.Get('http://www.fancast.com/')

    cookies = {}
    return cookies


def getVideoPath(path):
    """
    Build the url from the video url present in the video links.
    """
    #new_path = path.replace('/videos', '/embed?skipTo=0&skin=xfinity#')
    new_path = path + '?skipTo=0&skin=xfinity#'
    return new_path


def getBoxeeJSAction():
    #return 'http://dl.dropbox.com/u/2343163/xfinity/boxee-control.js'
    return ''


def getBoxeeCookie():
    config = mc.GetApp().GetLocalConfig()

    # Check for authentication cookies in the local configuration
    lfc = ''
    if config.GetValue('xfinity.cookies.lfc'):
        lfc = config.GetValue('xfinity.cookies.lfc')
    
    slfc = ''
    if config.GetValue('xfinity.cookies.slfc'):
        slfc = config.GetValue('xfinity.cookies.slfc')
    
    cookie = ''
    if lfc or slfc:
        cookie = 'lfc=%s; slfc=%s; ' % (lfc, slfc)
    
    return cookie


def sortVideos():
    pass

    
class XFinityTitle:
    """
    Class to parse www.fancast.com episodes
    """
    
    def __init__(self, code):
        self._code = code
        self._episodes = {}
        self._url = self.buildFullEpisodesUrl(code)
        self.parse()


    def parse(self):
        #data = self._get(self._url)
        f = urllib2.urlopen(self._url)
        parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
        dom = parser.parse(f)

        if not dom:
            return False

        tds = dom.getElementsByTagName('td')

        numbers = []
        names = []
        hrefs = []
        for td in tds:
            if td.attributes.get('class', False) and td.attributes['class'].value == 'first':
                links = td.getElementsByTagName('a')
                for link in links:
                    if link.attributes.get('class', False) and link.attributes['class'].value == 'fcHover':
                        hrefs.append(link.attributes['href'].value)
                        names.append(self._getText(link.childNodes))

            elif td.attributes.get('class', False) and td.attributes['class'].value == 'two':
                numbers.append(self._getText(td.childNodes))

        size = len(numbers)
        for i in range(size):
            key = numbers[i] + ' - ' + names[i]
            self._episodes[key] = 'http://www.fancast.com' + hrefs[i]


    def getEpisodes(self):
        return self._episodes


    def buildFullEpisodesUrl(self, code):
        return 'http://www.fancast.com/tv/xxx/%s/full-episodes' % code
        

    def _getText(self, nodes):
        rc = []
        for node in nodes:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return re.sub("\s+", " ", ''.join(rc)).strip(' ')
            

if __name__ == '__main__':
    test = XFinityTitle(11954)
    print test.getEpisodes()
