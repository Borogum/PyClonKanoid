# -*- coding: utf-8 -*-

# @Author: Darío M. García Carretero
# @Date:   2018-07-04T11:20:39+02:00
# @Email:  dario.aviles@gmail.com
# @Last modified by:   Darío M. García Carretero
# @Last modified time: 2018-07-12T09:49:46+02:00


import clr

clr.AddReference('IronPython.Wpf')
clr.AddReference('System.Windows.Forms')
clr.AddReference('PresentationFramework')
try:
    clr.AddReference('StdLib') # Needed only for compiled version
except:
    pass

import wpf
import math
import os
import random # Random goes from 0 to 0.5 I don´t know why

from System import EventHandler, TimeSpan, Uri
from System.Windows import Application, Window, TextAlignment
from System.Windows.Media import SolidColorBrush, Colors, Color
from System.Windows.Media.Imaging import BitmapImage
from System.Windows.Controls import TextBlock, Image
from System.Windows.Input import Key
from System.Windows.Threading import DispatcherTimer
from System.Windows.Shapes import Rectangle, Line


class Direction(object):

    LEFT=(-1,0)
    RIGHT=(1,0)
    UP=(0,1)
    DOWN=(0,-1)


class Edge(object):

    def __init__(self,xpos,ypos,length,direction):
        self.xpos=xpos
        self.ypos=ypos
        self.length=length
        self.direction=direction
        self.xdir=direction[0]
        self.ydir=direction[1]

    def collision(self,box):
        if self.direction in (Direction.UP,Direction.DOWN):

            return  ((box.xpos - box.width/2) <= self.xpos <= (box.xpos + box.width/2)) and \
                    ((self.ypos - self.length/2) <= (box.ypos+box.height/2) and \
                    (self.ypos + self.length/2) >= (box.ypos-box.height/2))

        elif self.direction in (Direction.LEFT,Direction.RIGHT):

            return  ((box.ypos - box.height/2) <= self.ypos <= (box.ypos + box.height/2)) and \
                    ((self.xpos - self.length/2) <= (box.xpos+box.width/2) and \
                    (self.xpos + self.length/2) >= (box.xpos-box.width/2))


class Wall(object):

    def __init__(self,xpos,ypos,length,direction):
        self.xpos=xpos
        self.ypos=ypos
        self.length=length
        self.direction=direction
        self.xdir=direction[0]
        self.ydir=direction[1]
        self.destroyed=False
        self.edges=self.get_edges()
        self.shape=Line()
        self.shape.Stroke = SolidColorBrush(Colors.Black)
        self.shape.X1 = 0
        self.shape.Y1 = 0
        if direction in (Direction.LEFT,Direction.RIGHT):
            self.shape.X2 = self.length
            self.shape.Y2 = 0
        else:
            self.shape.X2 = 0
            self.shape.Y2 = self.length
        self.shape.StrokeThickness = 1

    def get_edges(self):
        return [Edge(self.xpos,self.ypos,self.length,self.direction)]

    def collision(self,obj):
        for edge in self.edges:
            if edge.collision(obj):
                return edge

    def on_hit(self,other,edge):
        pass

    def get_bottom(self):
        return self.ypos + (direction not in (Direction.LEFT,Direction.RIGHT))*self.length/2

    def get_left(self):
        return self.xpos - (direction in (Direction.LEFT,Direction.RIGHT))*self.length/2


