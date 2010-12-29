boxee.enableLog(true);
boxee.renderBrowser = false;
boxee.useBoxeeCookies=true;
boxee.autoChoosePlayer = false;

boxee.setCanPause(true);
boxee.setCanSkip(false);
boxee.setCanSetVolume(true);

var detected = false;
var player = 'JSFANCASTCONTAINER.fancastContainer';

function startPlaying() {
    _loader = setInterval(
        function() {
            percentLoaded = parseInt(browser.execute('document.fancastVideoContainer.PercentLoaded();'));
            if (percentLoaded == 100) {
                var w = boxee.getActiveWidget();
                browser.execute(player + ".playVid();");
                //boxee.getActiveWidget().click(w.width - 5, w.height - 5);
                clearInterval(_loader);
            }
        },
        500);
}

function detectVideo() {
    if (!detected) {
        boxee.getWidgets().forEach(function(w) {
            if (w.getAttribute("id") == "fancastVideoContainer") {
                detected=true;
                boxee.notifyConfigChange(w.width,w.height);
                w.setCrop(0, 0, 0, 0);
                //w.setCrop(0, 0, 0, 33);
                w.setActive(true);
                setTimeout(startPlaying, 6000);
            } else {
                w.setActive(false);
            }
        });
        
        setTimeout(detectVideo, 500);
    }
}

boxee.onDocumentLoaded = function() {
    detectVideo();
}

boxee.onPause = function() {
    browser.execute(player + ".pauseVid();");
}
 
boxee.onPlay = function() {
   browser.execute(player+'.playVid();');
}
 
boxee.onSkip = function() {
   //current = Number(browser.execute(player+'.getCurrentTime()'))+10;
   //browser.execute(player+'.seekTo('+current+');')
}
 
boxee.onBigSkip = function() {
   //current = Number(browser.execute(player+'.getCurrentTime()'))+25;
   //browser.execute(player+'.seekTo('+current+');')
}
 
boxee.onBack = function() {
   //current = Number(browser.execute(player+'.getCurrentTime()'))-10;
   //browser.execute(player+'.seekTo('+current+')')
}
 
boxee.onBigBack = function() {
   //current = Number(browser.execute(player+'.getCurrentTime()'))-25;
   //browser.execute(player+'.seekTo('+current+')')
}
 
boxee.onSetVolume = function(volume) {
   var vol = volume/100;
   browser.execute(player+'.volumeChange('+vol+');');
}
