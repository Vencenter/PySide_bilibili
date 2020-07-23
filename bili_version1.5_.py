#-*- coding:utf-8 -*-
#*******************************************************************
#*******************************************************************
#*************************导入模块***********************************
#*******************************************************************
#*******************************************************************
from  PySide.QtGui  import *
from  PySide.QtCore  import *
import shutil
import re
import sys
import os
import json
import io
import urllib
import urllib2
import urllib3
import requests
import subprocess
from io import BytesIO
from PIL import Image
from contextlib import closing
from multiprocessing import Process
import random
import thread
import traceback
import time
reload(sys)
sys.setdefaultencoding("utf-8")




ffpmpegRoot=os.path.abspath(os.path.dirname(__file__)).replace('\\','/')

ffmpeg=ffpmpegRoot+"/ffmpeg/bin/ffmpeg.exe"
ffplay=ffpmpegRoot+"/ffmpeg/bin/ffplay.exe"
ffprobe=ffpmpegRoot+"/ffmpeg/bin/ffprobe=.exe"
#*************************表头参数**************************

image_name=""

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.0',
    'Referer': 'https://www.bilibili.com/',

}


def showProgress(label = 'Getting data' , waitSeconds = 0.01) :#进度条
    #print "**"*10
    def call(func) :
        def handle(*args , **kwargs) :
            progress = TextProgressDialog(label , action = func , args = args , kwargs = kwargs ,
                                          waitSeconds = waitSeconds , parent = args[0])
            return progress.start()
        return handle
    return call


class TextProgressDialog(QLabel):
    '''A dialog to show the progress of the process.'''
    def __init__(self, text, action, args=[], kwargs={}, waitSeconds=1, parent=None):
        '''If the passed time is greater then waitSeconds, the dialog will pop up.'''
       
        self._text = text + ' '
        self._action = action
        self._args = args
        self._kwargs = kwargs
        self._actionReturned = None
        self._actionFinished = False
        self._actionFailed = False
        self._actionException = ''
        self._thread = None
       
        self._waitSeconds = waitSeconds
        self._sleepSecond = 0.13
        self._progressTextCount = 8
        self._progressText = '>'*self._progressTextCount
        self._suffix = ''
        self._go = True
       
        self._app = QApplication.instance()
       
        QLabel.__init__(self, parent)
        self.setWindowTitle('Progress')
        #self.setWindowModality(QtCore.Qt.WindowModal)
        #self.setWindowFlags(QtCore.Qt.Dialog)
        #self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint)
        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        #self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.CustomizeWindowHint)
        #self.setWindowFlags(QtCore.Qt.Popup)


        
       
        s = 'background-color:pink; padding: 30'
        self.setStyleSheet(s)

        
       
        
   
    def closeEvent(self, event):
        self._go = False
       
        QLabel.closeEvent(self, event)
   
    def _run(self):
        self._thread = QThread(self)
       
        def run():
            try:
                self._actionReturned = self._action(*self._args, **self._kwargs)
                self._actionFailed = False
            except:
                self._actionFailed = True
                self._actionException = traceback.format_exc()
           
            self._actionFinished = True
            self._go = False
       
        self._thread.run = run
        self._thread.start()
   
    def start(self):
        #print 'isVisible:',self.isVisible()
       
        #self.show()
       
        #print 'isVisible:',self.isVisible()
       
        if self._action:
            self._run()
       
        start = time.time()
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.movie = QMovie(r"Loading1.gif")
            # 设置cacheMode为CacheAll时表示gif无限循环，注意此时loopCount()返回-1
        self.movie.setCacheMode(QMovie.CacheAll)
            # 播放速度
        self.movie.setSpeed(100)
        self.setMovie(self.movie)
        self.resize(200,200)
        self.move(300,150)
        while self._go:
            passedTime = time.time() - start
           
            if passedTime >= self._waitSeconds:
                if self.isVisible() == False:
                    self.show()
           
            passedTime = '%d' % passedTime
            suffix = self._suffix.ljust(self._progressTextCount, ' ')
            txt = '%s%s  %s  ' % (self._text, suffix, passedTime)
           
            #self.setText(txt)

            
            

            self.movie.start()

            
            self._app.processEvents()
           
            if self._suffix == self._progressText:
                self._suffix = ''
            else:
                self._suffix += '>'
           
            time.sleep(self._sleepSecond)
       
        else:
            self._thread.quit()
            self.close()
           
            if self._actionFailed:
                raiseExceptionDialog(self._actionException)
           
            return self._actionReturned

