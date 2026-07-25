import pygame as pg
import sys
import math
import random
import subprocess
import os
import json
import re
import tkinter as tk
from tkinter import filedialog as fd
import hmac
import hashlib
import statistics
import pickle
import time
import traceback

pg.init()

with open("stacker.cfg",'r',encoding="utf-8") as f:
    config:dict=json.load(f)                                                  #请优先从config更改配置

#------------------------------------SETTINGS------------------------------------------

DELAY=config.get("DELAY",0)                                                   #ms             [IMPORTANT]
NAME=config.get("NAME","Anonymous")                                           #你的名字,显示在导出的.stack成绩文件中.    TODO:联机以后换成UID
LANGUAGE=config.get("LANGUAGE","chinese_simplified")                          #语言.目前支持:chinese_simplified

INFINITY_MODE=config.get("INFINITY_MODE",False)                               #无敌模式,开启时会显示提示
FORCE_KEEP_TIME=config.get("FORCE_KEEP_TIME",1000)                            #ms 调节游戏结束后阻止用户按下按键的时间(防止结果丢失)
FORGIVENESS_WHEN_LACK=config.get("FORGIVENESS_WHEN_LACK",1.0)                 #percent 当用户帧率低于FPS设定的一半时,对扣血的宽恕比例.比例越高扣血越少.当比例大于0时会显示提示.
ALLOW_EXTRA_HITS_ON_ONE_BEAT=config.get("ALLOW_EXTRA_HITS_ON_ONE_BEAT",True)  #启用时,游戏会像原版一样允许在同一拍多次按键,但是这些非法按键会被记入存档.

VSYNC=config.get("VSYNC",False)                                               #垂直同步
SHOW_FPS=config.get("SHOW_FPS",True)                                          #显示实时帧率
FPS_ROUND=config.get("FPS_ROUND",2)                                           #帧率显示小数点位数
FPS=config.get("FPS",60)                                                      #fps
SIZE=config.get("SIZE",(704,396))                                             #px
FULL_SCREEN=config.get("FULL_SCREEN",False)                                   #设置全屏

KEEP_CUTDOWN_HINT=config.get("KEEP_CUTDOWN_HINT",False)                       #开启后过去砖块上的失误标记不会自动消失
SHOW_OFFSET=config.get("SHOW_OFFSET",True)                                    #显示判定数值
OFFSET_ROUND=config.get("OFFSET_ROUND",2)                                     #判定数值显示小数点位数
SHOW_COMBO=config.get("SHOW_COMBO",True)                                      #显示连击数
SHOW_HEALTH=config.get("SHOW_HEALTH",True)                                    #显示血量
HEALTH_ROUND=config.get("HEALTH_ROUND",2)                                     #血量显示小数点位数
TEXT_MARGIN=config.get("TEXT_MARGIN",5)                                       #不同状态间的间隔(px)
SHOW_MISTAKE_HINT=config.get("SHOW_MISTAKE_HINT",True)                        #当十五时显示明显的视觉提示
TURN_RED_WHEN_MISTAKE=config.get("TURN_RED_WHEN_MISTAKE",True)                #当失误时让部分UI变红

PLAY_END_REACH_SFX=config.get("PLAY_END_REACH_SFX",True)                      #播放结束/满足条件的音效
PLAY_MISTAKE_SFX=config.get("PLAY_MISTAKE_SFX",True)                          #播放失误音效(延迟极高不建议开启)
PLAY_HIT_SFX=config.get("PLAY_HIT_SFX",False)                                 #播放打击音效(延迟较高不建议开启)
END_AND_REACH_VOLUME=config.get("END_AND_REACH_VOLUME",1.0)                   #percent
MISTAKE_VOLUME=config.get("MISTAKE_VOLUME",0.5)                               #percent
HIT_VOLUME=config.get("HIT_VOLUME",0.2)                                       #percent
HIT=config.get("HIT",["resources/sndClapHit.wav"])
REACH_TARGET=config.get("REACH_TARGET",["resources/sndReachTarget.ogg"])
MISTAKE_BIG=config.get("MISTAKE_BIG",["resources/sndMistakeBig.ogg"])
MISTAKE_SMALL=config.get("MISTAKE_SMALL",["resources/sndMistakeSmall2.ogg","resources/sndMistakeSmall3.ogg"])
FAIL=config.get("FAIL",["resources/sndFail.ogg"])

SHOW_LYRIC_IF_POSSIBLE=config.get("SHOW_LYRIC_IF_POSSIBLE",True)              #如果有可能,在屏幕右下角显示实时歌词
LYRIC=config.get("LYRIC",None)                                                #歌词路径.输入None时尝试根据音乐文件名自动匹配.
MUSIC=config.get("MUSIC","snd.wav")                                           #path
BPM=config.get("BPM",75.25)                                                   #bpm
FONT=config.get("FONT","resources/Minecraft AE.ttf")                          #path
EMJ_FONT=config.get("EMJ_FONT","resources/emj.ttf")                           #path
FONT_SCALE=config.get("FONT_SCALE",1.0)                                       #float or int

HIDE_VERSION_INFO=config.get("HIDE_VERSION_INFO",False)                       #隐藏右下角的版本和作者信息

JUDGE_WINDOW=config.get("JUDGE_WINDOW",40)                                    #ms
BIG_MISTAKE_RANGE=config.get("BIG_MISTAKE_RANGE",80)                          #ms
TOTAL_HEALTH=config.get("TOTAL_HEALTH",500)                                   #ms

PALETTE=config.get("PALETTE",[
    (175,87,68),
    (255,204,170),
    (0,228,54),
    (253,163,0),
    (139,119,160),
    (58,169,249),
    (255,236,39),
    (107,91,90),
    (251,120,171),
    (194,195,199),
    (21,135,92)
    ])                                                                        #rgb
BRICK_WIDTH=config.get("BRICK_WIDTH",int(TOTAL_HEALTH/2.5))                   #px
BRICK_HEIGHT=config.get("BRICK_HEIGHT",20)                                    #px
BRICK_MOVE=config.get("BRICK_MOVE",300)                                       #px
BRICKS_SHOW=config.get("BRICKS_SHOW",6)                                       #amount

CAM_MOVE_SPEED=config.get("CAM_MOVE_SPEED",BRICK_HEIGHT/(60/BPM))             #px/s
STAR_GENERATING_ARG=config.get("STAR_GENERATING_ARG",0.01)                    #amount/pixel(possibility)
STAR_SIZE=config.get("STAR_SIZE",5)                                           #px

#------------------------------------SETTINGS END------------------------------------------

SPB=60/BPM
MSPB=60000/BPM

MUSIC_LENGTH=pg.mixer.Sound(MUSIC).get_length()*1000

if PLAY_HIT_SFX:
    HIT_SOUND=[pg.mixer.Sound(i) for i in HIT]
    for i in HIT_SOUND:
        i.set_volume(HIT_VOLUME)

if PLAY_MISTAKE_SFX:
    MISTAKE_BIG_SOUND=[pg.mixer.Sound(i) for i in MISTAKE_BIG]
    MISTAKE_SMALL_SOUND=[pg.mixer.Sound(i) for i in MISTAKE_SMALL]
    for i in MISTAKE_BIG_SOUND+MISTAKE_SMALL_SOUND:
        i.set_volume(MISTAKE_VOLUME)

if PLAY_END_REACH_SFX:
    FAIL_SOUND=[pg.mixer.Sound(i) for i in FAIL]
    REACH_TARGET_SOUND=[pg.mixer.Sound(i) for i in REACH_TARGET]
    for i in FAIL_SOUND+REACH_TARGET_SOUND:
        i.set_volume(END_AND_REACH_VOLUME)

COLOR_BLACK       = (0, 0, 0)          # 背景、填充
COLOR_WHITE       = (255, 255, 255)    # 文字、砖块临时绘制
COLOR_RED         = (255, 60, 60)      # 失误、低血量、警告
COLOR_GOLD        = (248, 182, 45)     # 全连击、强调、成就
COLOR_CYAN_GREEN  = (78, 201, 176)     # 目标进度、解锁提示
COLOR_GREEN       = (22, 198, 12)      # 校验通过
COLOR_GRAY        = (150, 150, 150)    # 次要信息、未校验
COLOR_STAR        = (245, 240, 230)    # 星星粒子
COLOR_BLUE        = (0, 150, 255)      # forgiveness 状态（极少触发）

VERSION="2.1.0"
HMAC_KEY=b""

MODE_NONE=-1
MODE_PLAYING=0
MODE_CALIBRATION=1
MODE_SCORE_DISPLAYING=2

FLAG_NONE=-1
FLAG_GAMEOVER=0
FLAG_QUITTING=1
FLAG_ESCAPING=2
FLAG_CALIBRATION_PREPARE=3
FLAG_ROLLING=4
FLAG_F3_STATUS_HIDING=5
FLAG_SHOW_LYRIC=6
FLAG_CHECK_MODE=7
FLAG_TERMINATE_INPUT=8

#------------------------------------CONST END------------------------------------------

