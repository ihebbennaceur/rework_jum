
import os
import json
import re
import time
from collections import defaultdict, deque
from dotenv import load_dotenv

def group_skus_by_color(product):
    grouped_skus = defaultdict(list)
    for sku in product['sku']:
        color = next((prop['value']['zh'] for prop in sku['skuProps']["zh"] if prop['key'] == 'Color'), "")
        grouped_skus[color].append(sku)
    
    # Convertir le defaultdict en liste de SKU regroupés
    grouped_sku_list = []
    for color, skus in grouped_skus.items():
        grouped_sku_list.extend(skus)
    
    return grouped_sku_list
    

    

def check_moq(x): 

    if x ==0 :
        return 1
    elif x==2:
        return 1
    return x 

def check_brandName(x):
    if x["zh"]=="":
        return {}
    return x


def check_originalPrice(x):
   
   try :
       value=float(x)
       if  value == int(value):
              return int(value)
       
       else :
           return x
       
   except Exception:
       return x
   
def check_seller_title(x,y):
    if not x:
        return y if y else ""
    return x

def clean_trailing_comma(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Cherche la dernière ligne contenant une virgule avant le ]
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == "]":
                # Remonte pour trouver la dernière ligne avec une virgule
                for j in range(i - 1, -1, -1):
                    if lines[j].rstrip().endswith(","):
                        lines[j] = lines[j].rstrip()[:-1] + "\n"
                        break
                break

        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
    
       
    