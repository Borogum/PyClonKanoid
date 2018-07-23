# PyClonKanoid

## What is PyClonKanoid?

PyClonKanoid is a **very simple** version of a classic videogame named [Arkanoid](https://en.wikipedia.org/wiki/Arkanoid "Arkanoid Wiki") . PyClonKanoid was programmed using a Python implementation called [IronPython](http://ironpython.net/ "IronPython Website") in combination with Windows Presentation Foundation (WPF) technology.


## What is the objetive of project?

The objetive is kill my boredom.


## How to use it?

You can run it directly with iron python command interpreter or you can compile the source code to generate an exe file. To compile source code you need use the iron python compiler. I create a bat file to realize compile task automatically:

```
@ECHO OFF

SET IRONPYTHON_COMPILER=C:\IronPython2.7\ipyc.exe
SET SOURCE_PATH=%~dp0
SET OUT_PATH=%~dp0bin\

copy /Y %SOURCE_PATH%pyclonkanoid.xaml %OUT_PATH%pyclonkanoid.xaml
copy /Y %SOURCE_PATH%config.cfg %OUT_PATH%config.cfg
copy /Y %SOURCE_PATH%icon.ico %OUT_PATH%icon.ico

%IRONPYTHON_COMPILER ^
%SOURCE_PATH%pyclonkanoid.py ^
/out:%OUT_PATH%pyclonkanoid ^
/main:%SOURCE_PATH%pyclonkanoid.py ^
/target:winexe ^
/win32icon:%SOURCE_PATH%icon.ico ^
/embed

```
You must change, when necessary, the values of variables _IRONPYTHON_COMPILER_, _SOURCE_PATH_ and _OUT_PATH_. To make the exe file work you must include some assemblies in the exe's folder. But don´t worry, all necessary files can be found in last [release](https://github.com/Borogum/PyClonKanoid/releases) of project.


## Controls

Press 'Enter' to start the game and use 'left' or 'right' arrows to move the base. You can stop game at anytime pressing 'Esc' key.

## Configuration

In the configuration file (config.cfg) you can modify a lot of parameters of game. Frames per second (fps), ball speed, etc. An example of a configuration file could be:

```
#Sample configuration file#

fps = 60
width = 580
height = 800
ball_speed = 8
ball_size = 15
base_speed = 10
base_width = 90
base_height = 20
block_width = 25
block_height = 25

[blocks]
x@x@x@@@x@xxx@xxx@@@x
x@x@x@xxx@xxx@xxx@x@x
x@@@x@@xx@xxx@xxx@x@x
x@x@x@xxx@xxx@xxx@x@x
x@x@x@@@x@@@x@@@x@@@x
xxxxxxxxxxxxxxxxxxxxx
@xxx@x@@@x@@xx@xxx@@x
@xxx@x@x@x@x@x@xxx@x@
@xxx@x@x@x@@xx@xxx@x@
@x@x@x@x@x@x@x@xxx@x@
x@x@xx@@@x@x@x@@@x@@x

```

Additionally, you can customize block distribution in section [blocks]. An x represents an empty space and @ represents a block. In previous example, the blocks shows a well-known message for all programmers.