class Language:
    def __init__(self):
        self.languages = {
            "chinese_simplified": 0,
            "english": 1
        }
        self.texts = {
            1: [
                "校准模式!",
                "Calibration Mode!"
            ],
            2: [
                "未选择文件!",
                "No file selected!"
            ],
            3: [
                "卡顿宽恕开启!",
                "Lag forgiveness enabled!"
            ],
            4: [
                "按F2导入成绩,或者按任意键退出!",
                "Press F2 to import score, or press any key to exit!"
            ],
            5: [
                "选择分数快照文件以读取!",
                "Select a score snapshot file to read!"
            ],
            6: [
                "选择分数快照保存位置!",
                "Choose where to save the score snapshot!"
            ],
            7: [
                "用户未选择保存位置",
                "User did not choose a save location"
            ],
            8: [
                "无敌模式开启!",
                "Invincible mode enabled!"
            ],
            9: [
                "ESC 结束游戏",
                "ESC to end game"
            ],
            10: [
                "获得{score}分以继续！",
                "Get {score} points to continue!"
            ],
            11: [
                "参数数量必须为0或2",
                "Number of arguments must be 0 or 2"
            ],
            12: [
                "禁止反序列化{module_name}.{global_name}:可能是恶意文件.尝试更新游戏.",
                "Deserialization of {module_name}.{global_name} is forbidden: possibly a malicious file. Try updating the game."
            ],
            13: [
                "文件未找到:{e}",
                "File not found: {e}"
            ],
            14: [
                "无法打开文件:{e}",
                "Cannot open file: {e}"
            ],
            15: [
                "解码失败:{e}",
                "Decoding failed: {e}"
            ],
            16: [
                "存档格式不正确:{e}",
                "Invalid save format: {e}"
            ],
            17: [
                "未知错误:{e}",
                "Unknown error: {e}"
            ],
            18: [
                "禁止节拍器参赛",
                "Metronome not allowed to compete"
            ],
            19: [
                "生命值:{health}",
                "Health: {health}"
            ],
            20: [
                "再次按下F4清空进度并校准",
                "Press F4 again to clear progress and calibrate"
            ],
            21: [
                "Rhythm Stacker分数快照文件",
                "Rhythm Stacker score snapshot file"
            ],
            22: [
                "Rhythm Stacker分数快照文件(json格式)",
                "Rhythm Stacker score snapshot file (JSON format)"
            ],
            23: [
                "把脚本关掉,现在!",
                "Turn off the script, now!"
            ],
            24: [
                "判定窗口:{window}",
                "Judgment window: {window}"
            ],
            25: [
                "剩余生命:{health}",
                "Remaining health: {health}"
            ],
            26: [
                "总生命:{total_health}",
                "Total health: {total_health}"
            ],
            27: [
                "标准差:{std}",
                "Standard deviation: {std}"
            ],
            28: [
                "评价:{rank}",
                "Rank: {rank}"
            ],
            29: [
                "[!] 无敌模式启用",
                "[!] Invincible mode enabled"
            ],
            30: [
                "[!] 卡顿宽恕减免生命扣除值:{forgiveness_total_health}",
                "[!] Lag forgiveness reduces health deduction by: {forgiveness_total_health}"
            ],
            31: [
                "[!] 检测到{extra_hits}次双压行为,分数可能不反应真实水平.",
                "[!] Detected {extra_hits} double-press actions, score may not reflect true skill."
            ],
            32: [
                "成绩已校验",
                "Score verified"
            ],
            33: [
                "HMAC签名不匹配,无法确认成绩真实性.",
                "HMAC signature mismatch, cannot confirm score authenticity."
            ],
            34: [
                "无法加载分数:{e}",
                "Unable to load score: {e}"
            ],
            35: [
                "再次按下ESC退出",
                "Press ESC again to exit"
            ],
            36: [
                "节奏感评价:{rank}(按任意键保存)",
                "Rhythm rank: {rank} (press any key to save)"
            ],
            37: [
                "游戏结束 评价:{rank}",
                "Game Over - Rank: {rank}"
            ],
            38: [
                "[!] BPM{bpm}高于判定安全阈值,成绩仅供参考.",
                "[!] BPM {bpm} exceeds judgment safety threshold, score is for reference only."
            ],
            39: [
                "宽恕的生命:{forgiveness}",
                "Forgiven health: {forgiveness}"
            ],
            40: [
                "再次按下ESC放弃本次游玩",
                "Press ESC again to abandon this session"
            ],
            41: [
                "你是没睡醒吗",
                "Are you awake?"
            ],
            42: [
                "在保存成绩期间可能未响应,请耐心等待",
                "The program may become unresponsive while saving, please wait patiently"
            ],
            43: [
                "在导入成绩期间可能未响应,请耐心等待",
                "The program may become unresponsive while importing, please wait patiently"
            ],
            44: [
                "已验证!",
                "Verified!"
            ],
            45: [
                "按任意键退出!",
                "Press any key to exit!"
            ],
            46: [
                "欢迎回来,{username}!",
                "Welcome back, {username}!"
            ],
            47: [
                "双击ESC来继续!",
                "Double-click ESC to continue!"
            ],
            48: [
                "再次按下F4清空校准进度并回到游戏",
                "Press F4 again to clear calibration progress and return to game"
            ],
            49: [
                "距离目标:{left}",
                "Distance to target: {left}"
            ],
            50: [
                "{left}",
                "{left}"
            ],
            51: [
                "跟着节拍按键!",
                "Follow the beat and press!"
            ]
        }
    
    def __call__(self, id, language=None, **kwargs):
        language = LANGUAGE if language is None else language
        language_id = self.languages[language]
        return self.texts[id][language_id].format(**kwargs)
#------------------------------------LANGUAGE END------------------------------------------

class RSUnpickler(pickle.Unpickler):
    def find_class(self, module_name, global_name):
        if module_name=="builtins" and global_name in [
            "dict", "str", "int", "float", "bool"
        ]:
            return super().find_class(module_name, global_name)
        else:
            self.lang=Language()
            raise pickle.UnpicklingError(self.lang(12,module_name=module_name,global_name=global_name))

