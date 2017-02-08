# river_ws
Wheelchair@River Lab

Download repos to your computer, you can run this command in your home directory
```bash
git clone git@github.com:luorui93/river_ws.git
```

Go to the directory you just downloaded
```bash
cd river_ws
```

Run catkin_make to build the workspace
```bash
catkin_make
```

Configure environmental variables
```bash
cd devel
source setup.bash
```

Then you are good to go
```bash
roslaunch speed_control wheelchair_teleop
```