#*******************************************************************
#*******************************************************************
#***************************布局类**********************************
#*******************************************************************
#*******************************************************************
class graphicsView(QGraphicsView):
    def __init__(self,parent=None):
        super(graphicsView,self).__init__(parent)
        #QObject.connect(self, SIGNAL('mousePressEvent()'),self.mousePressEvent)
        self.image=""
        QObject.connect(self, SIGNAL('mousePressEvent()'),self.mousePressEvent)

        

        
    def wheelEvent(self, event):
        
        global image_name
        self.image=image_name
        if(image_name!=""):
            value=event.delta()
            if event.delta() >= 0:
                self.width =self.image.width()
                self.height=self.image.height()
                if self.width< 1200:
                    self.width =self.width*1.5
                    self.height=self.height*1.5
                    pic=self.image.scaled(self.width,self.height,aspectRatioMode=Qt.KeepAspectRatio)
                    self.graphicsView.removeItem(self.item)
                    item1= QGraphicsPixmapItem(pic)

                    self.graphicsView= QGraphicsScene()
                    self.graphicsView.addItem(item1)                
                    self.setScene(self.graphicsView)
                    #self.setAlignment(Qt.AlignCenter and Qt.AlignTop)
                    self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
                    self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
                    self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                    self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                    self.setFrameShape(QFrame.NoFrame)
                    #self.setBackgroundBrush(QBrush(QColor(70, 170, 80)))
                            
                    self.item=item1
                    
                elif self.width< 300:
                    self.width =self.width*1.2
                    self.height=self.height*1.2
                    pic=self.image.scaled(self.width,self.height,aspectRatioMode=Qt.KeepAspectRatio)
                    self.graphicsView.removeItem(self.item)

                    self.graphicsView= QGraphicsScene()
                    item1= QGraphicsPixmapItem(pic)               
                    self.graphicsView.addItem(item1)                
                    self.setScene(self.graphicsView)
                    #self.setAlignment(Qt.AlignCenter and Qt.AlignTop)
                    self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
                    self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
                    self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                    self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                    self.setFrameShape(QFrame.NoFrame)
                    #self.setBackgroundBrush(QBrush(QColor(70, 170, 80)))
                    self.item=item1
            elif event.delta() <=  0:
                
        
                self.width =self.image.width()
                self.height=self.image.height()
                if self.width>800:
                    self.width =self.width*0.5
                    self.height=self.height*0.5
                    pic=self.image.scaled(self.width,self.height,Qt.IgnoreAspectRatio)
                    
                    self.graphicsView.removeItem(self.item)
            
             
                    self.graphicsView= QGraphicsScene()
                    
                    item1 = QGraphicsPixmapItem(pic)               
                    self.graphicsView.addItem(item1)
                    
                    self.setScene(self.graphicsView)
                    #self.setAlignment(Qt.AlignCenter or Qt.AlignTop)
                    self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
                    self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
                    self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                    self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                    self.setFrameShape(QFrame.NoFrame)
                    #self.setBackgroundBrush(QBrush(QColor(50, 200, 100)))
                    
                    
                    self.item=item1
                    
                    
                elif self.width>400:
                    self.width =self.width*0.75
                    self.height=self.height*0.75
                    pic=self.image.scaled(self.width,self.height,Qt.IgnoreAspectRatio)
                    
                    self.graphicsView.removeItem(self.item)
            
             
                    self.graphicsView= QGraphicsScene()
                    
                    item1 = QGraphicsPixmapItem(pic)               
                    self.graphicsView.addItem(item1)

                    self.setScene(self.graphicsView)
                    #self.setAlignment(Qt.AlignCenter or Qt.AlignTop)
                    self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
                    self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
                    self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                    self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                    self.setFrameShape(QFrame.NoFrame)
                    #self.setBackgroundBrush(QBrush(QColor(50, 200, 100)))
                    
                    
                    self.item=item1
                    


            

        
 

                

           
                
#*******************************************************************
#*******************************************************************
#***************************拖拽类**********************************
#*******************************************************************
#*******************************************************************

class MyLineEdit(QLineEdit):
        def __init__( self, parent=None ):
            super(MyLineEdit, self).__init__(parent)
            #self.setDragEnabled(True)
            pass
        def dragEnterEvent( self, event ):
            
            data = event.mimeData()
            urls = data.urls()
            if ( urls and urls[0].scheme() == 'file' ):
                event.acceptProposedAction()
        def dragMoveEvent( self, event ):
            data = event.mimeData()
            urls = data.urls()
            if ( urls and urls[0].scheme() == 'file' ):
                event.acceptProposedAction()

        def dropEvent( self, event ):
            data = event.mimeData()
            urls = data.urls()
            if ( urls and urls[0].scheme() == 'file' ):
                filepath = str(urls[0].path())[1:]
                filepath=filepath.decode('utf-8')
                self.setText(filepath)


