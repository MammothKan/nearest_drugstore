# 借助开放API计算两点间距离及路途时间

**背景：**  
疫情政策“大开大方”，兜里抗原“寥寥无几”。暇日，网上冲浪时，偶得喜讯“杭城开始抗原保供。

**基本需求：**  
全市共二百余家药店提供抗原，如何从二百余家药店中筛选出距离我最近的药店？

**解决方法：** 
1. 读取excel温江，获取所有药店地址信息；
2. 借助百度地图API **地理编码服务（又名Geocoder）**，将地址信息转换为经纬度数值；
3. 借助百度地图API **批量算路服务（又名RouteMatrix API）**，计算出发地经纬度与目的地经纬度间的距离和路途时间；
4. 将距离和路途信息写入excel文件。


reference:
1. [地理编码服务（又名Geocoder）说明文档](https://lbsyun.baidu.com/index.php?title=webapi/guide/webservice-geocoding)
2. [批量算路服务（又名RouteMatrix API）说明文档](https://lbsyun.baidu.com/index.php?title=webapi/route-matrix-api-v2)