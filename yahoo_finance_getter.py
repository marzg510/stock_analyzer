# coding: utf-8

import logging,logging.handlers
import sys
import os
from argparse import ArgumentParser
import time
import datetime
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError
import pandas as pd

OUTDIR='./data/transaction_data/'
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

log.info("reading codes.csv..")
code_df = pd.read_csv("data/stock_code/codes.csv")
code_df["code"] = (code_df["コード"]/10).astype(int).astype(str)
code_df["yahoo_code"] = code_df.code+".T"

log.info("getting transactions..")
sdf = None
for i,cr in code_df.iterrows():
  time.sleep(1)
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