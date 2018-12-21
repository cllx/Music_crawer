import os
import tkinter
import requests
from lxml import etree
import requests, os, json, base64
from selenium import webdriver
import urllib.parse
from scrapy.selector import Selector
from binascii import hexlify
from Crypto.Cipher import AES
# 标记是否停止下载，初始值为False，当值为True时，停止下载
flag = False

class Encrypyed():
    '''传入歌曲的ID，加密生成'params'、'encSecKey 返回'''
    def __init__(self):
        self.pub_key = '010001'
        self.modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        self.nonce = '0CoJUm6Qyw8W8jud'

    def create_secret_key(self, size):
        return hexlify(os.urandom(size))[:16].decode('utf-8')
    def aes_encrypt(self,text, key):
        iv = '0102030405060708'
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        result = encryptor.encrypt(text)
        result_str = base64.b64encode(result).decode('utf-8')
        return result_str
    def rsa_encrpt(self, text, pubKey, modulus):
        text = text[::-1]
        rs = pow(int(hexlify(text.encode('utf-8')), 16), int(pubKey, 16), int(modulus, 16))
        return format(rs, 'x').zfill(256)
    def work(self, ids, br=128000):
        text = {'ids': [ids], 'br': br, 'csrf_token': ''}
        text = json.dumps(text)
        i = self.create_secret_key(16)
        encText =self.aes_encrypt(text, self.nonce)
        encText = self.aes_encrypt(encText, i)
        encSecKey = self.rsa_encrpt(i, self.pub_key, self.modulus)
        data = {'params': encText, 'encSecKey': encSecKey}
        return data
    def search(self,text):
        text = json.dumps(text)
        i = self.create_secret_key(16)
        encText = self.aes_encrypt(text, self.nonce)
        encText = self.aes_encrypt(encText, i)
        encSecKey = self.rsa_encrpt(i, self.pub_key, self.modulus)
        data = {'params': encText, 'encSecKey': encSecKey}
        return data

class search():
    '''跟歌单直接下载的不同之处，1.就是headers的referer
                              2.加密的text内容不一样！
                              3.搜索的URL也是不一样的
        输入搜索内容，可以根据歌曲ID进行下载，大家可以看我根据跟单下载那章，自行组合
    '''
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36', 'Host': 'music.163.com', 'Referer': 'http://music.163.com/search/'} ###!!注意，搜索跟歌单的不同之处！！
        self.main_url = 'http://music.163.com/'
        self.session = requests.Session()
        self.session.headers = self.headers
        self.ep = Encrypyed()
    def search_song(self, search_content,search_type=1, limit=9):
        """
        根据音乐名搜索
      :params search_content: 音乐名
      :params search_type: 不知
      :params limit: 返回结果数量
      return: 可以得到id 再进去歌曲具体的url
        """
        url = 'http://music.163.com/weapi/cloudsearch/get/web?csrf_token='
        text = {'s': search_content, 'type': search_type, 'offset': 0, 'sub': 'false', 'limit': limit}
        data = self.ep.search(text)
        resp = self.session.post(url, data=data)
        result = resp.json()
        if result['result']['songCount'] <= 0:
            print('搜不到！！')
        else:
            songs = result['result']['songs']
        song_id_list = []
        for song in songs:
            song_id, song_name, singer, alia = song['id'], song['name'], song['ar'][0]['name'], song['al']['name']
            # print(song_id, song_name, singer, alia)
            song_id_list.append([song_id, song_name, singer])
        return song_id_list

