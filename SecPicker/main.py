import os
import sys
import time
import hashlib
import pandas as pd
import tempfile
import random
import traceback
from loguru import logger
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon,QPainter,QPixmap,QDesktopServices
from qfluentwidgets import *
if os.name == 'nt':
    from win32com.client import Dispatch

temp_dir = tempfile.gettempdir()
VERSION = "v33550336.402604032"
CODENAME = "Robin"
APIVER = 1
error_dialog = None
tray = None
unlocked = [False,False]

QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

class Config(QConfig):
    allowRepeat = ConfigItem("General","allowRepeat",False,BoolValidator())
    supportCS = ConfigItem("General", "supportCS", False, BoolValidator())
    chooseKey = ConfigItem("General","chooseKey","ctrl+w")
    autoStartup = ConfigItem("General","autoStartup",False,BoolValidator())
    lockNameEdit = ConfigItem("Secure","lockNameEdit",False,BoolValidator())
    lockConfigEdit = ConfigItem("Secure","lockConfigItem",False,BoolValidator())
    keyChecksum = ConfigItem("Secure","keyChecksum","0")
    logLevel = OptionsConfigItem("Debug", "logLevel", "INFO", OptionsValidator(["DEBUG", "INFO", "WARNING","ERROR"]), restart=True)
    apiver = ConfigItem("Version", "apiver", 1)

cfg = Config()
qconfig.load("app/plugin/SecPicker/config.json", cfg)
cfg.set(cfg.apiver,APIVER)

if os.path.exists("secpicker.log"):
    os.remove("secpicker.log")
logger.remove(0)
logger.add("secpicker.log")
logger.add(sys.stderr, level=cfg.get(cfg.logLevel))

logger.info("「她将自己的生活形容为一首歌，而那首歌的开始阴沉而苦涩。⌋")

def hookExceptions(exc_type, exc_value, exc_tb):
    error_details = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    if "TypeError: disconnect() of all signals failed" in error_details:
        return
    logger.error(error_details)
    if not error_dialog:
        w = ErrorDialog(error_details)
        w.exec()
sys.excepthook = hookExceptions

