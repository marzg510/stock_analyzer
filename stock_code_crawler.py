# coding: utf-8

import logging,logging.handlers
import sys
import os
from argparse import ArgumentParser
import selenium_helper as helper
import time
import selenium.common.exceptions
import pandas as pd

OUTDIR_SS='./log/ss/'
OUTDIR='./data/stock_code/'
LOGDIR='./log/'

# ログ設定
ap_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(ap_name)
log.setLevel(logging.DEBUG)
h = logging.handlers.TimedRotatingFileHandler('{}/{}.log'.format(LOGDIR,ap_name),'D',2,13)
h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
log.addHandler(h)
h = logging.StreamHandler(sys.stdout)
log.addHandler(h)

log.info("start")

outdir = OUTDIR
outdir_ss = OUTDIR_SS
log.info("outdir={}".format(outdir))
log.info("outdir_ss={}".format(outdir_ss))

# 処理開始
try:
    driver = helper.start_browser()
    helper.outdir_ss = outdir_ss
    helper.set_download(outdir)
    helper.is_save_html_with_ss = True
    driver.set_page_load_timeout(60)

    # 東証上場会社情報サービス検索
    log.info("getting search page")
    driver.get('https://www2.tse.or.jp/tseHpFront/JJK010010Action.do?Show=Show')
    time.sleep(1)
    helper.ss(name='search_page')
    # チェックボックスをONに
    e_chkbox_area = driver.find_element_by_xpath('//th[.="市場区分"]/following-sibling::td')
    log.debug(e_chkbox_area.get_attribute("outerHTML"))
    e_chkboxes = e_chkbox_area.find_elements_by_xpath('.//input[@type="checkbox"]')
    for e in e_chkboxes:
        log.debug(e.get_attribute("outerHTML"))
#        if ( e.get_attribute("value")!="ETN"):
#            continue
        e.click()
    helper.ss(name='search_page_chk_on')
    # 検索
    e_button = driver.find_element_by_xpath('//input[@type="button" and @name="searchButton"]')
    log.debug(e_button.get_attribute("outerHTML"))
    e_button.click()
    time.sleep(3)

    page_no = 1

    # ページ読み取り
    df = pd.DataFrame(index=[], columns=["コード","銘柄名","市場区分","本社所在地","業務分類","決算期","売買単位",
                                         "支配株主等に関する事項","注意情報等","継続企業の前提の注記"])
    while True:
        helper.ss(name='search_result_page_{}'.format(page_no))
        e_trs = driver.find_elements_by_xpath('//table[@class="tableStyle01 fontsizeS"]//tr/td/..')
        for i,e_tr in enumerate(e_trs):
#            log.debug("{},{}".format(i,e_tr.get_attribute("outerHTML")))
            if i % 2 == 0:  # 偶数行（見た目は奇数行）のとき
                e_code = e_tr.find_element_by_xpath('.//td[1]')
                e_market = e_tr.find_element_by_xpath('.//td[2]')
                e_honsha = e_tr.find_element_by_xpath('.//td[3]')
                e_kessan = e_tr.find_element_by_xpath('.//td[4]')
                e_unit = e_tr.find_element_by_xpath('.//td[5]')
                e_shihai = e_tr.find_element_by_xpath('.//td[6]')
                e_warn = e_tr.find_element_by_xpath('.//td[7]')
                e_warn2 = e_tr.find_element_by_xpath('.//td[8]')
            else:
                e_name = e_tr.find_element_by_xpath('.//td[1]')
                e_biz_class = e_tr.find_element_by_xpath('.//td[2]')
                r = pd.Series([e_code.text,e_name.text,e_market.text,e_honsha.text,e_biz_class.text,e_kessan.text,e_unit.text,e_shihai.text,e_warn.text,e_warn2.text],
                                index=df.columns)
                df = df.append(r,ignore_index=True)
#                log.debug("{},{},{},{}".format(i,e_code.text,e_name.text,e_market.text))
        # 次へボタンを押す
        try:
            e_next = driver.find_element_by_xpath('//img[@alt="次へ"]')
        except selenium.common.exceptions.NoSuchElementException:
            break
        e_next.click()
        time.sleep(3)
        page_no += 1
        log.info("next page={}".format(page_no))
    # csv出力処理
    # TODO:implement
    df.to_csv("{}/codes.csv".format(OUTDIR),index=False)
    log.debug(df)

except Exception as e:
    log.exception('exception occurred.')
    print(e, file=sys.stderr)

finally:
    if ( driver is not None ):
        driver.quit()
        log.info("WebDriver Quit")
    log.info("end")

exit()

