import pygame
import os
from time import sleep
from card_reader import cardreader
from threading import *
from api import *
from smartcard.Exceptions import NoCardException

red = (200,0,0)
lightred = (255,0,0)
green = (0,200,0)
lightgreen = (0,255,0)
blue = (0,0,200)
lightblue = (0,0,255)
orange = (255,153,51)
lightorange = (255,178,102)
white = (255,255,255)
grey = (224,224,224)
dgrey = (200,200,200)
black = (0,0,0)
X = 800
Y = 460

clock = pygame.time.Clock()
cr = cardreader()
resv_info = {}
refn = {}
token = {}
otp = []
rate = {"rate":0}

pygame.init()
screen = pygame.display.set_mode((X,Y))
pygame.display.set_caption("Hilbert")

#------------Components--------------------

def text_objects(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

def text(des,font,size,posx,posy,color=black):
    largeText = pygame.font.SysFont(font,size)
    TextSurf, TextRect = text_objects(des, largeText, color)
    TextRect.center = (posx,posy)
    screen.blit(TextSurf, TextRect)

def picture(name,posx,posy,alpha):
    bg = pygame.image.load(name).convert()
    bgrect = bg.get_rect()
    bgrect.center = (posx,posy)
    bg.set_alpha(alpha)   
    screen.blit(bg,bgrect)

def numpad():
    np = []
    
    for i in range (10):
        np.append(Button(str(i),60,60,grey,dgrey,20))
    delete = Button("DEL",60,60,grey,dgrey,20)
    clear = Button("CLR",60,60,grey,dgrey,20)
    
    np[1].place(X/9,Y/2-45)
    np[2].place(X/9+70,Y/2-45)
    np[3].place(X/9+140,Y/2-45)
    np[4].place(X/9,Y/2+25)
    np[5].place(X/9+70,Y/2+25)
    np[6].place(X/9+140,Y/2+25)
    np[7].place(X/9,Y/2+95)
    np[8].place(X/9+70,Y/2+95)
    np[9].place(X/9+140,Y/2+95)
    np[0].place(X/9+70,Y/2+165)
    delete.place(X/9+140,Y/2+165)
    clear.place(X/9,Y/2+165)

    if(len(otp)<6):
        for i in range (10): 
            if(np[i].is_clicked()):
                otp.append(i)
                sleep(0.1)
    
    if(delete.is_clicked()):
        if(len(otp)!=0):
            otp.pop()
            sleep(0.1)  
    if(clear.is_clicked()):
        otp.clear()
        sleep(0.1)

def rating_bar():
    rt = ["Poor","Not good","Average","Good","Excellent"]
    btn = []
    for i in range(5):
        btn.append(Button("",50,50,white,white,5))
        btn[i].place(X/3-20+70*i,Y/3)
            
    for i in range(5):
        if i < rate["rate"] :
            picture("star2c.jpg",X/3+5+70*i,Y/3+25,255)
        else:
            picture("star2.jpg",X/3+5+70*i,Y/3+25,255)
        
        text(rt[i],"Quicksand",12,X/3+5+70*i,Y/3+60)
    
    for i in range(5) :
        if(btn[i].is_clicked()):
            sleep(0.1)
            rate["rate"] = i+1
            return 1
    
    return 0

class Button(object):
    def __init__(self,msg,w,h,ic,ac,msgz,msgc=black):
        self.msg = msg
        self.w = w
        self.h = h
        self.ic = ic
        self.ac = ac
        self.msgz = msgz
        self.msgc = msgc
    
    def place(self,x,y):
        self.x = x
        self.y = y
        mouse = pygame.mouse.get_pos()
        clicked = pygame.mouse.get_pressed()
        if(x+self.w > mouse[0] > x and y+self.h > mouse[1] > y):
            pygame.draw.rect(screen, self.ac, (x,y,self.w,self.h))  #posx,posy,dimx,dimy
        
        else:
            pygame.draw.rect(screen, self.ic, (x,y,self.w,self.h))
        
        btnText2 = text(self.msg,"Quicksand Medium",self.msgz,x+self.w/2,y+self.h/2,self.msgc)

    def is_clicked(self):
        mouse = pygame.mouse.get_pos()
        clicked = pygame.mouse.get_pressed()

        if(self.x+self.w > mouse[0] > self.x and self.y+self.h > mouse[1] > self.y):
            if(clicked[0] == 1):
                return True
        
        return False

#--------------Pages-----------------

def kiosk_menu_page():
    boundary = -X/4
    alpha = 0
    is_inserted = 0
    run = True
    while run:

        for event in pygame.event.get():  # This will loop through a list of any keyboard or mouse events.
            if event.type == pygame.QUIT: # Checks if the red button in the corner of the window is clicked
                run = False  # Ends the game loop
    
        screen.fill(white)
        
        doge = picture('doge2.png',X/4+40,Y/2,alpha)
        if(alpha<128):
            alpha += 3
        
        title = text("Welcome to Hilbert Hostel","Quicksand",40,boundary,60)
        if(boundary<X/3):
            boundary += 9
        
        insert = text("Insert ID card to check-in","Quicksand",20,X-150,Y*3/4)
        ckoutBtn = Button("Check-out",150,60,orange,lightorange,15,white)
        ckoutBtn.place(80,Y-100)
        
        if(ckoutBtn.is_clicked()):
            check_out_page()
            boundary = -X/4
            alpha = 0
        
        #cardBtn = Button("Book",100,50,blue,lightblue,20)
        #cardBtn.place(X-200,Y/2+50)
        
        try:
            cr.connection.connect()
            td = Thread(target=gather_info,args=(cr,resv_info))
            td.start()
            book_detail_page()
            boundary = -X/4
            alpha = 0
        except NoCardException:
            print("no card woei")
            
        #if(cardBtn.is_clicked()):
        #    book_detail_page()
        #    boundary = -X/4
        #    alpha = 0

        pygame.display.update() 
        clock.tick(30)

def book_detail_page():
    run = True
    pointer = 0
    while run:

        for event in pygame.event.get():  # This will loop through a list of any keyboard or mouse events.
            if event.type == pygame.QUIT: # Checks if the red button in the corner of the window is clicked
                cr.card_data.clear()
                resv_info.clear()
                os.remove("room_image.jpg")
                os.remove("resized_room.jpg")
                os.remove("resized_room2.jpg")
                os.remove("card_image.jpg")
                run = False  # Ends the game loop
    
        OTPBtn = Button("Request OTP",150,50,orange,lightorange,13,white)
        nxtrmBtn = Button("Next",60,60,dgrey,grey,13)
        pvsrmBtn = Button("Back",60,60,dgrey,grey,13)
    
        screen.fill(white)   
        title = text("Here is your booking detail","Quicksand",30,(X/4),50)
        
        if(len(resv_info) != 0 and len(cr.card_data) != 0 and os.path.exists("resized_room.jpg")):
            if len(cr.card_data["rooms"])>1 :
                if pointer==0 :    
                    nxtrmBtn.place(X/2+50,Y/2+50)
                    if(nxtrmBtn.is_clicked()):
                        pointer += 1
                        sleep(0.1)
                elif pointer == len(cr.card_data["rooms"])-1 :
                    pvsrmBtn.place(X/6-50,Y/2+50)
                    if(pvsrmBtn.is_clicked()):
                        pointer -= 1
                        sleep(0.1)
                else:
                    nxtrmBtn.place(X/2+50,Y/2+50)
                    if(nxtrmBtn.is_clicked()):
                        pointer += 1
                        sleep(0.1) 
                    pvsrmBtn.place(X/6-50,Y/2+50)
                    if(pvsrmBtn.is_clicked()):
                        pointer -= 1
                        sleep(0.1)  

            rif = resv_info["rooms"][pointer]["type"].capitalize()
            nor = resv_info["rooms"][pointer]["beds"]
            dur = "{} to {}".format(resv_info['checkIn'][:10],resv_info['checkOut'][:10])
            
            add_on = text("Special request","Quicksand",30,X-150,Y/3-50)
            tom = picture('resized_room.jpg',X/3,Y/2-50,128)
            name = text("Name: "+cr.card_data['nameEN'],"Quicksand",15,X/4+50,Y*2/3)
            bk_id = text("Booking ID: "+resv_info['id'],"Quicksand",15,X/4+50,Y*2/3+30)
            room_type = text("Room type: {} , {} bed".format(rif,nor),"Quicksand",15,X/4+50,Y*2/3+70)
            room_dur = text(("Duration: "+dur),"Quicksand",15,X/4+50,Y*2/3+100)
            special_req = text(resv_info['specialRequests'],"Quicksand",15,X-150,Y/3)
            note = text("You can take you card back now","Quicksand Medium",15,X-150,Y-150)
            OTPBtn.place(X-220,Y-80)
            if(OTPBtn.is_clicked()):
                t = Thread(target=request_OTP,args=(resv_info,refn))
                t.start()
                enter_OTP_page()
                pointer = 0
                cr.card_data.clear()
                resv_info.clear()
                os.remove("room_image.jpg")
                os.remove("resized_room.jpg")
                os.remove("resized_room2.jpg")
                os.remove("card_image.jpg")
                run = False
        else :
            pls = text("Please wait","Quicksand",45,X/2,Y/2)

        pygame.display.update() 
        clock.tick(60)

def enter_OTP_page():
    run = True
    while run:

        for event in pygame.event.get():  # This will loop through a list of any keyboard or mouse events.
            if event.type == pygame.QUIT: # Checks if the red button in the corner of the window is clicked
                otp.clear()
                refn.clear()
                run = False  # Ends the game loop
        
        slide = 0
        screen.fill(white)
        title = text("Enter your OTP","Quicksand",30,125,40)
        ref = text("OTP ref no. ","Quicksand",25,95,Y/3+5)
        if(len(refn)!=0):
            refNum = text(refn['referenceCode'],"Quicksand",25,X/4+20,Y/3+5)
        else:
            refNum = text("-","Quicksand",25,X/4+20,Y/3+5)
        rif = resv_info["rooms"][0]["type"].capitalize()
        tom = picture('resized_room2.jpg',X-150,Y/4,128)
        info = text("Name: "+cr.card_data['nameEN'],"Quicksand",15,X-150,Y/2)
        info2 = text("Booking ID: "+resv_info['id'],"Quicksand",15,X-150,Y/2+30)
        info3 = room_type = text("Room type: "+rif,"Quicksand",15,X-150,Y*2/3+70)
        submitBtn = Button("Submit",100,50,orange,lightorange,20,white)

        for i in range(6):
            pygame.draw.rect(screen,grey,(50+slide,Y/4-40,50,50))
            slide += 70
        
        slide = 0
        for num in otp:
            text(str(num),"Quicksand",25,75+slide,Y/4-10)
            slide += 70

        submitBtn.place(X/2-50,Y-80)
        np = numpad()
    
        if(submitBtn.is_clicked()):
            t = Thread(target=verify_OTP,args=(resv_info,otp,token))
            t.start()
            take_pic_page()
            otp.clear()
            refn.clear()
            run = False
        
        pygame.display.update() 
        clock.tick(60)

def take_pic_page():
    run = True
    while run:

        for event in pygame.event.get():  # This will loop through a list of any keyboard or mouse events.
            if event.type == pygame.QUIT: # Checks if the red button in the corner of the window is clicked
                token.clear()
                os.remove("selfie.jpg")
                os.remove("resized_selfie.jpg")
                run = False  # Ends the game loop
        
        screen.fill(white)    

        title = text("Selfie verification","Quicksand",35,X/2,45)
        des = text("Please take a selfie before finishing the process","Quicksand",20,X/2,80)
        
        r = pygame.draw.rect(screen,black,(X/2-140,Y/2-105,280,210))
        r2 = pygame.draw.rect(screen,white,(X/2-139,Y/2-104,278,208))

        smileBtn = Button("Smile!",120,50,orange,lightorange,20,white)
        smileBtn.place(X/5,Y-100)

        if(os.path.exists("resized_selfie.jpg")):
            smileBtn.msg = "Retake"
            smileBtn.place(X/5,Y-100)
            proc = picture('resized_selfie.jpg',X/2,Y/2,255)
            finishBtn = Button("Finish",120,50,orange,lightorange,20,white)
            finishBtn.place(X*4/5-120,Y-100)

            if finishBtn.is_clicked() :
                t = Thread(target=send_data,args=(cr,token))
                t.start()
                check_in_complete_page()
                token.clear()
                os.remove("selfie.jpg")
                os.remove("resized_selfie.jpg")
                run = False

        if(smileBtn.is_clicked()):
            capture_pic(cr)
           
        pygame.display.update() 
        clock.tick(60)

def check_in_complete_page():
    blink = 0
    run = True
    while run:

        for event in pygame.event.get():  # This will loop through a list of any keyboard or mouse events.
            if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN: # Checks if the red button in the corner of the window is clicked
                run = False  # Ends the game loop
        
        screen.fill(white)
        title = text("Check-in complete","Quicksand",30,(X/4)-50,50)
        info = text("Check your account on the website","Quicksand",40,X/2,Y/2)
        if(blink<60): 
            leave = text("-Touch to leave-","Quicksand",20,(X/2),Y-80)
        if(blink>120):
            blink = 0   
        blink += 1
        pygame.display.update() 
        clock.tick(60)

def check_out_page():
    run = True
    while run:

        for event in pygame.event.get():  # This will loop through a list of any keyboard or mouse events.
            if event.type == pygame.QUIT:  # Checks if the red button in the corner of the window is clicked
                run = False  # Ends the game loop
        
        screen.fill(white)
        hb = text("Hilbert Hostel","Quicksand",40,X/2,70,orange)
        title = text("Please scan QR Code to check-out","Quicksand",20,X/2,Y/4)
        yee = Button("Finish",120,50,blue,lightblue,20,white)
        back = Button("Back",150,50,orange,lightorange,20,white)
        back.place(X*3/4,Y*3/4)
        if back.is_clicked() :
            run = False

        yee.place(X/2-60,Y/2+50)
        if yee.is_clicked() :
            run = check_out_confirm_page()
        pygame.display.update() 
        clock.tick(30)

def check_out_confirm_page():
    run = True
    while run:

        for event in pygame.event.get():  # This will loop through a list of any keyboard or mouse events.
            if event.type == pygame.QUIT:  # Checks if the red button in the corner of the window is clicked
                run = False  # Ends the game loop
        
        screen.fill(white)
        hb = text("Hilbert Hostel","Quicksand",40,X/2,70,orange)
        r = pygame.draw.rect(screen,black,(X/2-200,Y/2-105,400,210))
        r2 = pygame.draw.rect(screen,white,(X/2-200,Y/2-104,400,210))
        title = text("Confirmed checkout?","Quicksand",20,X/2,Y/2-10)
        cfm = Button("Confirm",150,50,orange,lightorange,20,white)
        cancel = Button("Cancel",150,50,orange,lightorange,20,white)

        cfm.place(X/2-170,Y/2+20)
        if cfm.is_clicked() :
            check_out_success_page()
            return False
        cancel.place(X/2+20,Y/2+20)
        if cancel.is_clicked() :
            return True
        pygame.display.update() 
        clock.tick(30)
        
def check_out_success_page():
    run = True
    thanks = 0
    while run:

        for event in pygame.event.get():  # This will loop through a list of any keyboard or mouse events.
            if event.type == pygame.QUIT:  # Checks if the red button in the corner of the window is clicked
                run = False  # Ends the game loop
        
        screen.fill(white)
        homeBtn = Button("Home",150,50,orange,lightorange,20,white)
        hb = text("Hilbert Hostel","Quicksand",40,X/2,70,orange)
        hb2 = text("How was Hilbert Hostel experience?","Quicksand",30,X/2,100)
        des = text("Share your experience while memories are fresh.","Quicksand",12,X/2,Y/2+50)
        des2 = text("Your review will help Hilbert Hostel imporves accomodation and tell those interested in what you'll find.","Quicksand",12,X/2,Y/2+70)
        des3 = text("Hilbert Hostel won't see your suggestion until you review you as well.","Quicksand",12,X/2,Y/2+110)
        
        thanks += rating_bar()
        if thanks != 0 :
            text("Thank you for rating","Quicksand",20,X/2,Y/2+20)

        homeBtn.place(X*3/4,Y-100)
        if homeBtn.is_clicked():
            thanks = 0
            rate["rate"] = 0
            run = False
        
        pygame.display.update() 
        clock.tick(30)

kiosk_menu_page()

pygame.quit()  # If we exit the loop this will execute and close our game