class Box(object):

    def __init__(self,width,height,xpos,ypos,direction,speed):
        self.width=width
        self.height=height
        self.xpos = xpos
        self.ypos = ypos
        self.xdir, self.ydir = self.normalize(direction[0],direction[1])
        self.speed = speed
        self.destroyed=False
        self.edges=self.get_edges()
        self.shape=Rectangle()
        self.shape.Width = width
        self.shape.Height = height
        self.shape.Stroke = SolidColorBrush(Colors.White)
        self.shape.Fill = SolidColorBrush(Colors.Black)

    def normalize(self,xpos,ypos):
        n=math.sqrt(pow(xpos,2)+pow(ypos,2))
        return xpos/n,ypos/n

    def scalar(self,edge):
        return self.xdir*edge.xdir+self.ydir*edge.ydir

    def set_direction(self,direction):
        self.xdir, self.ydir = self.normalize(direction[0],direction[1])

    def get_edges(self):
        return [
                Edge(self.xpos,self.ypos+self.height/2,self.width,Direction.LEFT),
                Edge(self.xpos+self.width/2,self.ypos,self.height,Direction.UP),
                Edge(self.xpos,self.ypos-self.height/2,self.width,Direction.RIGHT),
                Edge(self.xpos-self.width/2,self.ypos,self.height,Direction.DOWN)
                ]

    def get_direction(self):
        return (self.xdir,self.ydir)

    def get_bottom(self):
        return self.ypos-self.height/2

    def get_left(self):
        return self.xpos-self.width/2

    def collision(self,obj):
        for edge in self.edges:
            if edge.collision(obj):
                return edge

    def move(self):
        self.xpos+=self.xdir*self.speed
        self.ypos+=self.ydir*self.speed
        self.edges=self.get_edges()

    def on_hit(self,other,edge):
        pass


class Ball(Box):

    def on_hit(self,other,edge):
        s=self.scalar(edge)
        r=(2*random.random()-1)*(4*0.017) # +- 4 (1 Grad = 0.017 Rad)
        a=-2*math.acos(s)+r
        x=self.xdir*math.cos(a)-self.ydir*math.sin(a)
        y=self.xdir*math.sin(a)+self.ydir*math.cos(a)
        self.xdir=x
        self.ydir=y


class DestroyableBox(Box):

        def on_hit(self,other,edge):
            self.destroyed=True


