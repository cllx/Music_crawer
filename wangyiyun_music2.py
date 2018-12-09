import os
import tkinter
import requests
from lxml import etree
# 标记是否停止下载，初始值为False，当值为True时，停止下载
flag = False
class MusicSpider(object):
    def __init__(self):
        pass
    def download_songs(self, text, entry):
        self.text = text
        self.entry = entry
        url = self.entry.get() # 获取输入框中的字符串
        url = url.replace('/#', '').replace('https', 'http')# 对字符串进行去空格和转协议处理
        # 当没有输入url就点击下载或者回车的时候，在文本框中显示提示
        if url == '':
            self.text.insert(tkinter.END, '请输入您要下载的歌单的url地址！')
            return
        # 网易云音乐外链url接口：http://music.163.com/song/media/outer/url?id=xxxx
        out_link = 'http://music.163.com/song/media/outer/url?id='
        headers = {
            'Referer': 'https://music.163.com/',
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.89 "
                          "Safari/537.36"
        }
        # 请求页面的源码
        res = requests.get(url=url, headers=headers).text
        tree = etree.HTML(res)
        # 音乐列表
        song_list = tree.xpath('//ul[@class="f-hide"]/li/a')
        # 如果是歌手页面
        artist_name_tree = tree.xpath('//h2[@id="artist-name"]/text()')
        artist_name = str(artist_name_tree[0]) if artist_name_tree else None
        # 如果是歌单页面：
        song_list_name_tree = tree.xpath('//h2[contains(@class,"f-ff2")]/text()')
        song_list_name = str(song_list_name_tree[0]) if song_list_name_tree else None
        # 设置音乐下载的文件夹为歌手名字或歌单名
        folder = './' + artist_name if artist_name else './' + song_list_name
        if not os.path.exists(folder):
            os.mkdir(folder)
        for i, s in enumerate(song_list):
            href = str(s.xpath('./@href')[0])
            id = href.split('=')[-1]
            src = out_link + id # 拼接获取音乐真实的src资源值
            title = str(s.xpath('./text()')[0]) # 音乐的名字
            filename = title + '.mp3'
            filepath = folder + '/' + filename
            data = requests.get(src, headers=headers).content# 音乐的二进制数据
            info = '开始下载第%d首音乐：%s\n' % (i+1, filename)
            if flag:# 当停止下载时，显示信息，跳出循环，代码不再向下执行
                self.text.insert(tkinter.END, '停止下载')
                self.text.see(tkinter.END)
                self.text.update()
                break
            self.text.insert(tkinter.END, info) # 在文本框中显示下载信息
            self.text.see(tkinter.END)
            self.text.update()
            try:# 下载音乐
                with open(filepath, 'wb') as f:
                    f.write(data)
                    f.close()
            except Exception as e:
                print(e)
                self.text.insert(tkinter.END, e) # 将错误信息显示在前端文本框中
                self.text.see(tkinter.END)
                self.text.update()
        if not flag: # 中间没有点击停止下载，程序会走到这里
            self.text.insert(tkinter.END, '下载完成') # 在前端文本框中显示下载完毕
            self.text.see(tkinter.END)
            self.text.update()
class Application(object):
    def __init__(self):
        # 创建主窗口Tk()
        self.window = tkinter.Tk()
        # 设置一个标题，参数类型：string
        self.window.title('网易云音乐下载器——Powered by yLoNG')
        # 设置主窗口大小和位置
        # self.window.geometry('800x500+240+120')
        self.center_window(self.window, 800, 500) # 窗口居中，宽800，高500
        #  使用frame增加上中下4个框架
        self.fm1 = tkinter.Frame(self.window) # fm1存放label标签
        self.fm2 = tkinter.Frame(self.window) # fm2存放url输入框,下载按钮
        self.fm3 = tkinter.Frame(self.window) # fm3 存放下载信息显示的文本框
        self.fm4 = tkinter.Frame(self.window) # fm4用来存放底下停止和退出按钮
        self.fm1.pack()
        self.fm2.pack()
        self.fm3.pack()
        self.fm4.pack()

        # 创建一个标签
        self.label = tkinter.Label(self.fm1, text='输入你要下载的歌单的url，点击下载或者回车！', font=('微软雅黑', 15), width=35)
        # 显示，布局管理器----可以理解为一个弹性容器
        self.label.pack(fill=tkinter.X)
        
        # 创建一个输入框，用来接收用户输入的歌单的url
        self.entry = tkinter.Entry(self.fm2, width=46, bg='pink', font=('微软雅黑', 20))
        self.entry.grid(row=0, column=0, rowspan=1, columnspan=10, padx=2)
        self.entry.bind("<Key-Return>", self.press_enter)# 输入歌单url之后直接按回车键，触发press_enter函数

        #  创建下载按钮
        self.btn_download = tkinter.Button(self.fm2, text='下载', command=self.crawl, bg='red', font=('微软雅黑', 12))
        self.btn_download.grid(row=0, column=30, rowspan=1, columnspan=1, padx=5, pady=3)

        # 创建一个文本控件，用于显示多行文本，显示音乐下载信息
        self.text = tkinter.Text(self.fm3, width=110, height=18, font=('微软雅黑', 10))
        self.text.pack(side=tkinter.LEFT, fill=tkinter.Y)

        # 创建一个滚动条
        self.scroll = tkinter.Scrollbar(self.fm3)
        self.scroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        # 关联滚动条和文本 config, 相互关联
        self.scroll.config(command=self.text.yview())
        self.text.config(yscrollcomman=self.scroll.set)

        # 创建停止和退出按钮
        btn_stop = tkinter.Button(self.fm4, text='停止', command=self.stop, bg='gray', font=('微软雅黑', 16))
        btn_quit = tkinter.Button(self.fm4, text='退出', command=self.window.quit, bg='gray', font=('微软雅黑', 16))
        btn_stop.pack(side='left', padx=100, pady=10)
        btn_quit.pack(side='right', padx=100, pady=10)

    def stop(self):
        global flag # 将flag设为全局变量，以便下载过程中能随时获取
        flag = True
        return flag

    def crawl(self):
        text = self.text
        entry = self.entry
        self.text.delete(1.0, tkinter.END)
        global flag
        flag = False
        MusicSpider.download_songs(self, text, entry)

    def press_enter(self, even):
        return self.crawl()

    def center_window(self, root, width, height):
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        # print(size)
        root.geometry(size)

    def run(self):
        # 进入消息循环，显示主窗口
        self.window.mainloop()

if __name__ == '__main__':
    app = Application()
    app.run()
