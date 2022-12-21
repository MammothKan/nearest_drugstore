import pandas as pd
import requests
import logging
import json

from config import CONFIG

logging.basicConfig(level = logging.INFO,format = '%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# 出发地
logger.info(msg="Start \t 获取出发地地理编码 ...")
home_address = CONFIG.origin_address
geocoder_url = "https://api.map.baidu.com/geocoding/v3/"
geocoder_params = {
        "city": "杭州",
        "address": home_address,
        "output": "json",
        "callback": "ShowLocation",
        "ak": CONFIG.baidu_map_api_ak
    }
geocoder_response = requests.get(url=geocoder_url, params=geocoder_params)
if geocoder_response.status_code == 200:
        geocoder_response_content = json.loads(geocoder_response.text[27:-1])
        home_lng = geocoder_response_content['result']['location']['lng']    # 经度 longitude
        home_lat = geocoder_response_content['result']['location']['lat']    # 纬度 latitude
        logger.info(f"Process \t 出发地地理编码获取成功，纬度：{home_lat}；经度：{home_lng}")
else:
    logger.error("出发地地理编码获取失败")
    SystemExit()
# print(home_lat)
# print(home_lng)
logger.info("End \t 获取出发地地理编码.")

# 目的地
logger.info("Start \t 读取目的地地址信息 ...")
drugstore_df = pd.read_excel(CONFIG.io_path["input_file"])
logger.info(f"End \t 读取目的地地址信息，共{drugstore_df.shape[1]}条.")
# print(drugstore_df)

drugstore_df['lat'] = 'None'
drugstore_df['lng'] = 'None'
drugstore_df['walking_distance'] = 0
drugstore_df['walking_duration'] = 0
destinations_lat_lng = ""      # 用于暂存由目的地经纬度拼接而成的字符串，被用于批量算路接口
has_finished = -1              # 用于暂存已完成批量算路目的地地址的索引下标，因为批量算路API的单次分支最大为50，故用此变量完成多次批量算路API调用

# 获取目的地地理编码，并进行批量算路
logger.info("Start \t 获取目的地地理编码 ...")
geocoder_url = "https://api.map.baidu.com/geocoding/v3/"
for index, row in drugstore_df.iterrows():
    geocoder_params = {
        "city": "杭州",
        "address": row['address'],
        "output": "json",
        "callback": "ShowLocation",
        "ak": CONFIG.baidu_map_api_ak
    }
    geocoder_response = requests.get(url=geocoder_url, params=geocoder_params)
    if geocoder_response.status_code == 200:
        geocoder_response_content = json.loads(geocoder_response.text[27:-1])
        lng = geocoder_response_content['result']['location']['lng']    # 经度 longitude
        lat = geocoder_response_content['result']['location']['lat']    # 纬度 latitude
        drugstore_df.loc[index, 'lng'] = lng
        drugstore_df.loc[index, 'lat'] = lat
        destinations_lat_lng += str(lat) + ',' + str(lng) + '|'
        if index % 10 == 0: 
            logger.info(f"Process \t 已完成至第 {index} 条目的地地址编码转换;")
        if index % 50 == 0:         # 批量算路API 单次请求最大计算50条路径
            logger.info("Start \t 批量算路 ...")
            route_matrix_walking_url = "https://api.map.baidu.com/routematrix/v2/walking?"
            route_matrix_walking_params = {
                "origins": str(home_lat) + ',' + str(home_lng),
                # "destinations": "30.2753730476513,120.158671522578|30.2753730476513,120.158671522578",
                "destinations": destinations_lat_lng[:-1],
                "output": "json",
                "ak": CONFIG.baidu_map_api_ak
            }
            route_matrix_walking_response = requests.get(url=route_matrix_walking_url, params=route_matrix_walking_params)
            if route_matrix_walking_response.status_code == 200:
                # print(route_matrix_walking_response.text)
                route_matrix_walking_results = json.loads(route_matrix_walking_response.text)['result']
                # print("共获得 ", len(route_matrix_walking_results), "条结果")
                for _index, distance_duration_result in enumerate(route_matrix_walking_results):
                    drugstore_df.loc[has_finished + 1 + _index, 'walking_distance'] = distance_duration_result['distance']['text']
                    drugstore_df.loc[has_finished + 1 + _index, 'walking_duration'] = distance_duration_result['duration']['text']
                logger.info("End \t 批量算路.")
            else:
                logger.warning(f"第 {has_finished + 1} 至 {index} 条目的地批量算路请求失败.")
            # 重置    
            destinations_lat_lng = ""           # 重置 批量算路 目的地参数
            has_finished = index                # 移动已完成批量算路目的地下标
    else:
        logger.error(f"第 {index} 条目的地，经纬度请求失败。")   
logger.info("End \t 目的地地理编码获取.")

# 处理最后不满50条的目的地批量算路请求
if destinations_lat_lng != "":
    route_matrix_walking_url = "https://api.map.baidu.com/routematrix/v2/walking?"
    route_matrix_walking_params = {
        "origins": str(home_lat) + ',' + str(home_lng),
        # "destinations": "30.2753730476513,120.158671522578|30.2753730476513,120.158671522578",
        "destinations": destinations_lat_lng[:-1],
        "output": "json",
        "ak": CONFIG.baidu_map_api_ak
    }
    route_matrix_walking_response = requests.get(url=route_matrix_walking_url, params=route_matrix_walking_params)
    if route_matrix_walking_response.status_code == 200:
        # print(route_matrix_walking_response.text)
        route_matrix_walking_results = json.loads(route_matrix_walking_response.text)['result']
        logger.info(f"Process \t 完成最后 {len(route_matrix_walking_results)} 条目的地批量算路请求")
        for index, distance_duration_result in enumerate(route_matrix_walking_results):
            drugstore_df.loc[has_finished + 1 + index, 'walking_distance'] = distance_duration_result['distance']['text']
            drugstore_df.loc[has_finished + 1 + index, 'walking_duration'] = distance_duration_result['duration']['text']
    else:
        logger.warning(f"剩余多条目的地批量算路请求失败")

# 写入 excel 文件夹
logger.info("Start \t 写入文件")
drugstore_df.to_excel(CONFIG.io_path["output_file"])
logger.info("End \t 完成！")

