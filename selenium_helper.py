# coding: utf-8

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

outdir_ss = './file/ss/'
driver = None
ss_seq = 1
is_save_html_with_ss = False
user_agent = ''

#class SeleniumHelper():
#    def __init__(self, driver, ss_outdir):
#        self.driver = driver
#        self.ss_outdir = ss_outdir
#        self.seq = 1
#    def ss(self, seq=None, name='ss'):
#        '''
#        スクリーンショットを撮る
#        '''
#        out_seq = self.seq if seq is None else seq
#        fname = '{}/{}_{}.png'.format(self.ss_outdir,out_seq,name)
#        log.debug("ss fname ={}".format(fname))
#        self.driver.get_screenshot_as_file(fname)
#        self.seq += 1
#        return fname

def start_browser():
    global driver
    options = Options()
    options.add_argument('--headless')
    if user_agent != '':
        options.add_argument('--user-agent='+user_agent)
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(10)
    # windowサイズを変更
    win_size = driver.get_window_size()
    driver.set_window_size(win_size['width']+200,win_size['height']+400)
    return driver;

def set_download(outdir):
    global driver
    driver.command_executor._commands["send_command"] = (
        "POST",
        '/session/$sessionId/chromium/send_command'
    )
    params = {
        'cmd': 'Page.setDownloadBehavior',
        'params': {
            'behavior': 'allow',
            'downloadPath': outdir
        }
    }
    driver.execute("send_command", params=params)

def get_downloaded_filename(outdir):
    if len(os.listdir(outdir)) == 0:
        return None
    return max (
        [os.path.join(outdir, f) for f in os.listdir(outdir)], key=os.path.getctime
    )

def ss(seq=None, name='ss'):
    '''
    スクリーンショットを撮る
    '''
    global driver
    global ss_seq
    seq = ss_seq if seq is None else seq
    fname = os.path.join(outdir_ss,'{}_{}.png'.format(seq,name))
    driver.get_screenshot_as_file(fname)
    if is_save_html_with_ss:
        ps(seq,name)
    ss_seq += 1
    return fname

def ps(seq=None, name='ss'):
    '''
    HTMLソースを保存
    '''
    global driver
    global ss_seq
    seq = ss_seq if seq is None else seq
    fname = os.path.join(outdir_ss,'{}_{}.html'.format(seq,name))
    with open(fname, 'wt') as out:
        out.write(driver.page_source)
    return fname

if __name__ == '__main__':
    pass
#    helper = SeleniumHelper()

