# BilibiliLiveNotification

这是一个用于在关注的B站主播开播时，向指定聊天群发送提醒的Python程序。该程序适配了onebot11/go-cqhttp聊天机器人。

## 功能

- 监控B站直播状态
- 当关注的主播开播时，自动向配置的群聊发送提醒

## 配置

配置文件位于 `config.json`。请根据实际情况填写该文件中的相关信息。

## 运行步骤

1. 下载所有项目文件。
2. 修改 `config.json` 文件，填写必要的配置信息。
3. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
4. 双击 run.bat 启动程序。
## 注意事项
- 本项目不依赖特定的Python版本，兼容大部分版本。
- 请确保已经配置好onebot11或go-cqhttp聊天机器人环境。
- 不支持短房间号,比如大型官方赛事直播间用的，需要填写真实房间号。

## 许可证

本项目采用 MIT 许可证，详情请参见 LICENSE。
