import mc
import re
import urllib
import myhttp
import xfinity

app_id = 'xfinity'
use_rss = True

###############################################################################
##  Events                                                                   ##
###############################################################################
def play():
    """
    Play authenticated content with a cookie to be passed to the browser.
    """
    item = _getSelectedItem(200)
    url = item.GetPath()
    url = urllib.quote_plus(xfinity.getVideoPath(url))
    jsactions = urllib.quote_plus(xfinity.getBoxeeJSAction())
    cookie = urllib.quote_plus(xfinity.getBoxeeCookie())

    # Build flash link with cookie and jsactions url
    flash_link = 'flash://www.fancast.com/src=%s&bx-cookie=%s&bx-jsactions=%s'
    item_path = flash_link % (url, cookie, jsactions)

    # Play content
    item.SetPath(item_path)
    mc.GetPlayer().Play(item)


def jumpToLetter():
    """
    Jump to selected letter.
    """
    item = _getSelectedItem(300)
    list = mc.GetActiveWindow().GetList(100)

    letter = item.GetLabel()
    if letter == '*':
        list.SetFocusedItem(0)
    elif letter == '#':
        list.JumpToLetter('0')
    else:
        list.JumpToLetter(letter)


def showTitles():
    """
    Show title list.
    """
    _hideShowControl(200, 100)


def showEpisodes():
    """
    Show episode list of selected title.
    """
    path = _getSelectedPath(100)
    if use_rss:
        mc.GetActiveWindow().GetList(200).SetContentURL(path)
    else:
        m = re.search('(\d+)\.xml', path)
        code = m.group(1)
        print code
        episodes = xfinity.XFinityTitle(code).getEpisodes()

        items = mc.ListItems()
        for k, v in episodes.iteritems():
            item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_OTHER)
            item.SetLabel(str(k))
            item.SetPath(str(v))
            items.append(item)
        mc.GetActiveWindow().GetList(200).SetItems(items)

    _hideShowControl(100, 200)


def goToList():
    lists = [100, 200]

    for l in lists:
        control = mc.GetWindow(14000).GetControl(l)
        if control.IsVisible():
            control.SetFocus()
            break


def login():
    """
    Display login and password dialogs.
    Store them in the local configuration.
    """
    if True:
        alert('Functionality not yet supported')
        return

    user = ''
    passw = ''
    config = mc.GetApp().GetLocalConfig()

    if config.GetValue('xfinity.user'):
        user = config.GetValue('xfinity.user')

    if config.GetValue('xfinity.pass'):
        passw = config.GetValue('xfinity.pass')

    user = mc.ShowDialogKeyboard('xfinity username', user, False)
    passw = mc.ShowDialogKeyboard('password', passw, True)

    # Store user
    config.SetValue('xfinity.user', user)

    cookies = xfinity.login(user, passw)
    if cookies:
        # Store password and cookies
        config.SetValue('xfinity.pass', passw)
        for k, v in cookies.iteritems():
            config.SetValue('xfinity.cookies.'+k, v)


def options():
    """
    Display option dialog.
    """
    mc.ShowDialogOk('xfinity - options', 'Nothing here at the moment')


def search():
    """
    Display search dialog.
    """
    alert('Functionality not yet supported')


def about():
    """
    Display about dialog.
    """
    about = """Unofficial xfinity.tv app
Version 0.1
Copyright © 2011 Mariano Cano
GNU General Public License v2.0
"""
    mc.ShowDialogOk('xfinity - about', about)


###############################################################################
##  Tasks                                                                    ##
###############################################################################
def populateLetters():
    """
    Add list items with each letter in the list 300
    """
    abc = ['*', '#', 'A', 'B', 'C',
           'D', 'E', 'F', 'G', 'H',
           'I', 'K', 'L', 'M', 'N',
           'O', 'P', 'Q', 'R', 'S',
           'T', 'V', 'X', 'Y', 'Z']

    items = mc.ListItems()
    for l in abc:
        item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
        item.SetLabel(l)
        item.SetPath(l)
        items.append(item)

    mc.GetActiveWindow().GetList(300).SetItems(items)


def populateTitles():
    items = mc.ListItems()
    # TODO
    mc.GetActiveWindow().GetList(100).SetItems(items)


###############################################################################
##  Helpers                                                                  ##
###############################################################################
def log(s):
    """
    Log a message using boxee logger.
    """
    message = '@xfinity: %s' % str(s)
    mc.LogInfo(message)


def alert(msg):
    """
    Show a dialog with a simple message.
    """
    mc.ShowDialogOk('xfinity', msg)

def _getSelectedItem(list):
    """
    Get the selected item in a list
    """
    list = mc.GetActiveWindow().GetList(list)
    itemNumber = list.GetFocusedItem()
    return list.GetItem(itemNumber)


def _getSelectedPath(list):
    """
    Get the path of the selected element in a list
    """
    item = _getSelectedItem(list)
    return item.GetPath()


def _hideShowControl(hide, show):
    """
    Hide a control and show another.
    """
    control = mc.GetWindow(14000).GetControl(hide)
    control.SetVisible(False)

    control = mc.GetWindow(14000).GetControl(show)
    control.SetVisible(True)
    control.SetFocus()


###############################################################################
##  Main: activate main window                                               ##
###############################################################################
mc.ActivateWindow(14000)