class ErrorDialog(Dialog):  # 重大错误提示框
    def __init__(self, error_details='Traceback (most recent call last):', parent=None):
        # KeyboardInterrupt 直接 exit
        if error_details.endswith('KeyboardInterrupt') or error_details.endswith('KeyboardInterrupt\n'):
            sys.exit()

        super().__init__(
            'NamePicker 崩溃报告',
            '抱歉！NamePicker 发生了严重的错误从而无法正常运行。您可以保存下方的错误信息并向他人求助。'
            '若您认为这是程序的Bug，请点击“报告此问题”或联系开发者。',
            parent
        )
        global error_dialog
        error_dialog = True

        self.is_dragging = False
        self.drag_position = QPoint()
        self.title_bar_height = 30
        self.title_layout = QHBoxLayout()

        self.error_log = PlainTextEdit()
        self.ignore_error_btn = PushButton(FluentIcon.INFO, '忽略错误')
        self.report_problem = PushButton(FluentIcon.FEEDBACK, '报告此问题')
        self.copy_log_btn = PushButton(FluentIcon.COPY, '复制日志')
        self.restart_btn = PrimaryPushButton(FluentIcon.SYNC, '重新启动')

        self.titleLabel.setText('出错了（；´д｀）ゞ')
        self.titleLabel.setStyleSheet("font-family: Microsoft YaHei UI; font-size: 25px; font-weight: 500;")
        self.error_log.setReadOnly(True)
        self.error_log.setPlainText(error_details)
        self.error_log.setFixedHeight(200)
        self.restart_btn.setFixedWidth(150)
        self.yesButton.hide()
        self.cancelButton.hide()  # 隐藏取消按钮
        self.title_layout.setSpacing(12)

        # 按钮事件
        self.report_problem.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(
                'https://github.com/NamePickerOrg/NamePicker/issues/'))
        )
        self.copy_log_btn.clicked.connect(self.copy_log)
        self.restart_btn.clicked.connect(self.restart)
        self.ignore_error_btn.clicked.connect(lambda:self.close())

        self.title_layout.addWidget(self.titleLabel)
        self.textLayout.insertLayout(0, self.title_layout)  # 页面
        self.textLayout.addWidget(self.error_log)
        self.buttonLayout.insertStretch(0, 1)  # 按钮布局
        self.buttonLayout.insertWidget(0, self.copy_log_btn)
        self.buttonLayout.insertWidget(1, self.report_problem)
        self.buttonLayout.insertWidget(2, self.ignore_error_btn)
        self.buttonLayout.insertStretch(1)
        self.buttonLayout.insertWidget(5, self.restart_btn)

    def restart(self):
        if tray:
            tray.systemTrayIcon.hide()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def copy_log(self):  # 复制日志
        QApplication.clipboard().setText(self.error_log.toPlainText())
        Flyout.create(
            icon=InfoBarIcon.SUCCESS,
            title='复制成功！ヾ(^▽^*)))',
            content="日志已成功复制到剪贴板。",
            target=self.copy_log_btn,
            parent=self,
            isClosable=True,
            aniType=FlyoutAnimationType.PULL_UP
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() <= self.title_bar_height:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.move(event.globalPos() - self.drag_position)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False

    def closeEvent(self, event):
        global error_dialog
        error_dialog = False
        event.ignore()
        self.hide()
        self.deleteLater()

class Choose(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.names = {}
        self.sexlen = [0,0,0]
        self.sexl = [[],[],[]]
        self.numlen = [0,0,0]
        self.numl = [[],[],[]]
        self.chosen = []
        self.loadname()

        self.hBoxLayout = QHBoxLayout(self)
        self.options = QVBoxLayout(self)

        self.pickbn = PrimaryPushButton("点击抽选")
        self.pickbn.clicked.connect(self.pickcb)
        self.pickbn.setShortcut(cfg.get(cfg.chooseKey))
        self.pickbn.adjustSize()
        self.options.addWidget(self.pickbn,5)

        self.table = TableWidget(self)
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setRowCount(10)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["姓名","学号"])

        self.pn = QWidget()
        self.pnl = QHBoxLayout(self)
        self.pnLabel = SubtitleLabel("抽选数量", self)
        self.pickNum = SpinBox()
        self.pickNum.setRange(1, len(self.names["name"]))
        self.pnl.addWidget(self.pnLabel, 10)
        self.pnl.addWidget(self.pickNum, 5)
        self.pn.setLayout(self.pnl)
        self.options.addWidget(self.pn,5)

        self.sep = QWidget()
        self.sepl = QHBoxLayout(self)
        self.seLabel = SubtitleLabel("性别偏好", self)
        self.sexCombo = ComboBox()
        self.sexCombo.addItems(["都抽","只抽男","只抽女","只抽特殊性别"])
        self.sepl.addWidget(self.seLabel, 10)
        self.sepl.addWidget(self.sexCombo, 5)
        self.sep.setLayout(self.sepl)
        self.options.addWidget(self.sep, 5)

        self.nup = QWidget()
        self.nul = QHBoxLayout(self)
        self.nuLabel = SubtitleLabel("学号偏好", self)
        self.numCombo = ComboBox()
        self.numCombo.addItems(["都抽", "只抽单数", "只抽双数"])
        self.nul.addWidget(self.nuLabel, 10)
        self.nul.addWidget(self.numCombo, 5)
        self.nup.setLayout(self.nul)
        self.options.addWidget(self.nup, 5)

        self.scrollArea = ScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.opt = QWidget()
        self.opt.setLayout(self.options)

        self.hBoxLayout.addWidget(self.table,2)
        self.hBoxLayout.addWidget(self.opt,3,Qt.AlignCenter)
        self.setObjectName(text.replace(' ', 'Choose'))
        logger.info("主界面初始化完成")

    def pick(self):
        global cfg
        if self.sexCombo.currentText() != "都抽":
            if self.sexCombo.currentText() == "只抽男":
                le = self.sexlen[0]
                tar = self.sexl[0]
            elif self.sexCombo.currentText() == "只抽女":
                le = self.sexlen[1]
                tar = self.sexl[1]
            else:
                le = self.sexlen[2]
                tar = self.sexl[2]
        else:
            le = self.length
            tar = self.names["name"]

        if self.numCombo.currentText() != "都抽":
            if self.numCombo.currentText() == "只抽双数":
                tar = list(set(tar) & set(self.numl[0]))
                le = len(tar)
            else:
                tar = list(set(tar) & set(self.numl[1]))
                le = len(tar)
        le = len(tar)
        if le != 0:
            chs = random.randint(0, le - 1)
            if not cfg.get(cfg.allowRepeat):
                if len(self.chosen) >= le:
                    self.chosen = []
                    chs = random.randint(0, le - 1)
                else:
                    while chs in self.chosen:
                        chs = random.randint(0, le - 1)
                self.chosen.append(chs)
                logger.debug(self.chosen)
            tmp = {"name":tar[chs],"no":str(self.names["no"][self.names["name"].index(tar[chs])])}
            for i in self.names.keys():
                if i == "name" or i == "no":
                    continue
                tmp[i] = str(self.names[i][self.names["name"].index(tar[chs])])
            return tmp
        else:
            return "尚未抽选"

    def pickcb(self):
        logger.debug("pickcb被调用")
        self.table.setRowCount(self.pickNum.value())
        namet = []
        namel = []
        for i in range(self.pickNum.value()):
            n = self.pick()
            if n != "尚未抽选":
                namet.append(n)
            else:
                self.nost()

        if cfg.get(cfg.supportCS):
            with open("%s\\unread" % temp_dir, "w", encoding="utf-8") as f:
                f.write("111")
            with open("%s\\res.txt" % temp_dir, "w", encoding="utf-8") as f:
                for i in namet:
                    namel.append("%s（%s）" % (i[0], i[1]))
                f.writelines(namel)
            logger.info("文件存储完成")
        else:
            for i in range(len(namet)):
                self.table.setItem(i, 0, QTableWidgetItem(namet[i]["name"]))
                self.table.setItem(i, 1, QTableWidgetItem(namet[i]["no"]))
            logger.debug("表格设置完成")
    def nost(self):
        InfoBar.error(
            title='错误',
            content="没有符合筛选条件的学生",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM,
            duration=3000,
            parent=self
        )

    def loadname(self):
        try:
            name = pd.read_csv("names.csv", sep=",", header=0)
            name = name.to_dict()
            self.names["name"] = list(name["name"].values())
            self.names["sex"] = list(name["sex"].values())
            self.names["no"] = list(name["no"].values())
            for k in self.names.keys():
                for i in range(len(self.names[k])):
                    self.names[k][i] = str(self.names[k][i])
            self.length =len(name["name"])
            self.sexlen[0] = self.names["sex"].count("0")
            self.sexlen[1] = self.names["sex"].count("1")
            self.sexlen[2] = self.names["sex"].count("2")
            for i in self.names["name"]:
                if int(self.names["sex"][self.names["name"].index(i)]) == 0:
                    self.sexl[0].append(i)
                elif int(self.names["sex"][self.names["name"].index(i)]) == 1:
                    self.sexl[1].append(i)
                else:
                    self.sexl[2].append(i)

            for i in self.names["name"]:
                if int(self.names["no"][self.names["name"].index(i)])%2==0:
                    self.numl[0].append(i)
                else:
                    self.numl[1].append(i)
            self.numlen[0] = len(self.numl[0])
            self.numlen[1] = len(self.numl[1])
            logger.info("名单加载完成")
        except FileNotFoundError:
            logger.warning("没有找到名单文件")
            with open("names.csv","w",encoding="utf-8") as f:
                st  = ["name,sex,no\n","某人,0,1"]
                f.writelines(st)
            w = Dialog("没有找到名单文件", "没有找到名单文件，已为您创建默认名单，请自行编辑", self)
            w.exec()
            self.loadname()

class Settings(QFrame):
    def __init__(self, text: str, parent=None):
        global cfg
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', 'Settings'))
        self.stack = QStackedWidget(self)
        self.df = QVBoxLayout(self)
        self.scrollArea = ScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.optv =QWidget()
        self.opts = QVBoxLayout(self.optv)
        self.tlog = PushButton(FluentIcon.DOCUMENT,"测试日志输出")
        self.tcrash = PushButton(FluentIcon.CLOSE,"测试引发崩溃")
        self.tlog.clicked.connect(self.testLog)
        self.tcrash.clicked.connect(self.testCrash)
        self.cKey=SettingCard(
            icon=FluentIcon.FONT,
            title="抽选快捷键",
            content="设置抽选的快捷键（不区分大小写，使用英文加号(+)串联多个按键），重启生效"
        )
        self.cKeyInput = LineEdit()
        self.cKeyInput.setPlaceholderText("输入快捷键")
        self.cKeyInput.setText(cfg.get(cfg.chooseKey))
        self.cKey.hBoxLayout.addStretch(20)
        self.cKey.hBoxLayout.addWidget(self.cKeyInput)
        self.cKey.hBoxLayout.addStretch(1)
        self.cKeyInput.textChanged.connect(lambda :cfg.set(cfg.chooseKey,self.cKeyInput.text()))
        self.lock = PushSettingCard(
            icon=FluentIcon.CLOSE,
            title="锁定功能",
            content="重新锁定已经解锁的功能",
            text="锁定"
        )
        self.lock.clicked.connect(self.relock)
        self.sets = [SubtitleLabel("常规"),
        SwitchSettingCard(
            configItem=cfg.allowRepeat,
            icon=FluentIcon.LIBRARY,
            title="允许重复点名",
            content="允许点到重复名字"
        ),
        SwitchSettingCard(
            configItem=cfg.supportCS,
            icon=FluentIcon.LINK,
            title="课表软件联动",
            content="启用后将在ClassIsland/Class Widgets上（而非主界面）显示抽选结果，需要安装对应插件"
        ),
        SwitchSettingCard(
            configItem=cfg.autoStartup,
            icon=FluentIcon.POWER_BUTTON,
            title="开机自启",
            content="开机时自动启动（对于非Windows系统无效）"
        ),
        self.cKey,
        SubtitleLabel("安全设置"),
        HyperlinkCard(
            icon=FluentIcon.INFO,
            title="使用前必读",
            content="以下设置项在初次打开时会为您生成密钥，请妥善保管\n您需要凭密钥解锁限制，如果丢失请参照文档执行操作",
            url="https://namepicker-docs.netlify.app/guide/quickstart/lock.html",
            text="点击查看文档"
        ),
        self.lock,
        SwitchSettingCard(
         configItem=cfg.lockConfigEdit,
         icon=FluentIcon.HIDE,
         title="禁用设置编辑",
         content="启用后，将无法进行软件内设置编辑，重启生效"
        ),
        SubtitleLabel("调试"),
        ComboBoxSettingCard(
            configItem=cfg.logLevel,
            icon=FluentIcon.DEVELOPER_TOOLS,
            title="日志记录级别",
            content="日志的详细程度（重启以应用更改）",
            texts=["DEBUG", "INFO", "WARNING","ERROR"]
        ),self.tlog,
        self.tcrash]
        for i in self.sets:
            self.opts.addWidget(i)
        self.scrollArea.setStyleSheet("QScrollArea{background: transparent; border: none}")
        self.scrollArea.setWidget(self.optv)
        self.optv.setStyleSheet("QWidget{background: transparent}")
        self.df.addWidget(TitleLabel("设置"))
        QScroller.grabGesture(self.scrollArea.viewport(), QScroller.LeftMouseButtonGesture)
        # self.addSubInterface(self.scrollArea,"Settings","本体设置")
        # self.pivot.setCurrentItem("Settings")
        self.df.addWidget(self.scrollArea)
        cfg.autoStartup.valueChanged.connect(self.startupChange)
        cfg.lockNameEdit.valueChanged.connect(self.checkLock)
        cfg.lockConfigEdit.valueChanged.connect(self.checkLock)
        logger.info("设置界面初始化完成")

    def startupChange(self):
        if cfg.get(cfg.autoStartup):
            self.setStartup()
        else:
            self.removeStartup()

    def setStartup(self):
        if os.name != 'nt':
            return
        file_path='%s/main.exe'%os.path.dirname(os.path.abspath(__file__))
        icon_path = 'assets/favicon.ico'
        startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        name = os.path.splitext(os.path.basename(file_path))[0]  # 使用文件名作为快捷方式名称
        shortcut_path = os.path.join(startup_folder, f'{name}.lnk')
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = file_path
        shortcut.WorkingDirectory = os.path.dirname(file_path)
        shortcut.IconLocation = icon_path  # 设置图标路径
        shortcut.save()

    def removeStartup(self):
        file_path = '%s/main.exe' % os.path.dirname(os.path.abspath(__file__))
        name = os.path.splitext(os.path.basename(file_path))[0]
        startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        shortcut_path = os.path.join(startup_folder, f'{name}.lnk')
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)

    def testLog(self):
        logger.debug("这是Debug日志")
        logger.info("这是Info日志")
        logger.warning("这是Warning日志")
        logger.error("这是Error日志")

    def testCrash(self):
        raise Exception("NamePicker实际上没有任何问题，是你自己手贱引发的崩溃")

    def checkLock(self):
        global unlocked
        if cfg.get(cfg.keyChecksum) == "0" and (cfg.get(cfg.lockNameEdit) or cfg.get(cfg.lockConfigEdit)):
            kd = str(time.time())
            key = bytes(kd.encode("utf-8"))
            keymd5 = hashlib.md5(key).hexdigest()
            cfg.set(cfg.keyChecksum,keymd5)
            logger.info("生成密钥md5")
            with open("KEY","w",encoding="utf-8") as f:
                f.write(kd)
            w = Dialog("生成完成", "由于您是初次启用安全设置，已为您在软件目录生成密钥文件（文件名：KEY），请妥善保管该文件，您将来会需要凭该文件解锁限制", self)
            w.exec()
            if cfg.get(cfg.lockNameEdit):
                unlocked[0] = True
            elif cfg.get(cfg.lockConfigEdit):
                unlocked[1] = True

    def relock(self):
        global unlocked
        unlocked = [False, False]

