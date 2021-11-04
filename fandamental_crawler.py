# coding: utf-8

import logging,logging.handlers
import sys
import os
from argparse import ArgumentParser
import selenium_helper as helper
import time
import datetime
import selenium.common.exceptions
import pandas as pd

OUTDIR_SS='./log/ss/fandamental/'
OUTDIR='./data/fandamental_data/'
LOGDIR='./log/'

# ログ設定
ap_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(ap_name)
log.setLevel(logging.DEBUG)
h = logging.handlers.TimedRotatingFileHandler(os.path.join(LOGDIR,'{}.log'.format(ap_name)),'D',2,13)
h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
log.addHandler(h)
h = logging.StreamHandler(sys.stdout)
log.addHandler(h)

log.info("start")

outdir = OUTDIR
outdir_ss = OUTDIR_SS
log.info("outdir={}".format(outdir))
log.info("outdir_ss={}".format(outdir_ss))

log.info("reading targets.txt..")
code_df = pd.read_csv("data/fandamental_data/targets.txt",header=None,names=['code'])
#log.debug(code_df)


log.info("getting fandamentals..")
df = pd.DataFrame(index=[], columns=["コード","日付","業種","PER","PBR","利回り","信用倍率"])
# 処理開始
try:
    driver = helper.start_browser()
    helper.outdir_ss = outdir_ss
    helper.set_download(outdir)
    helper.is_save_html_with_ss = True
    driver.set_page_load_timeout(60)

    for i,cr in code_df.iterrows():
      cd = cr.code
      # =IMPORTXML("https://kabutan.jp/stock/?code="&$A1,"//div[@class='company_block']/table/tbody/tr[3]/td[1]/text()")
      driver.get("https://kabutan.jp/stock/?code={}".format(cd))
      time.sleep(3)
      helper.ss(name="{}_stock".format(cd))
      e_per = driver.find_element_by_xpath("//div[@id='stockinfo_i3']/table/tbody/tr[1]/td[1]")
      e_pbr = driver.find_element_by_xpath("//div[@id='stockinfo_i3']/table/tbody/tr[1]/td[2]")
      e_rim = driver.find_element_by_xpath("//div[@id='stockinfo_i3']/table/tbody/tr[1]/td[3]")
      e_shi = driver.find_element_by_xpath("//div[@id='stockinfo_i3']/table/tbody/tr[1]/td[4]")
      e_gyo = driver.find_element_by_xpath("//div[@id='stockinfo_i2']/div/a")
      e_date = driver.find_element_by_xpath("//div[@id='kobetsu_left']/h2/time")
#      r = pd.Series([cd,e_date.get_attribute("dateeime"),e_gyo.text,e_per.text.replace("倍",""),
#                    e_pbr.text.replace("倍",""),e_rim.text.replace("％",""),e_shi.text.replace("倍","")], index=df.columns)
      r = pd.Series([cd,e_date.get_attribute("datetime"),e_gyo.text,e_per.text,
                    e_pbr.text,e_rim.text,e_shi.text], index=df.columns)
      df = df.append(r,ignore_index=True)
#      log.debug("getting fandamentals code={},per={},pbr={},rim={},shin={},gyo={}".format(cd,e_per.text,e_pbr.text,e_rim.text,e_shi.text,e_gyo.text))
#      break
    df.to_csv(os.path.join(OUTDIR,"fandamental.csv"),index=False)
    df.to_csv(os.path.join(OUTDIR,"fandamental_{}.csv".format(datetime.datetime.now().strftime("%Y%m%d"))),index=False)
    log.debug(df)
except Exception as e:
    log.exception('exception occurred.')
    print(e, file=sys.stderr)

finally:
    if ( driver is not None ):
        driver.quit()
        log.info("WebDriver Quit")
    log.info("end")

log.info("exit")
exit();

'''
  yc = cr.yahoo_code
  log.info("Getting {}:{},{}".format(i,yc,cr["銘柄名"]))
  my_share = share.Share(yc)
  symbol_data = None
  try:
    symbol_data = my_share.get_historical(
                  share.PERIOD_TYPE_DAY, 10,
#                  share.PERIOD_TYPE_DAY, 100,
#                  share.PERIOD_TYPE_YEAR, 10,
                  share.FREQUENCY_TYPE_DAY, 1)
#                  share.FREQUENCY_TYPE_MONTH, 1)
  except YahooFinanceError as e:
    log.error("Yahoo Finance Error! {}:{},{}".format(e.message,yc,cr["銘柄名"]))
    continue

  if symbol_data is None:
    log.info("{}/{} is None".format(yc,cr["銘柄名"]))
    continue

  tmpdf = pd.DataFrame(symbol_data)
  tmpdf["datetime"] = pd.to_datetime(tmpdf.timestamp, unit="ms")
  tmpdf["code_y"] = yc
  tmpdf["code"] = yc[0:4]
  ordered_tmp = tmpdf[["code","datetime","open","high","low","close","volume","code_y"]]
  if sdf is None:
    sdf = ordered_tmp
  else:
    sdf = sdf.append(ordered_tmp)
    sdf.to_csv(os.path.join(OUTDIR,"trans_daily.csv"),index=False)
#    sdf.to_csv("data/transaction_data/trans_100hist_daily.csv",index=False)
#    sdf.to_csv("data/transaction_data/trans_hist_monthly.csv",index=False)
#  if i > 10:
#     break

log.info("get transaction end!")

sdf.to_csv(os.path.join(OUTDIR,"trans_daily_{}.csv".format(datetime.datetime.now().strftime("%Y%m%d"))),index=False)


log.info("end")
'''
