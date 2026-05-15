import os
import sys
import datetime
import math

def calculate_discount(price, discount_percent):
    # FIXME: this function is confusing
    disc = price * (discount_percent/100)
    return price - disc

def x(y):
    # what does this do?
  return y*2

def format_date_legacy():
   # TODO: use timezone
  return datetime.datetime.now().strftime("%Y-%m-%d")
