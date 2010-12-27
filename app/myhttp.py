import mc

class MyHttp(mc.Http):
    
    def __init__(self, *args, **kwds):
        self._referer = None
        self._url = None
        super(MyHttp, self).__init__(*args, **kwds)
        
    def Get(self, url):
        self._beforeRequest(url)
        data = super(MyHttp, self).Get(url)
        data2 = self._afterRequest(url)
        if data2:
            return data2
        return data

    def Post(self, url, urlEncodedPostData):
        self._beforeRequest(url)
        data = super(MyHttp, self).Post(url, urlEncodedPostData)
        data2 = self._afterRequest(url)
        if data2:
            return data2
        return data

    def GetUrl(self):
        return self._url

    def _beforeRequest(self, url):
        self._url = url
        if self._referer:
            self.SetHttpHeader('Request', self._referer)
            
    def _afterRequest(self, url):
        self._referer = url
        if self.GetHttpResponseCode() == 302:
            location = self.GetHttpHeader('location')
            return self.Get(location)
        return None
