import mc
import re
import urllib
import urllib2
import xml.dom.minidom
from BeautifulSoup import BeautifulSoup
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
    new_path = path + '?autoPlay=true&u=c&skipTo=0&skin=xfinity#'
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

    
class XFinityTvSeries:
    """
    Class to parse www.fancast.com full-episodes page like:
    http://www.fancast.com/tv/House/11954/full-episodes
    """
    
    def __init__(self, url=None, code=None):
        self._code = None
        self._url = None
        self._episodes = []
        
        if url:
            self._url = url
            self._code = self.getTitleCode()
        elif code:
            self._code = code
            self._url = self.getEpisodesUrl()
        else:
            raise TypeError('Required argument url or code')

        self.parse()
        

    def parse(self):
        f = urllib2.urlopen(self._url)
        data = f.read()
        episodes = []
        
        soup = BeautifulSoup(data)
        firsts = soup.findAll('td', attrs={'class':'first'})
        for f in firsts:
            link = f.find('a', attrs={'class':'fcHover'})
            desc = f.find('p', attrs={'class':'desc'})
            d = {
                'title': link.string.strip(),
                'description': desc.string.strip(),
                'image': f.img['src'],
                'season': '0',
                'number': '0',
                'path': 'http://www.fancast.com' + link['href']
                }
            episodes.append(d)

        twos = soup.findAll('td', attrs={'class':'two'})
        i = 0
        for t in twos:
            m = re.search("S(\d+)\s+\|\s+Ep(\d+)", t.string)
            if m:
                episodes[i]['season'] = m.group(1)
                episodes[i]['number'] = m.group(2)
            i += 1

        for e in episodes:
            self._episodes.append(XFinityEpisode(data=e))
        
            
    def getEpisodes(self):
        return self._episodes


    def getTitleCode(self):
        if not self._code and self._url:
            m = re.search("/(\d+)/full-episodes", self._url)
            self._code = m.group(1)
        return self._code
        

    def getEpisodesUrl(self):
        if not self._url and self._code:
            self._url = 'http://www.fancast.com/tv/xxx/%s/full-episodes' % self._code
        return self._url
        

    def _getText(self, nodes):
        rc = []
        for node in nodes:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return re.sub("\s+", " ", ''.join(rc)).strip(' ')


class XFinityEpisode:
    
    def __init__(self, tv_serie_id=None, episode_id=None, data=None):
        self._tvid = tv_serie_id
        self._epid = episode_id
        self._data = {}

        if tv_serie_id and episode_id:
            self._api = 'http://www.fancast.com/api/video/summary/TvSeries-%s/Video-%s' % (tv_serie_id, episode_id)
            self._parse(self._api)
        elif data:
            self._data = data
        else:
            raise TypeError("Parameters data or tv_serie_id and episode_id needs to be defined")

    def _parse(self, url):
        f = urllib2.urlopen(url)
        dom = xml.dom.minidom.parse(f)

        self._data['title'] = str(dom.getElementsByTagName('episodeTitle')[0].firstChild.data)
        self._data['description'] = str(dom.getElementsByTagName('episodeSeasonNumber')[0].firstChild.data)
        self._data['image'] = str(dom.getElementsByTagName('videoThumbnailUrl')[0].firstChild.data)
        self._data['season'] = dom.getElementsByTagName('episodeSeasonNumber')[0].firstChild.data
        self._data['number'] = dom.getElementsByTagName('episodeNumber')[0].firstChild.data
        self._data['path'] = 'http://www.fancast.com/tv/xxx/%s/%s/yyy/videos' % (tv_serie_id, episode_id)

    def getTitle(self):
        return self._data['title'].encode("iso-8859-15", "xmlcharrefreplace")

    def getDescription(self):
        return self._data['description'].encode("iso-8859-15", "xmlcharrefreplace")

    def getImage(self):
        return self._data['image'].encode("iso-8859-15")

    def getPath(self):
        return self._data['path'].encode("iso-8859-15")

    def getSeason(self):
        return int(self._data['season'])

    def getNumber(self):
        return int(self._data['number'])
    

class XFinityTitleList:
    
    def __init__(self, db='http://www.fancast.com/full_episodes_db.widget'):
        self._base = 'http://www.fancast.com'
        self._db = db
        self._titles = []
        self._parse()


    def _parse(self):
        f = urllib2.urlopen(self._db)
        data = f.read()
        data = re.sub("'([a-z])", "' \\1", data.replace('&', '&amp;'))
        dom = xml.dom.minidom.parseString(data)
        elements = dom.getElementsByTagName('b')

        for b in elements:
            code = str(b.attributes['id'].value)
            t = (
                b.firstChild.data.encode("iso-8859-15", "xmlcharrefreplace"),
                code,
                self._base + b.attributes['u'].value.encode("iso-8859-15", "xmlcharrefreplace"),
                self._base + '/api/entity/thumbnail/TvSeries-' + code + '/147/106'
                )
            self._titles.append(t)

        # Order by title:
        self._titles = sorted(self._titles, key=lambda x: x[0].lower())


    def getTitles(self):
        return self._titles


if __name__ == '__main__':
    #test = XFinityTitle(code=11954)
    #print test.getEpisodes()
    test = XFinityTvSeries(url='http://www.fancast.com/tv/House/11954/full-episodes')
    print test.getEpisodes()[0].__dict__
    #test = XFinityTitleList()
    #titles = test.getTitles()
    #for t in titles:
    #    print t[0]
    
