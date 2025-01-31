import pyautogui
import random
import tkinter as tk
x = 1650
cycle = 0
check = 1
idle_num =[0]
sleep_num = [1]
# walk_left = [2]
# walk_right = [3]
# event_number = random.randrange(1,3)
event_number = 2
impath = 'img'
#transfer random no. to event
def event(cycle,check,event_number,x):
    if event_number in idle_num:
        check = 0
        print('idle')
        window.after(40,update,cycle,check,event_number,x) #no. 1,2,3,4 = idle
    elif event_number == 5:
        check = 1
        print('from idle to sleep')
        window.after(100,update,cycle,check,event_number,x) #no. 5 = idle to sleep
    # elif event_number in walk_left:
    #     check = 4
    #     print('walking towards left')
    #     window.after(100,update,cycle,check,event_number,x)#no. 6,7 = walk towards left
    # elif event_number in walk_right:
    #     check = 5
    #     print('walking towards right')
    #     window.after(100,update,cycle,check,event_number,x)#no 8,9 = walk towards right
    elif event_number in sleep_num:
        check  = 2
        print('sleep')
        window.after(1000,update,cycle,check,event_number,x)#no. 10,11,12,13,15 = sleep
    elif event_number == 14:
        check = 3
        print('from sleep to idle')
        window.after(100,update,cycle,check,event_number,x)#no. 15 = sleep to idle


def choose_event(event_number):
    if event_number in idle_num:
        window.after(40,update,cycle,0,event_number,x)
        print('idle')
    elif event_number == 2:
        window.after(40,update,cycle,1,event_number,x)
        print('from idle to sleep')
    # elif event_number in walk_left:
    #     print('walking towards left')
    # elif event_number in walk_right:
    #     print('walking towards right')
    elif event_number in sleep_num:
        window.after(40,update,cycle,2,event_number,x)
        print('sleep')
    elif event_number == 3:
        window.after(40,update,cycle,3,event_number,x)
        print('from sleep to idle')


#making gif work 
def gif_work(cycle,frames,event_number,first_num,last_num):
    if cycle < len(frames) -1:
        cycle+=1
    else:
        cycle = 0
        # event_number = random.randrange(first_num,last_num+1,1)
        event_number = event_number
    return cycle,event_number
def update(cycle,check,event_number,x):
    #idle
    if check ==0:
        frame = idle[cycle]
        cycle ,event_number = gif_work(cycle,idle,event_number,1,5)
    
    #idle to sleep
    elif check ==1:
        frame = idle_to_sleep[cycle]
        cycle ,event_number = gif_work(cycle,idle_to_sleep,event_number,10,10)
#   sleep
    elif check == 2:
        frame = sleep[cycle]
        cycle ,event_number = gif_work(cycle,sleep,event_number,10,15)
#   sleep to idle
    elif check ==3:
        frame = sleep_to_idle[cycle]
        cycle ,event_number = gif_work(cycle,sleep_to_idle,event_number,1,1)
# #   walk toward left
#     elif check == 4:
#         frame = walk_positive[cycle]
#         cycle , event_number = gif_work(cycle,walk_positive,event_number,1,9)
#         x -= 3
# #   walk towards right
#     elif check == 5:
#         frame = walk_negative[cycle]
#         cycle , event_number = gif_work(cycle,walk_negative,event_number,1,9)
#         x -= -3
    window.geometry('250x250+'+str(x)+'+780')
    window.attributes('-topmost', True)
    label.configure(image=frame)
    # window.after(1,event,cycle,check,event_number,x)
    window.after(1,choose_event,event_number) 


window = tk.Tk()
#call buddy's action gif
idle = [tk.PhotoImage(file=impath+'/lone_image.png').subsample(4,4)]#idle gif
idle_to_sleep = [tk.PhotoImage(file=impath+'/lone_image2.png').subsample(4,4)]#idle to sleep gif
sleep = [tk.PhotoImage(file=impath+'/lone_image.png').subsample(4,4)]#sleep gif
sleep_to_idle = [tk.PhotoImage(file=impath+'/lone_image3.png').subsample(4,4)]#sleep to idle gif
# walk_positive = [tk.PhotoImage(file=impath+'walking_positive.gif',format = 'gif -index %i' %(i)) for i in range(8)]#walk to left gif
# walk_negative = [tk.PhotoImage(file=impath+'walking_negative.gif',format = 'gif -index %i' %(i)) for i in range(8)]#walk to right gif
#window configuration
window.wm_attributes('-transparentcolor', "black")
# window.wm_attributes('-alpha', 0.0)
window.config(highlightbackground='black')
label = tk.Label(window,bd=0,bg='black')
window.overrideredirect(True)
window.wait_visibility(window)
label.pack()
#loop the program
window.after(1,update,cycle,check,event_number,x)
window.mainloop()