class MusicSpider(object):
    def __init__(self):
        pass
    def download_songs(self, text, entry):
        headers = {
            'Referer': 'https://music.163.com/',
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.89 "
                          "Safari/537.36",
        }

        # 网易云音乐外链url接口：http://music.163.com/song/media/outer/url?id=xxxx
        out_link = 'http://music.163.com/song/media/outer/url?id='
        self.text = text
        self.entry = entry
        url = self.entry.get()# 获取输入框中的字符串
        # 当没有输入url就点击下载或者回车的时候，在文本框中显示提示
        if url == '':
            self.text.insert(tkinter.END, '请输入您要下载的歌单的url地址！')
            return
        for ch in url:
            if '\u4e00' <= ch <= '\u9fff':
                temp = 0
            else:
                temp = 1
            break
        if temp == 0:
            ch_filename = url
            d = search()
            song_list_id = d.search_song(url)
        else:
            url = url.replace('/#', '').replace('https', 'http')# 对字符串进行去空格和转协议处理
            # headers = {
            #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            #     'Referer': 'https://music.163.com/',
            #     'Host': 'music.163.com',
            #     'Cookie': "__gads=ID=e3027319dd5bfd99:T=1527085577:S=ALNI_MZETzgINyM5D7fRneLfn9nVv1fHDg; vjuids=b3bb39358.1638d64d014.0.5b9243c8dfce2; _ntes_nnid=a8578fffa16309693b53ace332860c7c,1527085584433; _ntes_nuid=a8578fffa16309693b53ace332860c7c; vjlast=1527085584.1540371044.21; vinfo_n_f_l_n3=a8a745fd8e9c1efd.1.0.1540371043830.0.1540371097375; JSESSIONID-WYYY=kR%2B2rEs8blRcgyo47VUNY0grFXJ5j1wRK9T5WzdNTVvKggZeKHmAHc%2BWnKHjPqAnAnvGwobQI7Utwf32myHYrGbtXTmiYnWOwkQg3XjlN%5CV2OwNsFt3ksAfGW64cWKJpkVuxO2TOvfuxcKOsWxMf1NPQr%2BHu8o%2BoMxzn%2FtBK%5CdclQ9sX%3A1544673329395; _iuqxldmzr_=32; __utma=94650624.1331097090.1544671531.1544671531.1544671531.1; __utmz=94650624.1544671531.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); WM_NI=o2BC%2Fwz7QtKVuv9JZg1YoGIX27Lm%2B0%2BFkTvVXEgIQcL%2BA9PToBXvkHIcqFfk6otRmP3KdN12A5MfBfm3AfesXIkKVuUVcj9HHNVlrzh1rCywutnkMIr7pS45BD7JnSvpRWE%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee9ae143af96b783e93df78e8ab6c85a929a9b84f341b4b5fed2f3529cbcaad5c12af0fea7c3b92aadee8ea4ae7dbae99f95ca5eb7aaf7abd96df387a1a8cc54f2e9848eaa3ce99aa5b5f55e9c9ba9aad46990f58fdad360ad9e9897ea448bbdbfa7e561f6b1bcb3f05cf195acafb43a83eb8387c16eafed8f87e8799c97a5acd57f978aad8bbc448c929a8df172acefbea4fc7db7aca28cd043b2e9c0b4b73f829cf9abed59b6b09eb8c837e2a3; WM_TID=lmx04p91zfdAUVRRRRcseohnx8NGcaoU; __utmc=94650624; __utmb=94650624.8.10.1544671531"
            # }

            # 请求页面的源码
            # browser = webdriver.Chrome("C:\\Users\hly\AppData\Local\Google\Chrome\Application\chrome.exe")
            # browser.get(url)
            # print(browser.page_source)
            # browser.close()

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
        if temp == 0:
            folder = './' + ch_filename
        else:
            folder = './' + artist_name if artist_name else './' + song_list_name
        if not os.path.exists(folder):
            os.mkdir(folder)

        if temp == 0:
            song_i = 0
            for song_s in song_list_id:
                song_i += 1
                src = out_link + str(song_s[0])
                filename = song_s[1] + '_' + song_s[2] +'.mp3'
                filepath = folder + '/' + filename
                data = requests.get(src, headers=headers).content
                info = '开始下载第%d首音乐：%s %s\n' % (song_i, filename, song_s[2])
                if flag:  # 当停止下载时，显示信息，跳出循环，代码不再向下执行
                    self.text.insert(tkinter.END, '停止下载')
                    self.text.see(tkinter.END)
                    self.text.update()
                    break
                self.text.insert(tkinter.END, info)  # 在文本框中显示下载信息
                self.text.see(tkinter.END)
                self.text.update()
                try:  # 下载音乐
                    with open(filepath, 'wb') as f:
                        f.write(data)
                        f.close()
                except Exception as e:
                    print(e)
                    self.text.insert(tkinter.END, e)  # 将错误信息显示在前端文本框中
                    self.text.see(tkinter.END)
                    self.text.update()
        else:
            for i, s in enumerate(song_list):
                href = str(s.xpath('./@href')[0])
                id = href.split('=')[-1]
                src = out_link + id # 拼接获取音乐真实的src资源值
                title = str(s.xpath('./text()')[0])# 音乐的名字
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
        if not flag:# 中间没有点击停止下载，程序会走到这里
            self.text.insert(tkinter.END, '下载完成') # 在前端文本框中显示下载完毕
            self.text.see(tkinter.END)
            self.text.update()

class Application(object):
    def __init__(self):
        # 创建主窗口Tk()
        self.window = tkinter.Tk()
        # 设置一个标题，参数类型：string
        self.window.title('云音乐下载——LoNG')
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
        self.label = tkinter.Label(self.fm1, text='输入歌单、歌手的url或歌曲名，点击下载或者回车！', fg="#ffffff", bg='#2e363a', font=('微软雅黑',15), width=797)
        # 显示，布局管理器----可以理解为一个弹性容器
        self.label.pack(fill=tkinter.X)

        # 创建一个输入框，用来接收用户输入的歌单的url
        self.entry = tkinter.Entry(self.fm2, width=46, fg="#ffffff", bg='#c20c0c', font=('微软雅黑', 20))
        self.entry.grid(row=0, column=0, rowspan=1, columnspan=10, padx=2)
        self.entry.bind("<Key-Return>", self.press_enter)# 输入歌单url之后直接按回车键，触发press_enter函数

        #  创建下载按钮
        self.btn_download = tkinter.Button(self.fm2, text='下载', fg="#ffffff", command=self.crawl, bg='#2e363a', font=('微软雅黑', 12))
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
    # app = MusicSpider()
    app.run()
