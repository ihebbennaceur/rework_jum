#################################################
liste_color=["color","颜色","颜色分类"]
#################################################
import requests
import json
from datetime import datetime
import random
import os
import time
from collections import defaultdict, deque
from dotenv import load_dotenv
import s1_utils.new_methodes as nm




load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

output_dir = os.getenv('output_dir1')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

#output_dir2 = os.getenv('output_dir2') #full data
#if not os.path.exists(output_dir2):
#    os.makedirs(output_dir2)

g1=float(os.getenv('moq_greater'))

#dummy

d_price=os.getenv('dummy_price')
d_skuProps=os.getenv("dummy_skuProps")
d_price={"TJS":0,"UZS":0,"RUB":0}
d_moq=int(os.getenv("dummy_moq"))
d_quantity=os.getenv("dummy_quantity")
d_specId=os.getenv("dummy_specId")
d_status=os.getenv("dummy_status")
d_sku_id=os.getenv("dummy_sku_id")






timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"f_{timestamp}.json"
filename2 = f"products_Full_{timestamp}.json"

output_file1 = os.path.join(output_dir, filename)
#output_file2 = os.path.join(output_dir2, filename2)

def read_num_iid_from_file(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            if "num_iid" in line:
                yield line.split(":")[1].strip().replace('"', '').replace(',', '')

#num_iid_list = read_num_iid_from_file("E:/JMNN/IMPORT/New_System/API/clean_batch_1_2025-03-01_14-06-10.txt ")

#print("Num_iid list loaded.")

def send_request(url):
    try:
        response = requests.get(url, timeout=12)
        return response
    except requests.exceptions.Timeout:
        print(f"Request timed out for URL: {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    

def process_data(data, num_iid):
   
           
    product_id = num_iid

    
    title = {
           
        "zh": data.get('item', {}).get('title', ""),
        "ru": ""
    }
    category_name = {"ru": ""}
    desc_short = {}
    desc = {}
    rating = {"value": 0, "count": 0}

    # price_empty_sku=min(data.get("item").get('price', 0),data.get("item").get('orginal_price', 0))
    item_data2 = data.get("item", {})
    price_empty_sku = min(float(item_data2.get("price") or 0), float(item_data2.get("orginal_price") or 0) )
    
    

    sold_count = data.get("item", {}).get('total_sold', 0)
    try:
        sold_count = int(sold_count)
    except ValueError:
        sold_count = 0

    if sold_count < 10:
        sold_count = random.randint(10, 50)

    viewCount = data.get("item", {}).get('viewCount', 0)
    reviewCount = data.get("item", {}).get('reviewCount', 0)

    # total_quantity = data.get("item", {}).get('num', "")
    total_quantity = data.get("item", {}).get('num', 0) or 0  #new modification
    moq = data.get("item", {}).get('min_num', 1)
    needs_category_review = True
    root_cat_id = data.get("item", {}).get('rootCatId', "")
    cid = data.get("item", {}).get('cid', "")
    is_checked = False

    unit_weight = data.get("item", {}).get('unitWeight', 0)
    try:
        unit_weight = int(unit_weight)
    except ValueError:
        unit_weight = 0

    suttleWeight = 0
    width = 0
    height = 0
    length = 0
    unit = data.get("item", {}).get('unit', "")

    post_fee = data.get("item", {}).get('post_fee', 0)
    try:
        post_fee = int(post_fee)
    except ValueError:
        post_fee = 0

    location = {
        #"zh": data.get("item", {}).get('location', ""),
        "zh": f"中国{data.get('item', {}).get('location', '')}", #Nazir changed
        "en": ""
    }

    props_list = data.get("item", {}).get("props", {})
    props = {
        "zh": [
            {
                "key": prop.get("name", ""),
                "value": prop.get("value", "")
            }
            for prop in props_list
        ],
        "ru": []
    }

    item_imgs = data.get('item', {}).get('item_imgs', [])
    image_urls = [img.get('url', '') for img in item_imgs]
    main_images = {"RU": image_urls} #Nazir have change to RU

    # Получение данных из desc_img
    desc_img = data.get('item', {}).get('desc_img', []) #Nazir have add
    desc_images = {"RU": desc_img}

    #video_data = data.get('item', {}).get('video', {})
    #video_urls = [video_data.get('url', '')] if isinstance(video_data, dict) else [video.get('url', '') for video in video_data]
    #video = {"RU": video_urls, "en": []}
   # video = {} #Nazir changed  

    brand_name = { #Nazir changed
        "zh": data.get("item", {}).get('brand', "")
    }
    brand_id = data.get("item", {}).get("brandId", "")

    skus_data = data.get('item', {}).get('skus', {}).get('sku', [])
    prop_imgs = data.get('item', {}).get('prop_imgs', {}).get('prop_img', [])
    result_skus = []

    # def extract_properties(properties_name):
    #     properties = []
    #     items = properties_name.split(";")
    #     color_dict = {}
    #     size_dict = {}

    #     for item in items:
    #         parts = item.split(":")
    #         if len(parts) == 4:
    #             key = parts[2]
    #             value = parts[3]

    #             is_color = any(img.get('properties') == f"{parts[0]}:{parts[1]}" for img in prop_imgs)

    #             if is_color:
    #                 color_dict = {
    #                     "key": "Color",
    #                     "value": {
    #                         "zh": value,
    #                         "ru": ""
    #                     }
    #                 }
    #             else:
    #                 properties.append({
    #                     "key": key,
    #                     "value": {
    #                         "zh": value,
    #                         "ru": ""
    #                     }
    #                 })

    #     if color_dict:
    #         properties.insert(0, color_dict)
    #     if size_dict:
    #         properties.append(size_dict)

    #     return properties
    def extract_properties(properties_name):
        zh_props = []
        ru_props = []
        color_prop = None

        items = properties_name.split(";")
        for item in items:
            parts = item.split(":")
            if len(parts) == 4:
                key = parts[2]
                value = parts[3]
                is_color = any(img.get('properties') == f"{parts[0]}:{parts[1]}" for img in prop_imgs)
                prop_dict = {"key": key, "value": value}
                if is_color or key.lower() == "color" or key.lower() == "颜色" or key.lower() == "颜色分类" :
                #if is_color or key.lower() in liste_color:    
                    color_prop = prop_dict
                else:
                    zh_props.append(prop_dict)

        # Place Color en premier si trouvé
        if color_prop:
            zh_props = [color_prop] + zh_props

        # ru_props vide comme dans ton exemple
        ru_props = [{"key": "", "value": ""}]

        for i in range(len(zh_props)-1):
            ru_props.append({"key": "", "value": ""})


        return {"zh": zh_props, "ru": ru_props}
    



    
    def get_sku_image(sku_properties, prop_imgs):
        sku_props_set = set(sku_properties.split(";"))  # séparer toutes les propriétés du SKU
        for img in prop_imgs:
            prop_img_properties = img.get("properties", "")
            if prop_img_properties in sku_props_set:  # comparaison stricte
                return img.get("url", "")
        return ""    






    # def get_sku_image(sku_properties, prop_imgs):
    #     for img in prop_imgs:
    #         prop_img_properties = img.get("properties", "")
    #         if prop_img_properties and prop_img_properties in sku_properties:
    #             return img.get("url", "")
    #     return ""

  

    for sku in skus_data:
        properties_name = sku.get("properties_name", "")
        extracted_properties = extract_properties(properties_name)
        # print(extracted_properties)
        sku_properties = sku.get("properties", "")
        sku_image_url = get_sku_image(sku_properties, prop_imgs)

        sku_info = {
            "skuId": str (sku.get("sku_id")), #Nazir added str
            "originalPrice": nm.check_originalPrice(float(sku.get("price", 0))),
            "skuProps": extracted_properties,
           "skuImage": {
        "RU": sku_image_url or (main_images.get("RU") or [""])[0]  #new modification 

    },
            "price": {
                "TJS": 0, "UZS": 0 , "RUB":0

            },
            "moq": 1,
            "quantity": sku.get("quantity", 0),
            "specId": "",
            "status": "active"
        }

        result_skus.append(sku_info)

    seller_info_data = data.get("item", {}).get("seller_info", {})
    seller_info = {
        "sid": seller_info_data.get("sid", ""), # Change to sid
        "sellerId": str(data.get('item', {}).get('seller_id', "")), # Преобразование в строку
        "shopId": str(data.get('item', {}).get('shop_id', "")), # Преобразование в строку
        # "title": seller_info_data.get("title", ""),
        "title": nm.check_seller_title(seller_info_data.get("title",""),seller_info_data.get("shop_name","")) ,
        "shopName": seller_info_data.get("shop_name", "")
    }





    video = data.get("item", {}).get("video", {})
    # video can be dict with "url" as string or list
    url = video.get("url", "")
    if isinstance(url, list):
        url = url[0] if url else ""
    video2 = {"RU": url} if url else {"RU": ""}
   
    
     


    final_data = {
        "productId": product_id,
        "title": title,
        "category": category_name,
        "descShort": desc_short,
        "desc": desc,
        "rating": rating,
        "soldCount": sold_count,
        "viewCount": viewCount,
        "reviewCount": reviewCount,
        "totalQuantity": int(total_quantity),
        "moq": int(nm.check_moq(moq)),
        "needsCategoryReview": needs_category_review,
        "rootCatId": root_cat_id,
        "cid": cid,
        "isChecked": is_checked,
        "unitWeight": unit_weight,
        "shuttleWeight": suttleWeight,
        "width": width,
        "height": height,
        "length": length,
        "unit": unit,
        "postFee": post_fee,
        "location": location,
        "props": props,
        "mainImages": main_images,
        "video": video2,
        "brandName": nm.check_brandName(brand_name),
        "brandId": brand_id,
        "sku": result_skus,
        "sellerInfo": seller_info,
        "descImg": desc_images,
        "sizeTableUrl": [],
        "sizeTable": {},
        "shopItem": [],
        "relatedItems": [],
        "error": "",
        "status": "active" #Nazir changed
    }

    return final_data , price_empty_sku




def main():
    start_time = time.time()
    r1 = os.getenv('r1')
    r2 = os.getenv('r2')
    path = os.getenv("l_dir")

    if not os.path.exists(path):
        print(f"Directory does not exist: {path}")
        return

    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    print("Only files:", files)

    for fname in files:
        old_data_json = os.path.join(path, fname)
        print(f"working on  : {old_data_json}")

        # Génère un nom de sortie unique pour chaque fichier
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"f_{timestamp}_{fname}"
        output_file1 = os.path.join(output_dir, filename)

        i = 0
        with open(old_data_json, "r", encoding="utf-8") as f:
            all_data = json.load(f)

        with open(output_file1, "w", encoding="utf-8") as json_file1:
            json_file1.write("[\n")
            for data in all_data:
                try:
                    if not isinstance(data, dict):
                        continue
                    error_code = data.get("error_code", {})
                    rd = random.randint(int(r2), int(r1))
                    num_iid = data.get("item", {}).get("num_iid", "unknown")

                    if error_code == "0000":
                        produit, ppp = process_data(data, num_iid)
                        produit['sku'] = nm.group_skus_by_color(produit)

                        if len(produit['sku']) == 0:
                            # dummy_image = produit["mainImages"]["RU"][0]
                            dummy_image = (produit.get("mainImages", {}).get("RU") or [""])[0]  #new modification

                            produit["sku"].append({
                                "skuId": rd,
                                "originalPrice": ppp,
                                "skuProps": d_skuProps,
                                "skuImage": {"RU": dummy_image},
                                "price": d_price,
                                "moq": d_moq,
                                "quantity": d_quantity,
                                "specId": d_specId,
                                "status": d_status
                            })

                        if len(produit["sku"]) == 0:
                            print(f"{num_iid}, sku is empty")

                        if float(produit["moq"]) < float(g1):
                            json.dump(produit, json_file1, indent=4, ensure_ascii=False)
                            json_file1.write(",\n")
                        i += 1

                    elif error_code == "2000":
                        with open("2000.txt", "a") as file:
                            file.write(f'"num_iid":"{num_iid}",\n')
                        print(f"{num_iid}, in 2000.txt")

                    elif error_code == "5000":
                        with open("5000.txt", "a") as file:
                            file.write(f'"num_iid":"{num_iid}",\n')
                        print(f"{num_iid}, in 5000.txt")

                    else:
                        with open("5000.txt", "a") as file:
                            file.write(f'"num_iid":"{num_iid}",\n')

                except Exception as e:
                    num_iid_safe = data.get("item", {}).get("num_iid", "unknown") if isinstance(data, dict) else "unknown"
                    print(f"Erreur produit {num_iid_safe}: {e}")
                    with open("5000.txt", "a") as file:
                        file.write(f'"num_iid":"{num_iid_safe}",\n')

            json_file1.write("\n]")
        # Nettoyage de la virgule finale
        nm.clean_trailing_comma(output_file1)
        print(f" file is ready : {output_file1}")

    end_time = time.time()
    print(f"Total successes: {i}")
    print(f"Time for execution: {end_time - start_time:.2f} seconds")

# def main():
#     start_time = time.time()
#     i = 0
#     r1=os.getenv('r1')
#     r2=os.getenv('r2')
    
#     # Charger le fichier JSON local depuis la variable d'environnement
#     old_data_json = os.getenv('OLD_DATA_JSON')
#     if not old_data_json:
#         raise FileNotFoundError("OLD_DATA_JSON not definied .env")
#     with open(old_data_json, "r", encoding="utf-8") as f:
#         all_data = json.load(f)

#     # with open(output_file1, "w", encoding="utf-8") as json_file1, open(output_file2, "w", encoding="utf-8") as json_file2:
#     with open(output_file1, "w", encoding="utf-8") as json_file1 :
#         json_file1.write("[\n")
#         # json_file2.write("[\n") full data

#         for data in all_data:
#             try:
#                 if not isinstance(data, dict):
#                     continue
#                 error_code = data.get("error_code", {})
#                 rd = random.randint(int(r2),int(r1))
#                 num_iid = data.get("item", {}).get("num_iid", "unknown")

#                 if error_code == "0000":
#                     produit,ppp = process_data(data, num_iid)
#                     produit['sku'] = nm.group_skus_by_color(produit)
                   

#                     if len(produit['sku'])== 0:
#                       dummy_image=produit["mainImages"]["RU"][0]
#                       produit["sku"].append({
#                                            "skuId":rd,                   
#                                            "originalPrice" : ppp,
#                                            "skuProps":d_skuProps,
#                                            "skuImage":{"RU":dummy_image},
#                                            "price":d_price,
#                                            "moq":d_moq,
#                                             "quantity":d_quantity,
#                                              "specId":d_specId,
#                                                 "status":d_status
#                                              })
#                     # print("the len of sku is ",len(produit["sku"]))

#                     # print("len of sku",len(produit["sku"]))

#                     if len(produit["sku"]) ==0:
#                         print(f"{num_iid}, sku is empty")

#                     # print(produit["mainImages"]["RU"][0]) 
               
                    
#                     # if not produit["sku"]:
#                     #     c+=1
#                     #     print(f"{num_iid}, sku is empty")
#                     # print("\n total empty is ",c)    



#                     if int(produit["moq"]) < int(g1):  
#                         json.dump(produit, json_file1, indent=4, ensure_ascii=False)
#                         json_file1.write(",\n")

#                     # json.dump(data, json_file2, indent=4, ensure_ascii=False) full data
#                     # json_file2.write(",\n")  full data
#                     i += 1
#                     # print(f"{num_iid}, success")

#                 elif error_code == "2000":
#                     with open("2000.txt", "a") as file:
#                         file.write(f'"num_iid":"{num_iid}",\n')
#                     print(f"{num_iid}, in 2000.txt")

#                 elif error_code == "5000":
#                     with open("5000.txt", "a") as file:
#                         file.write(f'"num_iid":"{num_iid}",\n')
#                     print(f"{num_iid}, in 5000.txt")

#                 else:
#                     with open("5000.txt", "a") as file:
#                         file.write(f'"num_iid":"{num_iid}",\n')

#             except Exception as e:
#                 num_iid_safe = data.get("item", {}).get("num_iid", "unknown") if isinstance(data, dict) else "unknown"
#                 print(f"Erreur produit {num_iid_safe}: {e}")
#                 with open("5000.txt", "a") as file:
#                     file.write(f'"num_iid":"{num_iid_safe}",\n')

#         json_file1.write("\n]")
#         #json_file2.write("\n]")  full data

#     end_time = time.time()
#     print(f"Total successes: {i}")
#     print(f"Time for execution: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
    # print(os.getenv("l_dir"))
    # path = os.getenv("l_dir")
    
    # if os.path.exists(path):
    #     files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    #     print("Only files:", files)
    # else:
    #     print(f"Directory does not exist: {path}")


    

# Utilisation après génération du fichier :
    # nm.clean_trailing_comma(output_file1)     
    
    