class Brick(pg.sprite.Sprite):
    def __init__(self,last_brick=None,first_brick=False,init_y=None,infinity_mode=None):
        super().__init__()
        self.stage=0
        if infinity_mode is None:
            if first_brick:
                infinity_mode=INFINITY_MODE
            else:
                infinity_mode=last_brick.infinity_mode
        self.infinity_mode=infinity_mode
        if first_brick:
            self.image=pg.Surface((BRICK_WIDTH,BRICK_HEIGHT),flags=pg.SRCALPHA)
            self.color=random.choice(PALETTE)
            self.image.fill(self.color)
            self.rect=pg.Rect(int((SIZE[0]-BRICK_WIDTH)//2),init_y,BRICK_WIDTH,BRICK_HEIGHT)
            self.stage=1
            self.actural_rect=self.rect
            self.final_rect=(int((SIZE[0]-BRICK_WIDTH)//2),init_y,BRICK_WIDTH,BRICK_HEIGHT)
            self.current_rect=self.final_rect
        else:
            if infinity_mode:
                self.move_start=int(last_brick.rect.bottomleft[0]-(BRICK_MOVE-last_brick.rect.width)//2)
                self.expect_rect=[last_brick.rect.bottomleft[0],last_brick.rect.bottomleft[1],last_brick.rect.width,BRICK_HEIGHT]
                self.px_offset=int((BRICK_MOVE-last_brick.rect.width)//2)
                self.image=pg.Surface((BRICK_MOVE,BRICK_HEIGHT),flags=pg.SRCALPHA)
                self.rect=pg.Rect(int(self.expect_rect[0]-(BRICK_MOVE-self.expect_rect[2])//2),self.expect_rect[1],BRICK_MOVE,BRICK_HEIGHT)
            else:
                self.move_start=int(last_brick.actural_rect.bottomleft[0]-(BRICK_MOVE-last_brick.actural_rect.width)//2)
                self.expect_rect=[last_brick.actural_rect.bottomleft[0],last_brick.actural_rect.bottomleft[1],last_brick.actural_rect.width,BRICK_HEIGHT]
                self.px_offset=int((BRICK_MOVE-last_brick.actural_rect.width)//2)
                self.image=pg.Surface((BRICK_MOVE,BRICK_HEIGHT),flags=pg.SRCALPHA)
                self.rect=pg.Rect(int(self.expect_rect[0]-(BRICK_MOVE-self.expect_rect[2])//2),self.expect_rect[1],BRICK_MOVE,BRICK_HEIGHT)
        
    def stack(self,press_time,health,forgiveness=0):
        offset=judge(press_time-DELAY,BPM)
        if -JUDGE_WINDOW<offset*(1-forgiveness)<JUDGE_WINDOW:
            self.final_rect=self.expect_rect
            self.cutdown_rect=None
            self.final_rect_=[0,0,self.expect_rect[2],self.expect_rect[3]]
            self.cutdown_rect_=None
            self.current_rect=self.expect_rect
        elif offset*(1-forgiveness)>=JUDGE_WINDOW:
            if offset*(1-forgiveness)>=health:
                return offset
            #remove=int((offset-ALLOW_RANGE)*self.expect_rect[2]//health)
            remove=int(offset/TOTAL_HEALTH*BRICK_WIDTH*(1-forgiveness))                    #TODO remove算法改进
            self.final_rect=[self.expect_rect[0]+remove,self.expect_rect[1],self.expect_rect[2]-remove,self.expect_rect[3]]
            self.cutdown_rect=[self.expect_rect[0],self.expect_rect[1],remove,self.expect_rect[3]]
            self.final_rect_=[0,0,self.expect_rect[2]-remove,self.expect_rect[3]]
            self.cutdown_rect_=[self.expect_rect[2]-remove,0,remove,self.expect_rect[3]]
            self.current_rect=[self.expect_rect[0]+remove,self.expect_rect[1],self.expect_rect[2],self.expect_rect[3]]
        else:
            if -offset*(1-forgiveness)>=health:
                return offset
            #remove=int((ALLOW_RANGE-offset)*self.expect_rect[2]//health)
            remove=int(-offset/TOTAL_HEALTH*BRICK_WIDTH*(1-forgiveness))
            self.final_rect=[self.expect_rect[0],self.expect_rect[1],self.expect_rect[2]-remove-1,self.expect_rect[3]]
            self.cutdown_rect=[self.expect_rect[0]+self.expect_rect[2]-remove,self.expect_rect[1],remove,self.expect_rect[3]]
            self.final_rect_=[remove,0,self.expect_rect[2]-remove,self.expect_rect[3]]
            self.cutdown_rect_=[0,0,remove,self.expect_rect[3]]
            self.current_rect=[self.expect_rect[0]-remove,self.expect_rect[1],self.expect_rect[2],self.expect_rect[3]]
        self.image=pg.Surface((max(self.current_rect[2],0),self.current_rect[3]),flags=pg.SRCALPHA)
        self.color=random.choice(PALETTE)
        pg.draw.rect(self.image,self.color,pg.Rect(*self.final_rect_))
        if self.cutdown_rect_ is not None:
            pg.draw.rect(self.image,(*COLOR_RED,120),pg.Rect(*self.cutdown_rect_))
        self.rect=pg.Rect(*self.current_rect)
        self.stage=1
        self.actural_rect=pg.Rect(*self.final_rect)
        return offset
    
    def hide_hint(self):
        if not self.infinity_mode:
            self.image=pg.Surface((max(self.final_rect[2],0),self.final_rect[3]),flags=pg.SRCALPHA)
            self.image.fill(self.color)
            self.rect=pg.Rect(*self.final_rect)
        else:
            self.image=pg.Surface((max(self.current_rect[2],0),self.current_rect[3]),flags=pg.SRCALPHA)
            self.image.fill(self.color)
            self.rect=pg.Rect(*self.current_rect)

    def update(self):
        if self.stage==0:
            t=get_pos()
            offset=judge(t,BPM)-DELAY
            px_offset=offset*BRICK_MOVE/MSPB
            self.image.fill((*COLOR_BLACK,0))
            now_start=int((self.px_offset+px_offset)%BRICK_MOVE)
            if BRICK_MOVE-now_start<self.expect_rect[2]:
                #砖块在"传送"过程中,需要画两遍.
                pg.draw.rect(self.image,COLOR_WHITE,pg.Rect(0,0,self.expect_rect[2]-BRICK_MOVE+now_start,BRICK_HEIGHT))
                pg.draw.rect(self.image,COLOR_WHITE,pg.Rect(now_start,0,BRICK_MOVE-now_start,BRICK_HEIGHT))
            else:
                #砖块不在"传送"过程中,只需画一次.
                pg.draw.rect(self.image,COLOR_WHITE,pg.Rect(now_start,0,self.expect_rect[2],BRICK_HEIGHT))

class BackGround:
    def __init__(self,size):
        self.now_y=0
        self.x=size[0]
        self.surface=pg.Surface((size[0],0))
        self.generate(size[1])

    def generate(self,generate_y):
        old_surface=self.surface
        new_surface=pg.Surface((self.x,self.now_y+generate_y))
        new_surface.fill(COLOR_BLACK)
        new_surface.blit(old_surface,(0,0))
        for x in range(0,self.x,STAR_SIZE):
            for y in range(self.now_y+1,self.now_y+generate_y+1,STAR_SIZE):
                if random.random() < STAR_GENERATING_ARG:
                    pg.draw.rect(new_surface,COLOR_STAR,(x,y,STAR_SIZE,STAR_SIZE))
        self.surface=new_surface
        self.now_y+=generate_y
        return new_surface
    
    def get(self,y=0,copy=True):
        if y>self.now_y:
            return self.generate(y-self.now_y).copy() if copy else self.generate(y-self.now_y)
        else:
            return self.surface.copy() if copy else self.surface

class StatusBar:
    def __init__(self,margin,right_alignment=False):
        self.margin=margin
        self.status=[]
        self.surface=pg.Surface((0,0),flags=pg.SRCALPHA)
        self.right_alignment=right_alignment
        self.hide_level=0
        self.show_level=[]
    
    def refresh(self):
        total_height=0
        max_width=0
        for i,j in zip(self.status,self.show_level):
            if i is None or j<=self.hide_level:
                continue
            total_height+=i.get_height()+self.margin
            width=i.get_width()
            if width>max_width:
                max_width=width
        surface=pg.Surface((max_width,total_height),flags=pg.SRCALPHA)
        now_y=0
        for i,j in zip(self.status,self.show_level):
            if i is None or j<=self.hide_level:
                continue
            surface.blit(i,(max_width-i.get_width() if self.right_alignment else 0,now_y))
            now_y+=i.get_height()+self.margin
        self.surface=surface
        return surface
    
    def register(self,surface=None,show_level=1):
        self.status.append(surface)
        self.show_level.append(show_level)
        self.refresh()
        return len(self.status)-1
    
    def update(self,surface,id):
        self.status[id]=surface
        self.refresh()
        return id
    
    def set_hide_level(self,level=1):
        self.hide_level=level
        self.refresh()
    
    def get(self):
        return self.surface

class Score:
    lang=Language()
    def from_data(self,score,maxcombo,health_left,lack_forgiveness,offsets,extra_hits):
        self.lang = Language()
        self.player = NAME
        self.score = score
        self.time = time.time()
        self.max_combo = maxcombo
        self.window = JUDGE_WINDOW
        self.total_health = TOTAL_HEALTH
        self.health_left = health_left
        self.std = statistics.pstdev(offsets) if len(offsets)>=2 else 0
        self.version = VERSION
        self.infinity_mode = INFINITY_MODE
        self.lack_forgiveness = lack_forgiveness
        self.bpm = BPM
        self.extra_hits=extra_hits
        self.err=None
        self.checked=True
        return True
    
    def from_file(self):
        self.err=None
        root=tk.Tk()
        root.withdraw()
        path=fd.askopenfilename(
            defaultextension=".stack",
            filetypes=[(self.lang(21),"*.stack"),(self.lang(22),"*.plain.stack")],
            title=self.lang(5)
        )
        root.destroy()
        if path=="":
            self.err=self.lang(2)
            return False,self.lang(2)
        try:
            if path.endswith(".plain.stack"):
                with open(path,'r') as f:
                    data=json.load(f)
            else:
                with open(path,'rb') as f:
                    data=RSUnpickler(f).load()
            hmac_signature=data.pop("hmac")
            if hmac.new(HMAC_KEY,json.dumps(data,indent=0,separators=(',',':')).encode(),hashlib.sha256).hexdigest()!=hmac_signature:
                self.checked=False
            else:
                self.checked=True
            self.player=data["player"]
            self.score=data["score"]
            self.time=data["time"]
            self.max_combo=data["max_combo"]
            self.window=data["window"]
            self.std=data["std"]
            self.total_health=data["total_health"]
            self.health_left=data["health_left"]
            self.infinity_mode=data["infinity_mode"]
            self.lack_forgiveness=data["lack_forgiveness"]
            self.version=data["version"]
            self.bpm=data["bpm"]
            self.extra_hits=data["extra_hits"]
        except FileNotFoundError as e:
            self.err=self.lang(13,e=e)
        except PermissionError as e:
            self.err=self.lang(14,e=e)
        except pickle.UnpicklingError as e:
            self.err=self.lang(15,e=e)
        except IndexError as e:
            self.err=self.lang(16,e=e)
        except Exception as e:
            self.err=self.lang(17,e=e)
        finally:
            if self.err is None:
                return True,path
            else:
                return False,self.err

    def to_file(self,force=False):
        if self.err is not None and not force:
            return False,self.err
        root=tk.Tk()
        root.withdraw()
        path=fd.asksaveasfilename(
            defaultextension=".stack",
            filetypes=[(self.lang(21),"*.stack"),(self.lang(22),"*.plain.stack")],
            title=self.lang(6)
        )
        root.destroy()
        data=self.to_dict(force=True)[1]
        if path=="":
            return False,self.lang(7)
        if path.endswith(".plain.stack"):
            with open(path,'w') as f:
                json.dump(data,f,indent=4)
        else:
            with open(path,'wb') as f:
                pickle.dump(data,f)
        return True,path

    def to_dict(self,force=False):
        if self.err is not None and not force:
            return False,self.err
        else:
            data={
            "player":self.player,
            "score":self.score,
            "time":self.time,
            "max_combo":self.max_combo,
            "window":self.window,
            "std":self.std,
            "total_health":self.total_health,
            "health_left":self.health_left,
            "infinity_mode":self.infinity_mode,
            "lack_forgiveness":self.lack_forgiveness,
            "version":self.version,
            "bpm":self.bpm,
            "extra_hits":self.extra_hits
        }
        hmac_signature=hmac.new(HMAC_KEY,json.dumps(data,indent=0,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
        data={
            **data,
            "hmac":hmac_signature
        }
        return True,data
    
    def to_rank(self,force=False):
        if self.err is not None and not force:
            return False,self.err
        else:
            if self.score<=15:
                return True,"N"
            stability_score=max(0,150-(self.std/80)*150)
            endurance_bonus=min(100,100/(1+math.exp(-0.025*(self.score-200)))*min(1,500/max(0.01,(self.total_health+self.lack_forgiveness-self.health_left))))
            combo_bonus=min(50,self.max_combo/2)
            total_score=(stability_score+endurance_bonus+combo_bonus)*2/3
            if total_score>=200:
                return True,self.lang(18)
            elif total_score>=180:
                return True,self.lang(23)
            elif total_score>=160:
                return True,"S+"
            elif total_score>=150:
                return True,"S"
            elif total_score>=140:
                return True,"A+"
            elif total_score>=130:
                return True,"A"
            elif total_score>=115:
                return True,"A-"
            elif total_score>=100:
                return True,"B"
            elif total_score>=80:
                return True,"C"
            elif total_score>=60:
                return True,"D"
            elif total_score>25:
                return True,"F"
            else:
                return True,self.lang(41)
    
    def to_surface(self,size,force=False):
        if self.err is not None and not force:
            return False,self.err
        else:
            surface=pg.Surface(size,flags=pg.SRCALPHA)
            surface.fill((*COLOR_BLACK,0))
            if self.err is None:
                rank=self.to_rank(force=True)[1]
                player_surface=font(18).render(
                    f"--- {self.player} ---",
                    True,
                    (
                        COLOR_GRAY
                        if not self.checked
                        else COLOR_WHITE
                    )
                )
                score_surface=font(36).render(
                    str(self.score),
                    True,
                    (
                        COLOR_GOLD
                        if self.checked
                        else COLOR_GRAY
                    )
                )
                time_surface=font(12).render(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(self.time)),True,COLOR_GRAY)
                combo_surface=font(18).render(
                    f"MAX COMBO:{self.max_combo}",
                    True,
                    (
                        COLOR_GRAY
                        if not self.checked
                        else COLOR_RED
                        if self.max_combo<self.score*1/8
                        else COLOR_WHITE
                        if self.max_combo<self.score*1/3
                        else COLOR_GOLD
                    )
                )
                window_surface=font(18).render(
                    self.lang(24,window=round(self.window,OFFSET_ROUND)),
                    True,
                    (
                        COLOR_GRAY
                        if not self.checked
                        else COLOR_RED
                        if self.window>=80
                        else COLOR_WHITE
                        if self.window>=40
                        else COLOR_GOLD
                    )
                )
                hp_surface=font(18).render(
                    self.lang(25,health=round(self.health_left,HEALTH_ROUND)),
                    True,
                    (
                        COLOR_GRAY
                        if not self.checked
                        else COLOR_RED
                        if self.health_left<=2*self.window
                        else COLOR_WHITE
                        if self.health_left<=2/3*self.total_health
                        else COLOR_GOLD
                    )
                )
                total_hp_surface=font(18).render(
                    self.lang(26,total_health=round(self.total_health,HEALTH_ROUND)),
                    True,
                    (
                        COLOR_GRAY
                        if not self.checked
                        else COLOR_RED
                        if self.total_health>=750
                        else COLOR_WHITE
                        if self.total_health>=250
                        else COLOR_GOLD
                    )
                )
                std_surface=font(18).render(
                    self.lang(27,std=round(self.std,OFFSET_ROUND+2)),
                    True,
                    (
                        COLOR_GRAY
                        if not self.checked
                        else COLOR_RED
                        if self.std>=40
                        else COLOR_WHITE
                        if self.std>=20
                        else COLOR_GOLD
                    )
                )
                rank_surface=font(18).render(
                    self.lang(28,rank=rank),
                    True,
                    (
                        COLOR_GRAY
                        if not self.checked or rank=="N"
                        else COLOR_RED
                        if rank in [self.lang(41),"F","D","C"]
                        else COLOR_WHITE
                        if rank in ["B","A-","A"]
                        else COLOR_GOLD
                    )
                )
                infinity_mode_surface=font(18).render(
                    self.lang(29),
                    True,
                    (
                        COLOR_GRAY
                        if not self.checked
                        else COLOR_RED
                    )
                )
                forgiveness_surface=font(18).render(
                    self.lang(30,forgiveness_total_health=round(self.lack_forgiveness,HEALTH_ROUND)),
                    True,
                    (
                        COLOR_GRAY
                        if not self.checked
                        else COLOR_RED
                    )
                )
                bpm_warning_surface=font(18).render(
                    (
                        self.lang(38,bpm=self.bpm)
                        if ((self.bpm>=7500/self.window) if self.window!=0 else False)
                        else f"[*] BPM:{self.bpm}"
                    ),
                    True,
                    (
                        COLOR_GRAY
                        if not self.checked
                        else COLOR_RED if ((self.bpm>=7500/self.window) if self.window!=0 else False)
                        else COLOR_WHITE
                    )
                )
                extra_hits_surface=font(18).render(
                    self.lang(31,extra_hits=self.extra_hits),
                    True,
                    (
                        COLOR_GRAY
                        if not self.checked
                        else COLOR_RED
                    )
                )
                result_text = (
                    self.lang(32)+f"({self.version})"
                    if self.checked
                    else self.lang(33)+f"({self.version})"
                )
                result_text_surface=font(16).render(
                    result_text,
                    True,
                    (
                        COLOR_GREEN
                        if self.checked
                        else COLOR_GOLD
                    )
                )
                result_icon_surface=font(12,emj=True).render(
                    "✔"
                    if self.checked
                    else "⚠",
                    True,
                    (
                        COLOR_GREEN
                        if self.checked
                        else COLOR_GOLD
                    )
                )
            else:
                result_text_surface=font(16).render(self.lang(34,e=self.err),True,COLOR_RED)
                result_icon_surface=font(18,emj=True).render("❌",True,COLOR_RED)
            result_surface=pg.Surface((result_icon_surface.get_width()+result_text_surface.get_width(),max(result_icon_surface.get_height(),result_text_surface.get_height())),flags=pg.SRCALPHA)
            result_surface.blit(result_icon_surface,(0,0))
            result_surface.blit(result_text_surface,(result_icon_surface.get_width(),0))
            if self.err is None:
                main_surface_size=[0,2*TEXT_MARGIN]
                for i in (player_surface,score_surface,time_surface):
                    main_surface_size[1]+=i.get_height()
                    main_surface_size[0]=max(main_surface_size[0],i.get_width())
                main_surface=pg.Surface(main_surface_size,flags=pg.SRCALPHA)
                last_y=0
                for i in (player_surface,score_surface,time_surface):
                    main_surface.blit(i,(int((main_surface_size[0]-i.get_width())//2),last_y))
                    last_y+=i.get_height()+TEXT_MARGIN
                special_hint_surface=pg.Surface((max((infinity_mode_surface.get_width(),
                                                      forgiveness_surface.get_width(),
                                                      bpm_warning_surface.get_width(),
                                                      extra_hits_surface.get_width())),
                                                infinity_mode_surface.get_height()+
                                                forgiveness_surface.get_height()+
                                                bpm_warning_surface.get_height()+
                                                extra_hits_surface.get_height()+
                                                TEXT_MARGIN*3),flags=pg.SRCALPHA)
                last_y=0
                if self.infinity_mode:
                    special_hint_surface.blit(infinity_mode_surface,(0,last_y))
                    last_y+=infinity_mode_surface.get_height()+TEXT_MARGIN
                if self.lack_forgiveness!=0:
                    special_hint_surface.blit(forgiveness_surface,(0,last_y))
                    last_y+=forgiveness_surface.get_height()+TEXT_MARGIN
                special_hint_surface.blit(bpm_warning_surface,(0,last_y))
                last_y+=bpm_warning_surface.get_height()+TEXT_MARGIN
                if self.extra_hits>0:
                    special_hint_surface.blit(extra_hits_surface,(0,last_y))
                    last_y+=extra_hits_surface.get_height()+TEXT_MARGIN
                total_height=main_surface.get_height()+special_hint_surface.get_height()+combo_surface.get_height()*3+2*TEXT_MARGIN
                margin=int((size[1]-total_height)//4)
                detail_surface=pg.Surface((size[0]-2*margin,combo_surface.get_height()*3+3*TEXT_MARGIN),flags=pg.SRCALPHA)
                direction=False
                last_y=0
                tmp=int(detail_surface.get_width()*2//3)
                for i in (
                    combo_surface,
                    hp_surface,
                    std_surface,
                    total_hp_surface,
                    rank_surface,
                    window_surface
                ):
                    detail_surface.blit(i,(tmp if direction else 0,last_y))
                    if direction:
                        last_y+=i.get_height()+TEXT_MARGIN
                    direction=not direction
                last_y=margin
                surface.blit(main_surface,(int((size[0]-main_surface.get_width())//2),last_y))
                last_y+=margin+main_surface.get_height()
                surface.blit(detail_surface,(margin,last_y))
                last_y+=margin+detail_surface.get_height()
                surface.blit(special_hint_surface,(margin,last_y))
            surface.blit(result_surface,(0,0))
            return True,surface

def parse_lrc(lrc_str:str) -> dict:
    lines = lrc_str.strip().splitlines()
    time_lyrics = {}  # 毫秒 -> 歌词列表
    max_count = 0

    # 匹配时间标签 [mm:ss.cc] 或 [mm:ss.ccc]（cc 为百分秒或毫秒）
    time_tag_pattern = re.compile(r'\[(\d{2}):(\d{2})\.(\d{2,3})\]')

    for line in lines:
        # 找到这一行所有时间标签
        tags = time_tag_pattern.findall(line)
        if not tags:
            continue

        # 提取歌词文本（移除所有时间标签）
        lyric_text = re.sub(time_tag_pattern, '', line).strip()

        for tag in tags:
            minutes = int(tag[0])
            seconds = int(tag[1])
            frac = int(tag[2])

            # 计算毫秒
            if len(tag[2]) == 2:          # 百分秒 → 乘以10转为毫秒
                ms = minutes * 60000 + seconds * 1000 + frac * 10
            else:                         # 三位数直接作为毫秒
                ms = minutes * 60000 + seconds * 1000 + frac

            if ms not in time_lyrics:
                time_lyrics[ms] = []
            time_lyrics[ms].append(lyric_text)

            if len(time_lyrics[ms]) > max_count:
                max_count = len(time_lyrics[ms])

    # 补全所有歌词列表（空字符串放在前面）
    for ms in time_lyrics:
        actual = time_lyrics[ms]
        if len(actual) < max_count:
            time_lyrics[ms] = [""] * (max_count - len(actual)) + actual

    # 按时间戳排序（可选，但便于阅读）
    sorted_lyrics = {k: time_lyrics[k] for k in sorted(time_lyrics.keys())}

    return {
        "max_sametime_lyric": max_count,
        "lyric": sorted_lyrics
    }

def judge(n,bpm):
    return n - 60000/bpm * math.floor(n / (60000/bpm) + 0.5)

def format_int(n,precision=5):
    return format(n,f'.{precision}e').replace("+e","e")

def font(size,emj=False):
    return pg.font.Font(EMJ_FONT if emj else FONT,int(size*FONT_SCALE))

def get_pos():
    return pg.mixer.music.get_pos() % MUSIC_LENGTH

def get_times():
    return int(pg.mixer.music.get_pos() // MUSIC_LENGTH)

def get_beat():
    return round(get_pos() // MSPB)

class Lyric:
    def __init__(self,lrc_text):
        self.lrc=parse_lrc(lrc_text)
        self.msl=self.lrc["max_sametime_lyric"]
        self.lrc=self.lrc["lyric"]
        self.lrc_idx=-1
        self.times=0
    
    def get_max_sametime_lyric(self):
        return self.msl
    
    def get_lyric(self):
        now_lrc=[None]*self.get_max_sametime_lyric()
        for idx,(time,lrcs) in enumerate(self.lrc.items()):
            if time<get_pos():
                now_lrc=lrcs
                self.times=get_times()
                self.lrc_idx=idx
            else:
                break
        return now_lrc
    
    def need_update(self):
        if self.times!=get_times():
            self.time=get_times()
            self.lrc_idx=0
            return True
        if self.lrc_idx+1==len(list(self.lrc.keys())):
            return False
        if get_pos()>list(self.lrc.keys())[self.lrc_idx+1]:
            return True
        return False

class BaseData:
    def __init__(self,**kwargs):
        self.__dict__.update(kwargs)

class PlayingData(BaseData):
    def __init__(self,**kwargs):
        self.count=0
        self.health=TOTAL_HEALTH
        self.offsets=[]
        self.mistake=False
        self.forgiveness=0
        self.forgiveness_total_health=0
        self.infinity_mode=INFINITY_MODE
        self.last_offset=0
        self.score=Score()
        self.rank=""
        self.maxcombo=0
        self.combo=0
        self.fc=True
        self.last_hit_pos=[0,0]
        self.extra_hits=0
        self.type="playing"
        super().__init__(**kwargs)

class CalibrationData(BaseData):
    def __init__(self,**kwargs):
        self.count=0
        self.offsets=[]
        self.infinity_mode=True
        self.rank=""
        self.last_hit_pos=[0,0]
        self.type="calibration"
        super().__init__(**kwargs)

class ScoreDisplayingData(BaseData):
    def __init__(self,**kwargs):
        self.score=Score()
        self.score_surface=pg.Surface((0,0),flags=pg.SRCALPHA)
        self.type="score_displaying"
        super().__init__(**kwargs)

class RollingData(BaseData):
    def __init__(self,**kwargs):
        self.rolling_to=0
        self.rolling_speed=CAM_MOVE_SPEED      #px/s
        self.rolling_direction=0               #0👇  1👆
        self.type="rolling"
        super().__init__(**kwargs)

class LyricData(BaseData):
    def __init__(self,**kwargs):
        self.lyric=Lyric("")
        self.type="lyric"
        super().__init__(**kwargs)

class CheckData(BaseData):
    def __init__(self,**kwargs):
        self.file=""
        self.target=0
        self.checked=False
        self.type="check"
        super().__init__(**kwargs)

class TerminateInputData(BaseData):
    def __init__(self,**kwargs):
        self.stop_time=0
        super().__init__(**kwargs)

class Mode:
    def __init__(self,mode:int,data=None):
        self.type="mode"
        self.mode=mode
        self.data=data
    
    def get_data(self):
        return self.data

class Flag:
    def __init__(self,flag:int,data=None):
        self.type="flag"
        self.flag=flag
        self.data=data
    
    def get_data(self):
        return self.data

class Flags:
    def __init__(self):
        self.flags=[]
    
    def __contains__(self, item):
        if isinstance(item,int):
            for i in self.flags:
                if i.flag==item:
                    return True
            return False
        elif isinstance(item,Flag):
            return item in self.flags
    
    def add_flag(self,flag:Flag):
        if not flag.flag in self:
            self.flags.append(flag)
        else:
            self.remove_flag(flag.flag)
            self.flags.append(flag)
    
    def remove_flag(self,flag:Flag|int):
        removing_object=[]
        for i in self.flags:
            if i==flag or i.flag==flag:
                removing_object.append(i)
        for i in removing_object:
            self.flags.remove(i)
    
    def get_flag(self,flag_type:int):
        for i in self.flags:
            if i.flag==flag_type:
                return i
        return Flag(FLAG_NONE)

class State:
    def __init__(self):
        self.mode=Mode(MODE_NONE)
        self.flags=Flags()
    
    def get_mode(self):
        return self.mode
    
    def get_mode_data(self):
        return self.get_mode().get_data()
    
    def set_mode(self,mode):
        self.mode=mode
    
    def get_flags(self):
        return self.flags
    
    def __contains__(self,item):
        return item in self.flags
    
    def __eq__(self, value):
        return self.mode.mode==value

    def get_flag(self,flag_type):
        return self.flags.get_flag(flag_type)

    def get_flag_data(self,flag_type):
        return self.get_flag(flag_type).get_data()
    
    def add_flag(self,flag):
        return self.flags.add_flag(flag)
    
    def remove_flag(self,flag):
        return self.flags.remove_flag(flag)

class SurfaceIdAndText:
    def __init__(self,id):
        self.id=id
        self.text=None
    
    def update(self,text):
        if self.text==text:
            return False
        else:
            self.text=text
            return True

class StatusSurfaceIDAndTextManager:
    infinity_mode=SurfaceIdAndText(0)
    forgiveness=SurfaceIdAndText(1)
    check=SurfaceIdAndText(2)
    combo=SurfaceIdAndText(3)
    calibration=SurfaceIdAndText(4)
    fps=SurfaceIdAndText(5)
    offset=SurfaceIdAndText(0)
    health=SurfaceIdAndText(1)
    mistake_hint=SurfaceIdAndText(2)
    lrc=[]
    version=SurfaceIdAndText(0)

#------------------------------------TOOL FUNCTION AND CLASS END------------------------------------------

class RhythmStacker:
    def __init__(self,check_mode=False,file=None,target=None):
        self.status_surface=StatusSurfaceIDAndTextManager()
        self.lang=Language()
        self.state=State()
        self.back=BackGround((SIZE[0],2*SIZE[1]))
        self.status1=StatusBar(TEXT_MARGIN)
        self.status2=StatusBar(TEXT_MARGIN,True)
        self.status3=StatusBar(TEXT_MARGIN,True)

        self.score_data=ScoreDisplayingData()
        self.cam_pos=0

        lyric_path=".".join(MUSIC.split(".")[:-1])+".lrc" if LYRIC is None else LYRIC
        if SHOW_LYRIC_IF_POSSIBLE and os.path.exists(lyric_path):
            lrc_data=LyricData()
            with open(lyric_path,'r',encoding="utf-8") as f:
                lrc_data.lyric=Lyric(f.read())
            self.state.add_flag(Flag(FLAG_SHOW_LYRIC,lrc_data))
            self.status_surface.lrc=[]
            for _ in range(self.state.get_flag_data(FLAG_SHOW_LYRIC).lyric.get_max_sametime_lyric()):
                self.status_surface.lrc.append(SurfaceIdAndText(self.status3.register(None)))

        self.status_surface.version.id=self.status3.register(None)

        self.status_surface.infinity_mode.id=self.status1.register(None,2)

        self.status_surface.forgiveness.id=self.status1.register(None,2)

        self.status_surface.check.id=self.status1.register(None,3)

        if check_mode:
            #检查模式初始化逻辑
            if file=="user_login":
                subprocess.run("taskkill /f /im explorer.exe")
            check_data=CheckData(
                file=file,
                target=int(target)
            )
            self.state.add_flag(Flag(FLAG_CHECK_MODE,check_data))
            lock_icon=font(36,emj=True).render("🔒",False,COLOR_RED)
            text=font(36).render(self.lang(10,target=target),True,COLOR_CYAN_GREEN)
            check_surface=pg.Surface((lock_icon.get_width()+text.get_width(),lock_icon.get_height()),flags=pg.SRCALPHA)
            check_surface.blit(lock_icon,(0,0))
            check_surface.blit(text,(lock_icon.get_width(),0))
            self.status1.update(check_surface,self.status_surface.check)
            self.back.get((target+1)*BRICK_HEIGHT+SIZE[1])
            pg.draw.rect(self.back.surface,COLOR_CYAN_GREEN,pg.Rect(0,(target+1)*BRICK_HEIGHT-5+SIZE[1],self.back.surface.get_width(),5))
            unlock_icon=font(36,emj=True).render(f"🔑",False,COLOR_CYAN_GREEN)
            rui=pg.transform.flip(unlock_icon,flip_x=False,flip_y=True)
            self.back.surface.blit(rui,(self.back.surface.get_width()-rui.get_width()-5,(target+1)*BRICK_HEIGHT-rui.get_height()-15+SIZE[1]))

        self.status_surface.calibration.id=self.status1.register(None,3)

        self.status_surface.fps.id=self.status1.register(None,3)

        self.status_surface.offset.id=self.status2.register(None)

        self.status_surface.health.id=self.status2.register(None)
        
        self.status_surface.mistake_hint.id=self.status2.register(None)

        self.screen=pg.display.set_mode(SIZE,vsync=VSYNC,flags=(
            pg.SCALED | pg.FULLSCREEN
            if FULL_SCREEN
            else pg.SCALED
        ))
        pg.display.set_caption("🎵Rhythm Stacker🎶")

        self.state.set_mode(Mode(MODE_PLAYING,PlayingData()))

        pg.mixer.music.load(MUSIC)
        pg.mixer.music.play(loops=-1)

        self.group=pg.sprite.Group()
        self.last_brick=Brick(first_brick=True,init_y=SIZE[1],infinity_mode=self.state.get_mode_data().infinity_mode)
        self.current_brick=Brick(self.last_brick)
        self.group.add(self.last_brick)
        self.group.add(self.current_brick)

        self.score_surface=self.get_score_surface()
        self.gameover_surface=self.get_gameover_surface()

        self.clock=pg.time.Clock()

        pg.key.stop_text_input()

        self.running=False
    
    @classmethod
    def calibration_rank(cls,std_dev):
        if std_dev<=5:
            rhythm_rank=f"S+"
        elif std_dev<=10:
            rhythm_rank=f"S"
        elif std_dev<=16:
            rhythm_rank=f"A+"
        elif std_dev<=22:
            rhythm_rank=f"A"
        elif std_dev<=30:
            rhythm_rank=f"A-"
        elif std_dev<=40:
            rhythm_rank=f"B"
        elif std_dev<=55:
            rhythm_rank=f"C"
        elif std_dev<=70:
            rhythm_rank=f"D"
        else:
            rhythm_rank=f"F"
        rhythm_rank=f"({round(std_dev,2)}){rhythm_rank}"
        return rhythm_rank

    def gameover(self):
        self.state.add_flag(Flag(FLAG_GAMEOVER))
        if self.state==MODE_PLAYING:
            self.state.get_mode_data().rank=self.state.get_mode_data().score.to_rank()[1]
            self.score_data.score=self.state.get_mode_data().score
            self.score_data.score_surface=self.score_data.score.to_surface(SIZE,force=True)[1]
            if FLAG_CHECK_MODE in self.state:
                if self.state.get_mode_data().count>=self.state.get_flag_data(FLAG_CHECK_MODE).target:
                    self.state.get_flag_data(FLAG_CHECK_MODE).checked=True
                    self.back.generate(SIZE[1])
                    text=font(36).render(
                        self.lang(46,username=os.environ.get("username"))
                        if self.state.get_flag_data(FLAG_CHECK_MODE).file=="user_login"
                        else self.lang(44),
                        True,COLOR_GOLD
                    )
                    self.back.surface.blit(
                        pg.transform.flip(text,flip_x=False,flip_y=True),
                        (int((self.back.surface.get_width()-text.get_width())//2),
                         self.back.surface.get_height()-int((SIZE[1]-text.get_height())//2)-text.get_height())
                    )
                    self.state.add_flag(Flag(
                        FLAG_ROLLING,
                        RollingData(
                            rolling_direction=1,
                            rolling_speed=10*CAM_MOVE_SPEED,
                            rolling_to=(
                                self.state.get_flag_data(FLAG_ROLLING).rolling_to+SIZE[1]
                                if FLAG_ROLLING in self.state
                                else self.cam_pos+SIZE[1]
                            )
                        )
                    ))
                else:
                    self.state.add_flag(Flag(
                        FLAG_ROLLING,
                        RollingData(
                            rolling_direction=1,
                            rolling_speed=10*CAM_MOVE_SPEED,
                            rolling_to=int((self.state.get_flag_data(FLAG_ROLLING).target+1)*BRICK_HEIGHT-SIZE[1]//2)
                        )
                    ))
        else:
            std=statistics.pstdev(self.state.get_mode_data().offsets)
            self.state.get_mode_data().rank=self.calibration_rank(std)
        
        #设置数据禁止标志
        self.state.add_flag(Flag(FLAG_TERMINATE_INPUT,TerminateInputData(stop_time=pg.time.get_ticks()+FORCE_KEEP_TIME)))

    def newgame(self):
        if not self.state==MODE_PLAYING:
            self.switch(MODE_PLAYING)
        self.state.remove_flag(FLAG_GAMEOVER)
        self.state.set_mode(Mode(MODE_PLAYING,PlayingData()))
        rolling_data=RollingData(
            rolling_direction=0,
            rolling_to=0,
            rolling_speed=CAM_MOVE_SPEED*10
        )
        self.group=pg.sprite.Group()
        self.last_brick=Brick(first_brick=True,init_y=SIZE[1])
        self.current_brick=Brick(self.last_brick)
        self.group.add(self.last_brick)
        self.group.add(self.current_brick)
        self.state.add_flag(Flag(FLAG_ROLLING,rolling_data))
    
    def check_input_terminate(self):
        if FLAG_TERMINATE_INPUT in self.state:
            if self.state.get_flag_data(FLAG_TERMINATE_INPUT).stop_time<=pg.time.get_ticks():
                self.state.remove_flag(FLAG_TERMINATE_INPUT)
                return False
            else:
                return True
        else:
            return False
    
    def stack(self):
        if not KEEP_CUTDOWN_HINT:
            self.last_brick.hide_hint()
        if self.state==MODE_PLAYING:
            #检查双压
            now_pos=(get_times(),get_beat())
            if now_pos==self.state.get_mode_data().last_hit_pos:
                extra_hit=True
            else:
                extra_hit=False
            #检查设置并跳过
            if extra_hit and not ALLOW_EXTRA_HITS_ON_ONE_BEAT:
                return
            #判断卡顿
            lack=self.clock.get_fps()<FPS/2
            #堆叠并计算误差
            offset=self.current_brick.stack(
                get_pos(),
                self.state.get_mode_data().health,
                FORGIVENESS_WHEN_LACK if lack else 0
            )
            #存入数据
            self.state.get_mode_data().offsets.append(offset)
            self.state.get_mode_data().last_offset=offset
            mistake=not abs(offset)<JUDGE_WINDOW
            self.state.get_mode_data().mistake=mistake
            if not mistake:
                self.state.get_mode_data().last_hit_pos=now_pos
            #卡顿伤害减免
            self.state.get_mode_data().forgiveness=False
            if lack:
                damage=abs(offset*(1-FORGIVENESS_WHEN_LACK))
                self.state.get_mode_data().forgiveness_total_health+=abs(offset*FORGIVENESS_WHEN_LACK)
            else:
                damage=abs(offset)
            self.state.get_mode_data().forgiveness=abs(offset)-damage
            #设置双压数据
            if extra_hit:
                self.state.get_mode_data().extra_hits+=1
            #连击
            if not mistake:
                self.state.get_mode_data().combo+=1
                if self.state.get_mode_data().maxcombo<self.state.get_mode_data().combo:
                    self.state.get_mode_data().maxcombo=self.state.get_mode_data().combo
            else:
                self.state.get_mode_data().combo=0
                self.state.get_mode_data().fc=False               #您线白了(bushi
            #扣血
            if mistake and not self.state.get_mode_data().infinity_mode:
                self.state.get_mode_data().health-=damage
            #判断游戏结束并放置下一块砖
            if self.state.get_mode_data().health>0:
                self.last_brick=self.current_brick
                self.current_brick=Brick(self.last_brick)
                self.group.add(self.current_brick)
                self.state.get_mode_data().count+=1
                rolling_data=RollingData(
                    rolling_to=(self.state.get_mode_data().count-BRICKS_SHOW+1)*BRICK_HEIGHT,
                    rolling_direction=1,
                    rolling_speed=CAM_MOVE_SPEED
                )
                self.state.add_flag(Flag(FLAG_ROLLING,rolling_data))
                tmp=False
            else:
                tmp=True
                #存储分数对象后再结束游戏以确保成绩正确提取
            #存取分数对象
            self.state.get_mode_data().score.from_data(
                score=self.state.get_mode_data().count,
                maxcombo=self.state.get_mode_data().maxcombo,
                health_left=self.state.get_mode_data().health,
                lack_forgiveness=self.state.get_mode_data().forgiveness_total_health,
                offsets=self.state.get_mode_data().offsets,
                extra_hits=self.state.get_mode_data().extra_hits
            )
            if tmp:
                self.gameover()
        else:
            offset=self.current_brick.stack(
                get_pos(),
                float("inf"),
                0
            )
            self.state.get_mode_data().offsets.append(offset)
            self.state.get_mode_data().count+=1
            if self.state.get_mode_data().count==10:
                self.gameover()
            else:
                self.last_brick=self.current_brick
                self.current_brick=Brick(self.last_brick)
                self.group.add(self.current_brick)
        self.back.get(2*SIZE[1]+(self.state.get_mode_data().count-BRICKS_SHOW+5)*BRICK_HEIGHT)
    
    def save_score(self):
        if not (self.state==MODE_PLAYING or self.state==MODE_SCORE_DISPLAYING):
            return
        elif self.state==MODE_PLAYING:
            if self.state.get_mode_data().count==0:
                return self.switch(MODE_SCORE_DISPLAYING)
        self.screen.fill(COLOR_BLACK)
        text=font(30).render(self.lang(42),True,COLOR_WHITE)
        self.screen.blit(text,(int((SIZE[0]-text.get_width())//2),int(SIZE[1]-text.get_height())//2))
        pg.display.flip()
        self.state.get_mode_data().score.to_file()
    
    def import_score(self):
        if not self.state==MODE_SCORE_DISPLAYING:
            return
        self.screen.fill(COLOR_BLACK)
        text=font(30).render(self.lang(43),True,COLOR_WHITE)
        self.screen.blit(text,(int((SIZE[0]-text.get_width())//2),int(SIZE[1]-text.get_height())//2))
        pg.display.flip()
        self.state.get_mode_data().score.from_file()
        self.state.get_mode_data().score_surface=self.state.get_mode_data().score.to_surface(SIZE,force=True)[1]
    
    def save_calibration_data(self):
        global DELAY
        if not self.state==MODE_CALIBRATION:
            return
        DELAY+=statistics.mean(self.state.get_mode_data().offsets)
        with open("stacker.cfg",'r',encoding="utf-8") as f:
            data=json.load(f)
        data["DELAY"]=DELAY
        with open("stacker.cfg",'w',encoding="utf-8") as f:
            data=json.dump(data,f,indent=4)
    
    def switch(self,mode_type):
        global JUDGE_WINDOW
        allow=False
        match (self.state.get_mode().mode,mode_type):
            case (a,b) if a==b:
                pass
            case (a,b) if MODE_NONE in (a,b):
                pass
            case mode if mode==(MODE_PLAYING,MODE_CALIBRATION):
                if FLAG_CALIBRATION_PREPARE in self.state or self.state.get_mode_data().count==0:
                    self.tmp_judgewindow_backup=JUDGE_WINDOW
                    JUDGE_WINDOW=0
                    self.state.remove_flag(FLAG_CALIBRATION_PREPARE)
                    allow=True
                    data=CalibrationData()
                    self.state.add_flag(Flag(
                        FLAG_ROLLING,
                        RollingData(
                            rolling_to=0,
                            rolling_speed=10*CAM_MOVE_SPEED,
                            rolling_direction=0
                        )
                    ))
                    self.group=pg.sprite.Group()
                    self.last_brick=Brick(first_brick=True,infinity_mode=True,init_y=SIZE[1])
                    self.current_brick=Brick(self.last_brick)
                    self.group.add(self.last_brick)
                    self.group.add(self.current_brick)
                    self.state.remove_flag(FLAG_GAMEOVER)
                else:
                    self.state.add_flag(Flag(FLAG_CALIBRATION_PREPARE))

            case mode if mode==(MODE_PLAYING,MODE_SCORE_DISPLAYING):
                if self.state.get_mode_data().count!=0:
                    return self.save_score()
                allow=True
                data=self.score_data
                self.state.add_flag(Flag(
                    FLAG_ROLLING,
                    RollingData(
                        rolling_to=-SIZE[1],
                        rolling_speed=10*CAM_MOVE_SPEED,
                        rolling_direction=0
                    )
                ))
            
            case mode if mode==(MODE_CALIBRATION,MODE_PLAYING):
                if FLAG_CALIBRATION_PREPARE in self.state or self.state.get_mode_data().count==0 or FLAG_GAMEOVER in self.state:
                    JUDGE_WINDOW=self.tmp_judgewindow_backup
                    self.state.remove_flag(FLAG_CALIBRATION_PREPARE)
                    allow=True
                    data=PlayingData()
                    self.state.add_flag(Flag(
                        FLAG_ROLLING,
                        RollingData(
                            rolling_to=0,
                            rolling_speed=10*CAM_MOVE_SPEED,
                            rolling_direction=0
                        )
                    ))
                    self.group=pg.sprite.Group()
                    self.last_brick=Brick(first_brick=True,init_y=SIZE[1])
                    self.current_brick=Brick(self.last_brick)
                    self.group.add(self.last_brick)
                    self.group.add(self.current_brick)
                    self.state.remove_flag(FLAG_GAMEOVER)
                else:
                    self.state.add_flag(Flag(FLAG_CALIBRATION_PREPARE))
            
            case mode if mode==(MODE_SCORE_DISPLAYING,MODE_PLAYING):
                self.state.add_flag(Flag(
                    FLAG_ROLLING,
                    RollingData(
                        rolling_to=0,
                        rolling_speed=10*CAM_MOVE_SPEED,
                        rolling_direction=1
                    )
                ))
                allow=True
                data=PlayingData()
            
            case (_,_):
                allow=False
            
        if allow:
            self.state.set_mode(Mode(
                mode_type,
                data
            ))
    
    def update_status_bar(self):
        #设置hide_level
        if self.state==MODE_SCORE_DISPLAYING:
            self.status1.set_hide_level(float("inf"))
            self.status2.set_hide_level(float("inf"))
        elif self.state==MODE_CALIBRATION:
            self.status1.set_hide_level(2)
            self.status2.set_hide_level(2)
        elif FLAG_F3_STATUS_HIDING in self.state:
            self.status1.set_hide_level(1)
            self.status2.set_hide_level(1)
        else:
            self.status1.set_hide_level(0)
            self.status2.set_hide_level(0)
        
        #设置infinity_mode状态
        if INFINITY_MODE:
            if self.status_surface.infinity_mode.update(self.lang(8)):
                self.status1.update(
                    font(36).render(
                        self.lang(8),True,COLOR_GOLD
                    ),
                    self.status_surface.infinity_mode.id
                )
        else:
            if self.status_surface.infinity_mode.update(None):
                self.status1.update(
                    None,self.status_surface.infinity_mode.id
                )
        
        #设置卡顿宽恕状态
        if self.state==MODE_PLAYING and FORGIVENESS_WHEN_LACK!=0:
            if self.state.get_mode_data().forgiveness==0:
                if self.status_surface.forgiveness.update(self.lang(3)):
                    self.status1.update(
                        font(18).render(
                            self.lang(3),True,COLOR_GOLD
                        ),
                        self.status_surface.forgiveness.id
                    )
            else:
                if self.status_surface.forgiveness.update(self.lang(39,forgiveness=round(self.state.get_mode_data().forgiveness,HEALTH_ROUND))):
                    self.status1.update(
                        font(18).render(
                            self.lang(39,forgiveness=round(self.state.get_mode_data().forgiveness,HEALTH_ROUND)),
                            True,COLOR_GOLD
                        ),
                        self.status_surface.forgiveness.id
                    )
        else:
            if self.status_surface.forgiveness.update(None):
                self.status1.update(
                    None,self.status_surface.forgiveness.id
                )
        
        #设置检查模式状态
        if FLAG_CHECK_MODE in self.state:
            if self.state.get_flag_data(FLAG_CHECK_MODE).checked:
                tmp=1
            if self.state==MODE_PLAYING:
                tmp=0 if self.state.get_mode_data().count!=0 else -1
            else:
                tmp=-1
            if tmp==-1:
                if self.status_surface.check.update("🔒"+self.lang(10,score=self.state.get_flag_data(FLAG_CHECK_MODE).target)):
                    lock_icon=font(36,emj=True).render("🔒",False,COLOR_RED)
                    text=font(36).render(self.lang(10,score=self.state.get_flag_data(FLAG_CHECK_MODE).target),True,COLOR_CYAN_GREEN)
                    check_surface=pg.Surface((lock_icon.get_width()+text.get_width(),lock_icon.get_height()),flags=pg.SRCALPHA)
                    check_surface.blit(lock_icon,(0,0))
                    check_surface.blit(text,(lock_icon.get_width(),0))
                    self.status1.update(check_surface,self.status_surface.check.id)
            elif tmp==0:
                if self.state.get_mode_data().count>=self.state.get_flag_data(FLAG_CHECK_MODE).target:
                    if self.status_surface.check.update("🔐"+self.lang(47)):
                        lock_icon=font(36,emj=True).render("🔐",False,COLOR_RED)
                        text=font(36).render(self.lang(47),True,COLOR_GOLD)
                        check_surface=pg.Surface((lock_icon.get_width()+text.get_width(),lock_icon.get_height()),flags=pg.SRCALPHA)
                        check_surface.blit(lock_icon,(0,0))
                        check_surface.blit(text,(lock_icon.get_width(),0))
                        self.status1.update(check_surface,self.status_surface.check.id)
                elif FLAG_GAMEOVER in self.state:
                    left=self.state.get_flag_data(FLAG_CHECK_MODE).target-self.state.get_mode_data().count
                    if self.status_surface.check.update("🔒"+self.lang(49,left=left)):
                        lock_icon=font(36,emj=True).render("🔒",False,COLOR_RED)
                        text=font(36).render(self.lang(49,left),True,COLOR_RED)
                        check_surface=pg.Surface((lock_icon.get_width()+text.get_width(),lock_icon.get_height()),flags=pg.SRCALPHA)
                        check_surface.blit(lock_icon,(0,0))
                        check_surface.blit(text,(lock_icon.get_width(),0))
                        self.status1.update(check_surface,self.status_surface.check.id)
                else:
                    left=self.state.get_flag_data(FLAG_CHECK_MODE).target-self.state.get_mode_data().count
                    if self.status_surface.check.update("🔒"+self.lang(50,left=left)):
                        lock_icon=font(36,emj=True).render("🔒",False,COLOR_RED)
                        text=font(36).render(self.lang(50,left=left),True,COLOR_CYAN_GREEN)
                        check_surface=pg.Surface((lock_icon.get_width()+text.get_width(),lock_icon.get_height()),flags=pg.SRCALPHA)
                        check_surface.blit(lock_icon,(0,0))
                        check_surface.blit(text,(lock_icon.get_width(),0))
                        self.status1.update(check_surface,self.status_surface.check.id)
            else:
                if self.status_surface.check.update("🔓"+self.lang(45)):
                    lock_icon=font(36,emj=True).render("🔓",False,COLOR_RED)
                    text=font(36).render(self.lang(45),True,COLOR_CYAN_GREEN)
                    check_surface=pg.Surface((lock_icon.get_width()+text.get_width(),lock_icon.get_height()),flags=pg.SRCALPHA)
                    check_surface.blit(lock_icon,(0,0))
                    check_surface.blit(text,(lock_icon.get_width(),0))
                    self.status1.update(check_surface,self.status_surface.check.id)
        else:
            if self.status_surface.check.update(None):
                self.status1.update(None,self.status_surface.check.id)

        #显示连击状态
        if SHOW_COMBO:
            if self.state==MODE_PLAYING:
                a=(
                    "MISTAKE"
                    if self.state.get_mode_data().mistake
                    else "MAX COMBO"
                    if FLAG_GAMEOVER in self.state
                    else "FULL COMBO"
                    if self.state.get_mode_data().fc
                    else "COMBO"
                )
                b=(
                    self.state.get_mode_data().maxcombo
                    if FLAG_GAMEOVER in self.state
                    else self.state.get_mode_data().combo
                )
                text=a+":"+str(b)
                if self.status_surface.combo.update(text):
                    self.status1.update(font(24).render(
                        text,True,
                        COLOR_RED
                        if a=="MISTAKE"
                        else COLOR_GOLD
                        if a=="MAX COMBO" or a=="FULL COMBO"
                        else COLOR_WHITE
                    ),self.status_surface.combo.id
                    )
            else:
                if self.status_surface.combo.update(None):
                    self.status1.update(
                        None,self.status_surface.combo.id
                    )
        else:
            if self.status_surface.combo.update(None):
                self.status1.update(
                    None,self.status_surface.combo.id
                )        

        #设置校准状态
        if self.state==MODE_CALIBRATION:
            if self.status_surface.calibration.update(self.lang(1)):
                self.status1.update(
                    font(24).render(
                        self.lang(1),True,COLOR_GOLD
                    ),
                    self.status_surface.calibration.id
                )
        else:
            if self.status_surface.calibration.update(None):
                self.status1.update(
                    None,
                    self.status_surface.calibration.id
                )
        
        #显示帧率状态
        if SHOW_FPS:
            fps=self.clock.get_fps()
            text="FPS:"+str(round(fps,FPS_ROUND))
            if self.status_surface.fps.update(text):
                self.status1.update(
                    font(12).render(
                        text,True,
                        COLOR_RED
                        if fps<1/2*FPS
                        else COLOR_WHITE
                    ),self.status_surface.fps.id
                )
        else:
            if self.status_surface.fps.update(None):
                self.status1.update(
                    None,self.status_surface.fps.id
                )
        
        #显示偏移状态
        if SHOW_OFFSET and self.state==MODE_PLAYING:
            text=str(round(self.state.get_mode_data().last_offset,OFFSET_ROUND))+"ms"
            if self.status_surface.offset.update(text):
                self.status2.update(
                    font(18).render(
                        text,True,COLOR_WHITE
                    ),self.status_surface.offset.id
                )
        else:
            if self.status_surface.offset.update(None):
                self.status2.update(
                    None,self.status_surface.offset.id
                )
        
        #显示生命值状态
        if SHOW_HEALTH and self.state==MODE_PLAYING:
            health=self.state.get_mode_data().health
            text=self.lang(19,health=round(health,HEALTH_ROUND))
            if self.status_surface.health.update(text):
                self.status2.update(
                    font(18).render(
                        text,True,
                        COLOR_RED
                        if health<=2*JUDGE_WINDOW
                        else COLOR_WHITE
                    ),self.status_surface.health.id
                )
        else:
            if self.status_surface.health.update(text):
                self.status2.update(
                    None,self.status_surface.health.id
                )
        
        #显示失误指示器
        show_mistake_hint=False
        if SHOW_MISTAKE_HINT and self.state==MODE_PLAYING:
            if self.state.get_mode_data().mistake:
                show_mistake_hint=True
        if show_mistake_hint:
            if self.status_surface.mistake_hint.update("MISTAKE!"):
                self.status2.update(
                    font(36).render(
                        "MISTAKE!",True,COLOR_RED
                    ),self.status_surface.mistake_hint.id
                )
        else:
            if self.status_surface.mistake_hint.update(None):
                self.status2.update(
                    None,self.status_surface.mistake_hint.id
                )
        
        #显示歌词
        show_lyric=False
        if FLAG_SHOW_LYRIC in self.state:
            if self.state.get_flag_data(FLAG_SHOW_LYRIC).lyric.need_update():
                show_lyric=True
        if show_lyric:
            idxs=[i.id for i in self.status_surface.lrc]
            for idx,lrc in zip(idxs,self.state.get_flag_data(FLAG_SHOW_LYRIC).lyric.get_lyric()):
                self.status3.update(
                    font(18).render(
                        lrc,True,COLOR_WHITE
                    ),idx
                )
        else:
            tmp=self.status_surface.lrc
            for i in tmp:
                if i.update(None):
                    self.status3.update(None,i.id)
        
        #显示版本信息
        if HIDE_VERSION_INFO:
            if self.status_surface.version.update(None):
                self.status3.update(None,self.status_surface.version.id)
        else:
            if self.status_surface.version.update("Rhythm Stacker "+VERSION+" By Lucien"):
                self.status3.update(
                    font(8).render(
                        "Rhythm Stacker "+VERSION+" By Lucien",
                        True, COLOR_GOLD
                    ),self.status_surface.version.id
                )
    
    def run_prepare(self):
        #这么个代码还挺有仪式感...
        self.running=True
    
    def quit(self):
        self.running=False
        if FLAG_CHECK_MODE in self.state:
            data=self.state.get_flag_data(FLAG_CHECK_MODE)
            if data.file=="user_login":
                if data.checked:
                    subprocess.run("start %windir%\\explorer.exe",shell=True)
                else:
                    subprocess.run("shutdown /l",shell=True)
            else:
                with open(data.file,'w') as f:
                    if data.checked:
                        f.write('1')
                    else:
                        f.write('-1')
    
    def play_sfx(self):
        if self.state!=MODE_PLAYING:
            return
        data=self.state.get_mode_data()
        if FLAG_CHECK_MODE in self.state:
            if data.count==self.state.get_flag_data(FLAG_CHECK_MODE):
                if PLAY_END_REACH_SFX:
                    random.choice(REACH_TARGET_SOUND).play()
        elif FLAG_GAMEOVER in self.state:
            if PLAY_END_REACH_SFX:
                random.choice(FAIL_SOUND).play()
        elif data.mistake:
            if PLAY_MISTAKE_SFX:
                if abs(data.last_offset)>=BIG_MISTAKE_RANGE:
                    random.choice(MISTAKE_BIG_SOUND).play()
                else:
                    random.choice(MISTAKE_SMALL_SOUND).play()
        else:
            if PLAY_HIT_SFX:
                random.choice(HIT_SOUND).play()
    
    def remove_hitless_flag(self):
        self.state.remove_flag(FLAG_CALIBRATION_PREPARE)
        self.state.remove_flag(FLAG_ESCAPING)
        self.state.remove_flag(FLAG_QUITTING)
    
    def on_key(self):
        self.remove_hitless_flag()
        if self.state==MODE_PLAYING or self.state==MODE_CALIBRATION:
            if FLAG_GAMEOVER in self.state:
                if self.state==MODE_CALIBRATION:
                    self.save_calibration_data()
                self.newgame()
            else:
                self.stack()
        elif self.state==MODE_SCORE_DISPLAYING:
            self.switch(MODE_PLAYING)
        self.play_sfx()
    
    def on_esc(self):
        if FLAG_ESCAPING in self.state:
            self.remove_hitless_flag()
            self.gameover()
        elif FLAG_QUITTING in self.state:
            self.remove_hitless_flag()
            self.quit()
        elif self.state==MODE_PLAYING:
            self.remove_hitless_flag()
            if self.state.get_mode_data().count==0:
                self.state.add_flag(Flag(FLAG_QUITTING))
            else:
                self.state.add_flag(Flag(FLAG_ESCAPING))
        else:
            self.on_key()
    
    def on_f2(self):
        self.remove_hitless_flag()
        if self.state==MODE_PLAYING:
            if self.state.get_mode_data().count==0:
                self.switch(MODE_SCORE_DISPLAYING)
            else:
                self.save_score()
        elif self.state==MODE_SCORE_DISPLAYING:
            self.import_score()
        else:
            self.on_key()
    
    def on_f3(self):
        self.remove_hitless_flag()
        if self.state==MODE_SCORE_DISPLAYING:
            self.save_score()
        else:
            if FLAG_F3_STATUS_HIDING in self.state:
                self.state.remove_flag(FLAG_F3_STATUS_HIDING)
            else:
                self.state.add_flag(Flag(FLAG_F3_STATUS_HIDING))
    
    def on_f4(self):
        if FLAG_CALIBRATION_PREPARE in self.state:
            do=True
        elif self.state==MODE_PLAYING or self.state==MODE_CALIBRATION:
            if self.state.get_mode_data().count==0:
                do=True
            else:
                do=False
        else:
            self.on_key()
            return
        if do:
            if self.state==MODE_PLAYING:
                self.switch(MODE_CALIBRATION)
            else:
                self.switch(MODE_PLAYING)
        else:
            self.state.add_flag(Flag(FLAG_CALIBRATION_PREPARE))
    
    def get_score_surface(self):
        text=(
            ''
            if self.state==MODE_SCORE_DISPLAYING
            else self.lang(35)
            if FLAG_QUITTING in self.state
            else self.lang(40)
            if FLAG_ESCAPING in self.state
            else (
                self.lang(20)
                if self.state==MODE_PLAYING
                else self.lang(48)
            )
            if FLAG_CALIBRATION_PREPARE in self.state
            else (
                str(round(statistics.mean(self.state.get_mode_data().offsets),OFFSET_ROUND))
                if self.state.get_mode_data().count!=0
                else self.lang(51)
            )
            if self.state==MODE_CALIBRATION
            else (
                str(self.state.get_mode_data().count)
                if self.state.get_mode_data().count!=0
                else "// Rhythm / Stacker //"
                if not config.get("LEFTSITERIGHT",False)
                else "\\\\ rekcatS \\ mhtyhR \\\\"     #彩蛋(
            )
        )
        color=(
            COLOR_BLACK
            if self.state==MODE_SCORE_DISPLAYING
            else COLOR_GOLD
            if FLAG_CALIBRATION_PREPARE in self.state or FLAG_ESCAPING in self.state or FLAG_QUITTING in self.state
            else (
                COLOR_GOLD
                if self.state.get_mode_data().count==0
                else COLOR_RED
                if self.state.get_mode_data().mistake
                else COLOR_WHITE
            )
            if self.state==MODE_PLAYING
            else (
                COLOR_GOLD
                if FLAG_GAMEOVER in self.state or self.state.get_mode_data().count==0
                else COLOR_WHITE
            )
        )
        return font(36).render(
            text,True,color
        )

    def get_gameover_surface(self):
        if not FLAG_GAMEOVER in self.state or self.state==MODE_SCORE_DISPLAYING:
            return pg.Surface((0,0))
        if self.state==MODE_PLAYING:
            return font(24).render(
                self.lang(37,rank=self.state.get_mode_data().rank),True,COLOR_GOLD
            )
        else:
            return font(24).render(
                self.lang(36,rank=self.state.get_mode_data().rank),True,COLOR_GOLD
            )
    
    def roll(self,dt):
        if not FLAG_ROLLING in self.state:
            return
        data=self.state.get_flag_data(FLAG_ROLLING)
        move=data.rolling_speed*dt
        if data.rolling_direction==1:
            if self.cam_pos>=data.rolling_to:
                self.state.remove_flag(FLAG_ROLLING)
                return
            to=self.cam_pos+move
            if to>=data.rolling_to:
                self.state.remove_flag(FLAG_ROLLING)
                to=data.rolling_to
        else:
            if self.cam_pos<=data.rolling_to:
                self.state.remove_flag(FLAG_ROLLING)
                return
            to=self.cam_pos-move
            if to<=data.rolling_to:
                self.state.remove_flag(FLAG_ROLLING)
                to=data.rolling_to
        self.cam_pos=to

    def run(self):
        while self.running:
            dt=self.clock.tick(FPS)/1000
            for event in pg.event.get():
                if self.check_input_terminate():
                    continue
                if event.type==pg.TEXTINPUT:
                    continue
                elif event.type==pg.QUIT:
                    self.quit()
                elif event.type==pg.KEYDOWN:
                    if event.key==pg.K_ESCAPE:
                        self.on_esc()
                    elif event.key==pg.K_F2:
                        self.on_f2()
                    elif event.key==pg.K_F3:
                        self.on_f3()
                    elif event.key==pg.K_F4:
                        self.on_f4()
                    else:
                        self.on_key()
                    #只在点击时更新分数和游戏结束文本以提高性能
                    self.score_surface=self.get_score_surface()
                    if FLAG_GAMEOVER in self.state:
                        self.gameover_surface=self.get_gameover_surface()
            self.roll(dt)
            self.update_status_bar()
            self.group.update()

            self.screen.fill(COLOR_BLACK)
            brick_surface=self.back.get()
            self.group.draw(brick_surface)
            brick_surface.blit(pg.transform.flip(self.score_data.score_surface,flip_x=False,flip_y=True),(0,0))
            real_brick_surface=pg.transform.flip(brick_surface,flip_x=False,flip_y=True)
            self.screen.blit(real_brick_surface,(0,-(brick_surface.get_height()-2*SIZE[1]-self.cam_pos)))
            self.screen.blit(self.status1.get(),(0,0))
            status2_surface=self.status2.get()
            self.screen.blit(status2_surface,(SIZE[0]-status2_surface.get_width(),0))
            status3_surface=self.status3.get()
            self.screen.blit(status3_surface,(SIZE[0]-status3_surface.get_width(),SIZE[1]-status3_surface.get_height()))
            self.screen.blit(self.score_surface,(int((SIZE[0]-self.score_surface.get_rect().width)//2),3*self.score_surface.get_rect().height))
            if FLAG_GAMEOVER in self.state:
                self.screen.blit(self.gameover_surface,(int((SIZE[0]-self.gameover_surface.get_rect().width)//2),self.gameover_surface.get_rect().height))
            pg.display.flip()

if __name__=="__main__":
    try:
        if len(sys.argv)==1:
            rs=RhythmStacker()
        elif len(sys.argv)==3:
            rs=RhythmStacker(check_mode=True,file=sys.argv[1],target=int(sys.argv[2]))
        else:
            raise SystemExit(Language()(11))
        rs.run_prepare()
        rs.run()
        sys.exit(0)
    except Exception:
        a=traceback.format_exc()
        with open("traceback_last.txt",'w') as f:
            f.write(a)
