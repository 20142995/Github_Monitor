# Github_Monitor 

## config.ini 说明

```
[keyword1]
;  要监控的关键字
keyword = CVE-2020
; 发件设置 用户名
user = xxxx@qq.com
; 发件设置 密码或授权码，qq邮箱为授权码
passwd = ytvkxca
; 要接收通知的邮箱
touser = xxxxxx@qq.com,xxxxxx@qq.com
[keyword2]
keyword = 扫描器
user = xxxx@qq.com
passwd = ytvkxca
touser = xxxxxx@qq.com
```
## 使用方法

```
环境安装就不作说明了。。。

先填好配置，保持几个文件在同目录。

未写定时方法，建议使用crontab实现定时任务
参考(每天8点检查一次)
0 8 * * * python3 /tmp/github_monitor.py
```