class About(QFrame):
    def __init__(self, text: str, parent=None):
        global cfg
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', 'About'))
        self.df = QVBoxLayout(self)
        self.about = TitleLabel("关于")
        self.image = ImageLabel("assets/NamePicker.png")
        self.ver = SubtitleLabel("SecPicker - Codename %s (Based on NamePicker v2.0.2d1dev)"%(CODENAME))
        self.author = BodyLabel("By 灵魂歌手er（Github @LHGS-github）")
        self.cpleft = BodyLabel("本软件基于GNU GPLv3获得授权")

        self.linkv = QWidget()
        self.links = QHBoxLayout(self.linkv)
        self.ghrepo = HyperlinkButton(FluentIcon.GITHUB, "https://github.com/NamePickerOrg/NamePicker", 'GitHub Repo')
        self.docsite = HyperlinkButton(FluentIcon.DOCUMENT,"https://namepicker-docs.netlify.app/","官方文档")
        self.links.addWidget(self.ghrepo)
        self.links.addWidget(self.docsite)

        self.df.addWidget(self.about)
        self.df.addWidget(self.image)
        self.df.addWidget(self.ver)
        self.df.addWidget(self.author)
        self.df.addWidget(self.cpleft)
        self.df.addWidget(self.linkv)
        logger.info("关于界面初始化")

