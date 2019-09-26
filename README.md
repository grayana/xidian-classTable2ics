# xidian-classTable2ics
将西电教务系统的课表导出为ICS日历文件

## 需要安装的库文件

`requests` `retry`

## 使用方法
 运行 `pip install requests` `pip install request` 安装`requests` `retry`库
 然后通过`getClass.py`获取到个人课表的JSON数据，再运行`toICS.py`即可生成相应的`.ics`文件
 