#*******************************************************************
#*******************************************************************
#***************************功能类**********************************
#*******************************************************************
#*******************************************************************
class bilibili_(QWidget):
    
    def __init__(self):
        super(bilibili_,self).__init__()

        #self.setWindowFlags(Qt.Window)
        self.setWindowTitle(u"Vedio Download Tool")
        self.p=None
        
        self.initUI()
    def initUI(self):
        #人员信息统计并从空添加，使用列表即可。
        #self._tree=Treeview()
        #self._list=Listview()

        down_address=QLabel(u'输入下载地址：')
        self.down_address=QLineEdit("https://www.bilibili.com/video/BV1K7411b7Gp?from=search&seid=14568016733497290075")
        analyze=QPushButton(u"解析")

        
        
        self._tree=graphicsView(self)
 
        
        
        save_adrss=QLabel(u'下载位置：')
        self.save_address=MyLineEdit()
        self.save_adrss_look=QPushButton(u"==>：")
        
        self.start_down=QPushButton(u"下载视频")
        comp_video =QPushButton(u"合并视频")
        del_viedo=QPushButton(u"清除缓存")
        open_video =QPushButton(u"缓存位置")

        file_name=QLabel(u'视频名称：')
        self.file_name=QLineEdit(u"")
        self.file_name.setPlaceholderText(u'自动获取')
        time_pos=QLabel(u"进度")
        self.time_pos=QLineEdit(u"0")
        self.pbar = QProgressBar()


        
        laty_1=QHBoxLayout()
        laty_1.addWidget(down_address)
        laty_1.addWidget(self.down_address)
        laty_1.addWidget(analyze)
     

        laty_2=QHBoxLayout()
        laty_2.addWidget(self._tree)
        
        
      

        laty_3=QHBoxLayout()
        laty_3.addWidget(save_adrss)
        laty_3.addWidget(self.save_address)
        laty_3.addWidget(self.save_adrss_look)


        laty_4=QHBoxLayout()
        laty_4.addWidget(file_name,1)
        laty_4.addWidget(self.file_name,7)
        laty_4.addWidget(time_pos,1)
        laty_4.addWidget(self.pbar ,2)

        laty_5=QHBoxLayout()
        laty_5.addWidget(self.start_down)
        laty_5.addWidget(comp_video)
        laty_5.addWidget(del_viedo)
        laty_5.addWidget(open_video)


        all_lay=QVBoxLayout()
        all_lay.addLayout(laty_1)
        all_lay.addLayout(laty_2)
        all_lay.addLayout(laty_3)
        all_lay.addLayout(laty_4)
        all_lay.addLayout(laty_5)

        self.setLayout(all_lay)
        
        self.resize(800,550)

        analyze.clicked.connect(self.resolve)
        self.save_adrss_look.clicked.connect(self.saveAdrss)
        self.start_down.clicked.connect(self.startDownload)
        comp_video.clicked.connect(self.compVideo)
        del_viedo.clicked.connect(self.delVideo)
        open_video.clicked.connect(self.openVideo)
        self.show()



        
             
    

        

    @showProgress(label="My label")
    def startDownload(self):
        
        if str(self.down_address.text())=="" or str(self.save_address.text())=="":
            QMessageBox.information(self,u"提示", u"请输入网址和下载地址，视频名称可不写")
            return

        url=str(self.down_address.text())
        title= str(self.file_name.text())
        response = requests.get(url, headers=headers)
    
        regt= re.compile(r'https://www.bilibili.com/video/av(\d+)/')
        av_num=re.findall(regt,response.text)

        aid=av_num[0]

        #print aid

        use_url = 'https://api.bilibili.com/x/web-interface/view?aid=%s' % (aid,)
        urllib3.disable_warnings() 
        response = requests.get(use_url, headers=headers, verify=False) 
        content = json.loads(response.text)

        cid = content["data"]["pages"][0]["cid"]

        #print cid

        url_api = 'https://api.bilibili.com/x/player/playurl?cid={}&avid={}&qn={}'.format(cid, aid, 960)
        #print url_api 
        htmls = requests.get(url_api, headers=headers).json()

       
        

        headerss={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36","Referer":"https://www.bilibili.com/video/"+aid}
        
        video_address = htmls['data']['durl'][0]['url']
        #print video_address

        downpos=str(self.save_address.text()).decode('utf-8')
        new_name=downpos+"/" + title+".flv"

        self.start_down.setEnabled(False)
        print new_name
 
        try:
            if not os.path.exists(new_name):
                 with closing(requests.get(video_address,headers=headerss,stream=True)) as response:
                    chunk_size = 2048  # 单次请求最大值
                    content_size = int(response.headers['content-length'])  # 内容体总大小
                    data_count = 0
                    with open(new_name, "wb") as file:
                        for data in response.iter_content(chunk_size=chunk_size):
                            file.write(data)
                            data_count = data_count + len(data)
                            now_jd = (float(data_count) / content_size) * 100
                            print("文件下载进度：%.2f%s".decode("utf-8") % (now_jd,"%"))
                 
                           
            self.pbar.setValue(100)
            self.start_down.setEnabled(True)
        except Exception as e:
                print e

        
    def resolve(self):
        
        if str(self.down_address.text())=="":
            QMessageBox.information(self,u"提示", u"请输入网址")
            return
        #currentPos=os.path.abspath(os.path.dirname(__file__))
        #os.chdir(currentPos)
        url=str(self.down_address.text())
        response = requests.get(url, headers=headers)
        
        title=re.findall("<title .*?>(.*?)</title>",response.text)
        title = re.sub("[~ ゜-゜&;？❤()]+".decode("utf8"), "".decode("utf8"),title[0])
        name="cache/text.html"
        with open(name, "wb") as f:
            f.write((response.text).encode("utf-8"))
        
        regt= re.compile(r'(https://www.bilibili.com/video/av\d+/)')
        av_num=re.findall(regt,response.text)

        aid=av_num[0]
        
        self.down_address.setText(aid)
        

 
        if title!="" and av_num!=[]:
            self.loadImage(av_num[0])
            self.file_name.setText(str(title).decode("utf-8"))
            #QMessageBox.information(self,u"提示", u"解析完成")
        else:
            QMessageBox.information(self,u"提示", u"解析失败，无法下载")
            
    def image_to_byte_array(self,html):#将jpg字节转换为png字节
        byte_stream = BytesIO(html)  # 把请求到的数据转换为Bytes字节流
        roiImg = Image.open(byte_stream)   # Image打开Byte字节流数据
        #roiImg.show()   #显示图片
        imgByteArr = io.BytesIO()     
        roiImg.save(imgByteArr, format='PNG') 
        imgByteArr = imgByteArr.getvalue()
        return imgByteArr

    def loadImage(self,url):
        try:
            reg = re.compile(r'https:/.*?av(\d+)/')
            av=re.findall(reg,url)[0]
            use_url = 'https://api.bilibili.com/x/web-interface/view?aid=%s' % (av,)
            urllib3.disable_warnings() 
            response = requests.get(use_url, headers=headers, verify=False) 
            content = json.loads(response.text)
  
            statue_code = content.get('code')
            if statue_code == 0:
                img_url=(content.get('data').get('pic'))
                

                req = requests.get(img_url,headers=headers)
                html=req.content
                pic_address= self.image_to_byte_array(html)
            
                self._tree.image=QPixmap()
                self._tree.image.loadFromData(pic_address)
                self._tree.graphicsView= QGraphicsScene()            
                self._tree.item = QGraphicsPixmapItem(self._tree.image)               
                self._tree.graphicsView.addItem(self._tree.item)                
                self._tree.setScene(self._tree.graphicsView)
                global image_name
                image_name=self._tree.image
                    
        except Exception as e:
            QMessageBox.information(self,u"提示", u"图像解析失败")
            
    def compVideo(self):

        QMessageBox.information(self,u"提示", u"功能取消！")  
            
       
    def delVideo(self):
        QMessageBox.information(self,u"提示", u"功能取消！")  
                        
           
    def openVideo(self):
        
        if os.path.exists(ffpmpegRoot+"/cache/history.part"):
            with open(ffpmpegRoot+"/cache/history.part") as file:
                filedata= json.loads(file.read())
                filepos=filedata[0]
                filename= filedata[1]
        else:
            filepos=""
            filename=""
        if str(self.save_address.text())!="" and str(self.file_name.text())!="":
            path= str(self.save_address.text()).decode("utf-8")
            if os.path.isdir(path):
                os.startfile(path)
        elif str(self.save_address.text())!='' and str(self.file_name.text())=="":
            path= str(self.save_address.text()).decode("utf-8")
            self.file_name.setText(filename)
        elif str(self.save_address.text())=='' and str(self.file_name.text())!="":
            self.save_address.setText(filepos)
        else:
            self.save_address.setText(filepos)
            self.file_name.setText(filename)
            #os.startfile(filepos)

            
            

            
        
 
   
    def saveAdrss(self):
        #利用文件保存对话框获取文件的路径名称，将存在的json,txt文件拷贝至指定位置。
        
        
        filename = QFileDialog.getExistingDirectory()
        
        if filename:
            filename=str(filename).decode('utf-8')
            filename=filename.replace("\\",'/')
            self.save_address.setText(filename)
        else:
            pass
            #QMessageBox.information(self,u'提示页面',u'取消成功')



#*******************************************************************
#*******************************************************************
#***************************主函数***********************************
#*******************************************************************
#******************************************************************* 

if __name__ == '__main__': 
    app = QApplication(sys.argv)
    bili = bilibili_()
    bili.show()
    sys.exit(app.exec_())
