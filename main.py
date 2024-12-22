import asyncio
import aiohttp
import json
import os
import requests



class BilibiliLiveNotification():
    def __init__(self):
        self.live_rooms = []  # 存储配置中的直播间信息
        self.live_statuses = {}  # 存储每个直播间的最后状态
        self.live_covers = {}  # 存储每个直播间的封面 URL
        self.live_unames = {}  # 存储每个直播间的主播名
        self.live_urls = {}  # 存储每个直播间的 URL
        self.base_url = {} # 存储机器人框架地址
        self.token = {}
        self.load_config()


    def load_config(self):
        """加载配置文件"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.base_url = config['http_base_url']
                self.live_rooms = config['live_rooms']
                self.token = config['token']
                # 初始化每个直播间的状态
                for room in self.live_rooms:
                    self.live_statuses[room['room_id']] = None
        except Exception as e:
            print(f"加载配置文件失败: {e}")
    
    async def initialize(self):
        """异步初始化：启动直播状态监控任务"""
        print("异步初始化：启动多个直播间状态监控任务")
        # 插件启动时，检查每个直播间的状态并发送初始提醒
        await self.initial_check()
        asyncio.create_task(self.monitor_live_status())  # 启动后台任务

        


    async def initial_check(self):
        """插件启动时进行一次直播状态检查，若已直播则发送提醒"""
        # 获取所有需要检查的直播间 ID
        room_ids = [room['room_id'] for room in self.live_rooms]
        live_info = await self.fetch_live_status_batch(room_ids)
    
        # 根据批量查询的状态推送提醒
        for room, (status, cover, uname, live_url) in zip(self.live_rooms, live_info):
            if status == 1:
                # 构建复杂消息链
                msg_chain = [
                    {
                        "type": "image",
                        "data": {
                            "file": cover  # 假设cover是图片的URL或文件路径
                        }
                    },
                    {
                        "type": "text",
                        "data": {
                            "text": f"{uname} 正在直播！\n{live_url}"
                        }
                    }
                ]

                # 构造发送消息的API端点和参数
                endpoint = "/send_msg"
                # 在请求中加入 token
                headers = {
                    'Content-Type': 'application/json',
                    "Authorization": f"Bearer {self.token}"  # 假设 token 需要作为 Authorization header 发送
                }

                # 遍历 room['group_id'] 中的所有群号，逐个发送请求
                for group_id in room['group_ids']:
                    payload = {
                            "group_id": group_id,  # 群号
                            "message": msg_chain
                    }
                    
                    full_url = self.base_url + endpoint
                    # print("initial_check ok!!!!")
                    response = requests.post(full_url, headers=headers,data=json.dumps(payload))
                    print(uname + " 直播了")
                    await asyncio.sleep(1)

                
                # 更新直播间的状态、封面、主播名和直播间地址
                self.live_statuses[room['room_id']] = status
                self.live_covers[room['room_id']] = cover
                self.live_unames[room['room_id']] = uname
                self.live_urls[room['room_id']] = live_url


    async def fetch_live_status_batch(self, room_ids):
        """批量获取直播间状态、封面、主播名和直播间 URL"""
        url = "https://api.live.bilibili.com/xlive/web-room/v1/index/getRoomBaseInfo"
        params = {
            "req_biz": "web_room_componet",
        }
        # 使用一个列表来传递多个 room_ids
        # 将 room_ids 作为多个相同名称的参数
        params.update({f'room_ids': room_ids})

        async with aiohttp.ClientSession() as session:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Referer": "https://live.bilibili.com/",
            }
            async with session.get(url, params=params, headers=headers) as resp:
                # 输出响应状态码和返回内容（调试用）
                if resp.status == 200:
                    data = await resp.json()
                    if isinstance(data, dict) and 'code' in data and data['code'] == 0:
                        # 从返回的 data['data']['by_room_ids'] 中提取信息
                        live_info = []
                        for room_id, room_info in data['data']['by_room_ids'].items():
                            live_info.append((
                                room_info['live_status'],  # 直播状态
                                room_info.get('cover', ''),  # 封面图片 URL
                                room_info['uname'],  # 主播名
                                room_info['live_url']  # 直播间 URL
                            ))
                            

        return live_info
    

    async def monitor_live_status(self):
        """后台任务：定时检查多个直播间的状态"""
        while True:
            # 获取所有需要检查的直播间 ID
            room_ids = [room['room_id'] for room in self.live_rooms]
            live_info = await self.fetch_live_status_batch(room_ids)
            
            # 根据批量查询的状态推送提醒
            for room, (status, cover, uname, live_url) in zip(self.live_rooms, live_info):
                if status == 1 and status != self.live_statuses.get(room['room_id']):
                    # 构建复杂消息链
                    msg_chain = [
                        {
                            "type": "image",
                            "data": {
                                "file": cover  # 假设cover是图片的URL或文件路径
                            }
                        },
                        {
                            "type": "text",
                            "data": {
                                "text": f"{uname} 正在直播！\n{live_url}"
                            }
                        }
                    ]

                    # 构造发送消息的API端点和参数
                    endpoint = "/send_msg"
                    # 在请求中加入 token
                    headers = {
                        'Content-Type': 'application/json',
                        "Authorization": f"Bearer {self.token}"  # 假设 token 需要作为 Authorization header 发送
                    }

                    # 遍历 room['group_id'] 中的所有群号，逐个发送请求
                    for group_id in room['group_ids']:
                        payload = {
                                "group_id": group_id,  # 群号
                                "message": msg_chain
                        }
                        
                        full_url = self.base_url + endpoint
                        # print("monitor_live_status ok!!!!")
                        response = requests.post(full_url, headers=headers,data=json.dumps(payload))
                        print(uname + " 直播了")
                        await asyncio.sleep(1)


                    # 更新直播间的状态、封面、主播名和直播间地址
                    self.live_statuses[room['room_id']] = status
                    self.live_covers[room['room_id']] = cover
                    self.live_unames[room['room_id']] = uname
                    self.live_urls[room['room_id']] = live_url
                elif status != 1:
                    # 当前不是直播中且状态发生变化时，清除状态
                    self.live_statuses[room['room_id']] = None
                    self.live_covers[room['room_id']] = ''
                    self.live_unames[room['room_id']] = ''
                    self.live_urls[room['room_id']] = ''

            await asyncio.sleep(60)  # 每60秒检查一次所有直播间



async def main():
    notification = BilibiliLiveNotification()
    await notification.initialize()
    await asyncio.Future()  # 让主线程等待，防止程序结束

if __name__ == '__main__':
    asyncio.run(main())