class KeyMsg(MessageBoxBase):
    def __init__(self, parent=None,check="NameEdit"):
        super().__init__(parent)
        self.check = check
        self.titleLabel = SubtitleLabel('选择KEY文件')
        self.explain = BodyLabel("选择KEY文件以解锁该功能")
        self.selectButton = PrimaryPushButton("点击选择文件")
        self.selectButton.clicked.connect(self.checkFile)
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.explain)
        self.viewLayout.addWidget(self.selectButton)

    def checkFile(self):
        global unlocked
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_filter = "All Files (*)"
        fn = QFileDialog.getOpenFileNames(self, "选择KEY文件", "", file_filter, options=options)
        logger.debug(fn)
        if fn[0]:
            with open(fn[0][0],"r",encoding="utf-8") as f:
                key = str(f.read()).encode("utf-8")
                logger.debug(key)
                keymd5 = hashlib.md5(key).hexdigest()
                logger.debug(keymd5)
                if keymd5 == cfg.get(cfg.keyChecksum):
                    if self.check == "NameEdit":
                        unlocked[0] = True
                    else:
                        unlocked[1] = True
                    InfoBar.success(
                        title='校验成功',
                        content="您已完成校验，现在应该可以使用对应功能",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.BOTTOM,
                        duration=3000,
                        parent=self
                    )
                else:
                    InfoBar.error(
                        title='校验失败',
                        content="未能成功验证，请确认是否选择了正确的文件",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.BOTTOM,
                        duration=3000,
                        parent=self
                    )
        else:
            InfoBar.error(
                title='校验失败',
                content="请选择文件",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM,
                duration=3000,
                parent=self
            )