class Gui(Window):

    def __init__(self,cfg):
        self.path = os.path.dirname(os.path.abspath(__file__))
        basename=os.path.basename(os.path.abspath(__file__)).split('.')[0]
        wpf.LoadComponent(self, os.path.join(self.path, basename + '.xaml'))
        self.Icon=BitmapImage(Uri(os.path.join(self.path,'icon.ico')))
        self.config_file=os.path.join(self.path, cfg)
        self.config_file=cfg
        self.configuration={}
        self.canvas = self.FindName("Canvas")
        self.started=False
        self.mask=[]
        self.objects=[]
        self.base=None
        self.ball=None
        self.floor=None
        #START Configuration file
        with open(self.config_file) as f:
            for l in f:
                if l.startswith('#') or l.startswith('\n'):
                    pass
                elif l.startswith('[blocks]'):
                    for l in f:
                        d=l.strip()
                        length=len(d)
                        row=[]
                        for x in d:
                            if x=='@':
                                row.append(1)
                            elif x=='x':
                                row.append(0)
                            else:
                                pass
                        self.mask.append(row)
                else:
                    kv=[x.strip() for x in l.split('=')]
                    self.configuration[kv[0].lower()]=int(kv[1])
        self.Width = self.configuration['width']
        self.Height  = self.configuration['height']
        #END Configuration file
        self.timers={'ball':self.create_timer(self.ball_timer,1000/self.configuration['fps']),
                     'base':self.create_timer(self.base_timer,1000/self.configuration['fps'])}

    def get_text(self,text):
        tb = TextBlock()
        tb.Text = text
        tb.Width=self.canvas.ActualWidth
        tb.Height=40
        tb.FontSize=30
        tb.Background = SolidColorBrush(Colors.Black)
        tb.Foreground = SolidColorBrush(Colors.White)
        tb.TextAlignment = TextAlignment.Center
        return tb

    def show_text(self,text):
        self.canvas.SetLeft(text,0)
        self.canvas.SetBottom(text,(self.canvas.ActualHeight-text.Height)/2)
        self.canvas.Children.Add(text)

    def create_timer(self,f,freq):
        timer=DispatcherTimer()
        timer.Tick += EventHandler(f)
        timer.Interval = TimeSpan.FromMilliseconds(freq)
        return timer

    def plot(self,obj):
        self.canvas.SetLeft(obj.shape,obj.get_left())
        self.canvas.SetBottom(obj.shape,obj.get_bottom())
        if obj.shape not in self.canvas.Children:
            self.canvas.Children.Add(obj.shape)

    def loaded(self,sender,e):
        self.init_game()

    def clear(self):
        for timer in self.timers:
            self.timers[timer].Stop()
        self.objects[:]=[]
        self.canvas.Children.Clear()

    def init_game(self):
        self.clear()
        self.started=False
        self.show_text(self.get_text("Press 'Enter' to play"))

    def start_game(self):
        self.clear()
        #WALLS
        walls = [Wall(0, self.canvas.ActualHeight/2, self.canvas.ActualHeight, Direction.UP),
                 Wall(self.canvas.ActualWidth/2, self.canvas.ActualHeight, self.canvas.ActualWidth, Direction.RIGHT),
                 Wall(self.canvas.ActualWidth, self.canvas.ActualHeight/2, self.canvas.ActualHeight, Direction.DOWN),
                 Wall(self.canvas.ActualWidth/2, 0, self.canvas.ActualWidth, Direction.LEFT)]
        for wall in walls:
            self.objects.append(wall)
        self.floor=walls[-1]
        #BASE
        self.base=Box(self.configuration['base_width'],self.configuration['base_height'],
               self.canvas.ActualWidth/2,20,Direction.LEFT,self.configuration['base_speed'])
        self.plot(self.base)
        self.objects.append(self.base)
        #BALL
        rx=2*random.random()-0.5
        r=2*random.random()-1
        r=r/abs(r)
        ry=r*math.sqrt(1-pow(rx,2))
        self.ball=Ball(self.configuration['ball_size'],self.configuration['ball_size'],
               self.canvas.ActualWidth/2,50,(rx,ry), self.configuration['ball_speed'])
        self.plot(self.ball)
        rows=len(self.mask)
        cols=len(self.mask[0])
        block_height=self.configuration['block_height']
        block_width=self.configuration['block_width']
        for i in range(rows):
             for j in range(cols):
                 if self.mask[i][j] == 1:
                     xpos=block_width+j*block_width+(block_width/2)
                     ypos=self.canvas.ActualHeight-(block_width+block_width*i+(block_width/2))
                     db=DestroyableBox(block_width, block_height, xpos, ypos, (1,0), 0)
                     self.plot(db)
                     self.objects.append(db)
        #INIT GAME
        self.timers['ball'].Start()
        self.started=True

    def ball_timer(self,sender,e):

        for obj in self.objects:
            c=obj.collision(self.ball)
            if c is not None:
                if obj==self.floor:
                    self.timers['ball'].Stop()
                    self.show_text(self.get_text("Keep trying! Press 'Enter' to retry"))
                    self.started=False
                else:
                    self.ball.on_hit(obj,c)
                    obj.on_hit(self.ball,None)

                if obj.destroyed:
                    self.canvas.Children.Remove(obj.shape)
                    self.objects.remove(obj)
                break

        if len(self.objects)==5: #4 Walls + base
            self.timers['ball'].Stop()
            self.show_text(self.get_text("Good job! Press 'Esc' to retry"))
            self.started=False
        else:
            self.ball.move()
            self.plot(self.ball)

    def base_timer(self,sender,e):
        if self.started and ((self.base.get_direction() == Direction.LEFT and \
        (self.base.xpos-self.base.width/2-self.base.speed)>0) \
        or (self.base.get_direction() == Direction.RIGHT and \
        (self.base.xpos+self.base.width/2+self.base.speed) < self.canvas.ActualWidth)):
            self.base.move()
            self.plot(self.base)

    def key_up(self,sender,e):
        (e.Key == Key.Escape) and self.init_game()
        (e.Key == Key.Enter) and not self.started and self.start_game()
        if (e.Key in (Key.Right,Key.Left)) and self.timers['base'].IsEnabled:
            self.timers['base'].Stop()

    def key_down(self,sender,e):
        if e.Key == Key.Left:
            if self.started and not self.timers['base'].IsEnabled:
                self.base.set_direction(Direction.LEFT)
                self.timers['base'].Start()
        elif e.Key == Key.Right:
            if self.started and not self.timers['base'].IsEnabled:
                self.base.set_direction(Direction.RIGHT)
                self.timers['base'].Start()


if __name__ == '__main__':
    Application().Run(Gui('config.cfg'))