class App(FluentWindow):
    def __init__(self):
        super().__init__()
        qconfig.theme = Theme.AUTO
        setTheme(Theme.AUTO)
        self.Choose = Choose("随机抽选",self)
        self.Settings = Settings("设置",self)
        self.About = About("关于", self)
        self.initNavigation()
        self.initWindow()
        self.stackedWidget.currentChanged.connect(self.checkLocker)
        logger.info("主界面初始化")

    def checkLocker(self):
        global unlocked
        current = self.stackedWidget.currentWidget()
        logger.debug(current)
        if current == self.Settings and cfg.get(cfg.lockConfigEdit) and not unlocked[1]:
            w = KeyMsg(self, "Settings")
            w.exec()
            if not unlocked[1]:
                self.switchTo(self.Choose)

    def initNavigation(self):
        self.addSubInterface(self.Choose, FluentIcon.HOME, "随机抽选")
        self.addSubInterface(self.Settings, FluentIcon.SETTING, '设置', NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.About, FluentIcon.INFO, '关于', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(700, 500)
        self.setWindowIcon(QIcon('assets/NamePicker.png'))
        self.setWindowTitle('NamePicker')

    def closeEvent(self, event):
        if "noshortcut" in sys.argv:
            sys.exit(0)
        else:
            self.hide()
            event.ignore()

class ExamplePlugin:
    """示例插件主类"""
    
    def __init__(self):
        self.config_path = "app/plugin/SecPicker/config.json"
        self.config = {}
        self.load_config()
        
    def load_config(self):
        """加载插件配置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "enabled": True,
                    "show_welcome": True,
                    "custom_message": "欢迎使用示例插件！"
                }
                self.save_config()
        except Exception as e:
            logger.error(f"加载插件配置失败: {e}")
            self.config = {}
            
    def save_config(self):
        """保存插件配置"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"保存插件配置失败: {e}")
            
    def get_info(self):
        """获取插件信息"""
        return {
            "name": "SecPicker",
            "version": "v33550336.402604032",
            "description": "NamePicker for SecRandom",
            "author": "灵魂歌手er",
            "enabled": self.config.get("enabled", True)
        }
        
    def execute(self, *args, **kwargs):
        """执行插件主要功能"""
        main = App()
        main.show()
        return "示例插件执行成功"

def show_dialog(parent=None):
    plugin = ExamplePlugin()
    plugin.execute()

def get_plugin_info():
    """获取插件信息"""
    plugin = ExamplePlugin()
    return plugin.execute()
    
def execute_plugin(*args, **kwargs):
    """执行插件功能"""
    plugin = ExamplePlugin()
    return plugin.get_info()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = App()
    main.show()
    sys.exit(app.exec_())