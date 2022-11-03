#from re import L
from cgi import test
from pkgutil import extend_path
from re import L
from shutil import ExecError
from tempfile import TemporaryFile
from PIL import Image, ImageDraw, ImageFilter, ImageStat
from cv2 import resize
from matplotlib.image import thumbnail
#from cv2 import threshold
#from flask import request
#from matplotlib.pyplot import text
import pygame
import math
import Class_object as co
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import io
import random
import time
import os
from os import listdir
from os.path import isfile, join
import tkinter
import tkinter.filedialog as tkFileDialog

#glitter of her eyes, full of tears
#heart2 barren2
#world that had no hope in it and no desire
#display the array in a cleaner manner
def display_array(arr):
    for rows in arr:
        print(rows)
    print("")
#trims the image so the non-shape colors are removed
def dowload_img(url):
    
    image_content = requests.get(url).content

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file)
        

        #file_path = download_path + file_name
        
        # with open(file_path, "wb") as f:
        #     image.save(f, "JPEG")
    except Exception as e:
        print("failed - ", e)
        return None
    return image
def get_images_from_google(wd, delay, max_image, search):
    
    url = "https://www.google.com/search?q={}&source=lnms&tbm=isch&sa=X&ved".format(search)
    wd.get(url)

    image_urls = []
    set_num_time = 0
    while len(image_urls) < max_image and set_num_time <= 10:
        thumbnail = wd.find_elements(By.CLASS_NAME, "Q4LuWd")

        for img in thumbnail[len(image_urls): max_image]:
            try:
                img.click()
                time.sleep(delay)
            except:
                continue
            
            images = wd.find_elements(By.CLASS_NAME, "n3VNCb")
            for image in images:
                if image.get_attribute('src') and 'http' in image.get_attribute('src'):
                    image_urls.append(image.get_attribute('src'))
            
            set_num_time += 1
            if(set_num_time >= 10):
                print("breaking")
                break
    return image_urls
def cut_img(img, mag, threshold, direction):
    #start from lines on the four side of the picture and make every pixel black if it does not touch an edge, helps get the shape in the middle
    #from left to right
    width, height = img.size
    if(direction == "left" or direction == None):
        for rows in range(height):
            for col in range(width):
                if(mag[rows][col] >= threshold * 255):
                    break
                else:
                    img.putpixel((col,rows), (0,0,1))
    if(direction == "top" or direction == None):
        #from top to bottom
        for col in range(width):
            for rows in range(height):
                if(mag[rows][col] >= threshold * 255):
                    break
                else:
                    img.putpixel((col,rows), (0,0,1))
    if(direction == "bottom" or direction == None):
        #from bottom to top
        for col in range(width):
            for rowsinv in range(height):
                if(mag[height - rowsinv - 1][col] >= threshold * 255):
                    break
                else:
                    img.putpixel((col,height - rowsinv - 1), (0,0,1))
    if(direction == "right" or direction == None):
        #from right to left
        for rows in range(height):
            for colinv in range(width):
                if(mag[rows][width - colinv - 1] >= threshold * 255):
                    break
                else:
                    img.putpixel((width - colinv - 1,rows), (0,0,1))
    return img
#get the general image color
def get_general_img_color(img, height, width):
    num_to_devide = 0
    r_sum = 0
    b_sum = 0
    g_sum = 0
    for y in range(height):
        for x in range(width):
            r,g,b=img.getpixel((x,y))
            if(r != 0 and g != 0 and b != 0):
                r_sum += r
                b_sum += b
                g_sum += g
                num_to_devide += 1
    
    return (int(r_sum/num_to_devide), int(b_sum/num_to_devide), int(g_sum/num_to_devide))
#blurs the grid arround the array at a specific color
def expand(img, x, y, radius, general_color):
    r_sum = 0 
    b_sum = 0
    g_sum = 0
    total_num = 0
    width, height = img.size 
    
    
    if(x > width - 1):
        x = width - 1
    if(y > height - 1):
        y = height - 1
    if(x < 0):
        x = 0
    if(y < 0):
        y = 0
    
    
    r,g,b = img.getpixel((x, y))
    for y_add in range(radius * 2 + 1):
        for x_add in range(radius * 2 + 1):
            if(img.mode == "RGB"):
                if((0 <= x + x_add - radius < width) and (0 <= y + y_add - radius < height)):
                    r,g,b = img.getpixel((x + x_add - radius, y + y_add - radius))
                    if((r,g,b) != (0,0,1)):
                        r_sum += r
                        g_sum += g
                        b_sum += g
                        total_num += 1
            #if pixel not black
            
    if(total_num != 0):
        img.putpixel((x, y),(int(r_sum/total_num), int(b_sum/total_num), int(g_sum/total_num)))
    else:
        img.putpixel((x, y), general_color)
    
    return img
#blur starting from the middle
def spiral(X, Y):
    x = y = 0
    dx = 0
    dy = -1
    arr = []
    for i in range(max(X, Y)**2):
        if (-X/2 < x <= X/2) and (-Y/2 < y <= Y/2):
            arr.append((x, y))
            # DO STUFF...
        if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
            dx, dy = -dy, dx
        x, y = x+dx, y+dy
    return arr
def make_array_0(width, height):
    arr=[]
    for y in range(height):
        arr.append([])
        for x in range(width):
            arr[y].append(0)
    return arr
def turn_to_grascale(img):
    """
    Turns img to grayscale
    """
    width, height = img.size
    img_grascale = img.copy()
    img_array = make_array_0(width, height)
    #turn to grascale
    if(img.mode == "RGBA"):
        for y in range(height):
            for x in range(width):
                
                r,g,b,_=img.getpixel((x,y))
                mean = int(0.2989 * r + 0.5870 * g + 0.1140 * b)
                img_grascale.putpixel((x,y),(mean,mean,mean))
                img_array[y][x] = mean
    else:
        for y in range(height):
            for x in range(width):
                r,g,b=img.getpixel((x,y))
                mean = int(0.2989 * r + 0.5870 * g + 0.1140 * b)
                img_grascale.putpixel((x,y),(mean,mean,mean))
                img_array[y][x] = mean
    return img_grascale, img_array
def find_edge_sobel(img, img_array):
    width, height = img.size
    mag = make_array_0(width, height)

    #horizontal and vertical derivative approximations
    Gx = [[-1, 0, 1],[-2, 0, 2], [-1, 0, 1]]
    Gy = [[1, 2, 1], [0, 0, 0], [-1, -2, -1]]

    #applay Sobel operator to the image
    for y in range(1, height - 2):
        for x in range(1, width - 2):

            sumx = 0
            sumy = 0
            for ykernel in range(len(Gx)):
                for xkernel in range(len(Gx[0])):
                    sumx += Gx[ykernel][xkernel] * img_array[y + ykernel][x + xkernel]
            for ykernel in range(len(Gy)):
                for xkernel in range(len(Gy[0])):
                    sumy += Gy[ykernel][xkernel] * img_array[y + ykernel][x + xkernel]


            mag[y][x] = int(math.sqrt(sumx**2 + sumy ** 2))


    return mag
#combine multiple images
def make_multiple_img_into_one(img_arr_original):
    img_arr = []
    for arrays in img_arr_original:
        img_arr.append(arrays[0])
    max_height = 0
    max_width = 0
    for imgs in img_arr:
        width, height = imgs.size
        if(max_width < width):
            max_width = width
        if(max_height < height):
            max_height = height
    img_final = Image.new("RGB", (max_width, max_width), color = (0,0,0))
    for y in range(max_height):
        for x in range(max_height):
            temp_pixel_arr = []
            for imgs in img_arr:
                width, height = imgs.size
                #check to see if the pixel is in the image
                #if((0 < x - (max_width - width)/2 < width) and (0 < y - (max_height - height)/2 < height)):
                if(imgs.mode == "RGB"):
                    r,g,b = imgs.getpixel((x - (max_width - width)/2, y - (max_height - height)/2))
                elif(imgs.mode == "RGBA"):
                    r,g,b,_ = imgs.getpixel((x - (max_width - width)/2, y - (max_height - height)/2))
                temp_pixel_arr.append((r,g,b))
            if(temp_pixel_arr == []):
                img_final.putpixel((x, y), (0,0,0))
            else:
                img_final.putpixel((x, y), random.choice(temp_pixel_arr))
    return img_final, max_width, max_height
def if_two_images(img_arr_original, number_sobel = 80):
    #take two images and take the shape of one with the actual image of the other
    img_arr = [img_arr_original[0][0], img_arr_original[1][0]]
    width = img_arr[0].size[0]
    height = img_arr[0].size[1]
    final_img = Image.new("RGB", (width, height), color = (0,0,0))
    for y in range(height):
        for x in range(width):
            if(img_arr[0].mode == "RGB"):
                r,g,b = img_arr[0].getpixel((x, y))
            elif(img_arr[0].mode == "RGBA"):
                r,g,b,_ = img_arr[0].getpixel((x, y))
            

            if(img_arr_original[0][3][y][x] > number_sobel): #return to 80
                final_img.putpixel((x,y), (r,g,b))
            elif((r,g,b) != (0,0,1)):
                try:
                    if(img_arr[1].mode == "RGB"):
                        r,g,b = img_arr[1].getpixel((x, y))
                    elif(img_arr[1].mode == "RGBA"):
                        r,g,b,_ = img_arr[1].getpixel((x, y))
                    final_img.putpixel((x,y), (r,g,b))
                except Exception as e:
                    print(e)
                    continue
            else:
                final_img.putpixel((x,y), (r,g,b))

    #make the contour clear by adding details of the original img

    

    return final_img, width, height

def display_img(screen, img, x, y):
    #display the img first
    mode = img.mode
    size = img.size
    data = img.tobytes()
    py_image = pygame.image.fromstring(data, size, mode)
    screen.blit(py_image, (x,y))
def brightness(im):
   stat = ImageStat.Stat(im)
   r,g,b = stat.rms
   return int(math.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2)))
def make_pixel_different_brightness(r,g,b,r1,g1,b1):
    if(r * g * b == 0):
        return (0,0,0)
    Y = 0.299*r1 + 0.587*g1 + 0.144*b1
    a = r/b
    c = r/g
    d = b/g
    e = b/r
    r = Y/(0.299 + 0.587/c + 0.144/a)
    b = Y/(0.299/e + 0.587/d + 0.144)
    g = (Y-0.299*r - 0.144 * b)/0.587
    return (int(r),int(g),int(b))
#to make a photomosaics
def make_photomosaics(screen, img, img_arr):
    #display_img(screen, img, 0, 0)
    print("making photomosaic")
    h, w= img.size
    scl = 60
    img_small = img.resize((int(h/scl), int(w/scl)))
    w2, h2 = img_small.size
    brightness_arr = []
    for i in range(len(img_arr)):
        #rezise the img to get smaller and process faster
        img_arr[i] = img_arr[i].resize((scl, scl))

        brightness_arr.append(brightness(img_arr[i]))

    img_final = Image.new("RGB", (h, w), color = (0,0,0))
    for y in range(h2):
        for x in range(w2):
            r,g,b = img_small.getpixel((x,y))
            Y_bright = 0.299 * r + 0.597 * g + 0.114 * b
            record = 256
            best_img = img_arr[0]
            for j in range(len(brightness_arr)):
                if(abs(Y_bright - brightness_arr[j]) < record):
                    record = abs(Y_bright - brightness_arr[j])
                    best_img = img_arr[j]
            for y2 in range(scl):
                for x2 in range(scl):
                    #get rgb of pixel in small image
                    r1,g1,b1 = best_img.getpixel((x2,y2))
                    #get rgb of big image
                    r,g,b = img.getpixel((x*scl + x2, y*scl + y2))
                    #change rgb to new color
                    color_pixel = make_pixel_different_brightness(r,g,b,r1,g1,b1)
                    #apply it big image
                    img_final.putpixel((x*scl+x2,y*scl+y2), color_pixel)
            
    #display_img(screen, img_final, 0, 0)
    #img_final.save("damn{}.jpg".format(random.randint(0, 1000)))
    return img_final
def get_arr_from_google(wd, arr_words):
    num_images_to_search = 0
    urls = []
    img_arr = []
    #get images from google
    for words_to_search in arr_words:
        if(words_to_search[len(words_to_search) - 1] in "0123456789"):
            if(words_to_search[len(words_to_search) - 2: len(words_to_search) - 1] in "0123456789"):
                print(words_to_search, words_to_search[len(words_to_search) - 2: len(words_to_search)])
                num_images_to_search = int(words_to_search[len(words_to_search) - 2: len(words_to_search)])
                words_to_search = words_to_search[0:len(words_to_search) - 2]
            else:
                num_images_to_search = int(words_to_search[len(words_to_search) - 1])
                words_to_search = words_to_search[0:len(words_to_search) - 1]
            print(num_images_to_search)
        else:
            num_images_to_search = 1
        
        urls = get_images_from_google(wd, 0.5, num_images_to_search, words_to_search)
        print("Len ", len(urls))
        print(type(urls))
        
        img_to_add = dowload_img(urls[len(urls) - 1])
        minus_num = 1
        while(img_to_add == None):
            minus_num += 1
            
            img_to_add = dowload_img(urls[len(urls) - minus_num])
            
        img_arr.append([img_to_add])
    return img_arr
def make_img_bigger(img):
    #make img bigger depending on the scale
    print("making image bigger")
    w, h = img.size
    scl = 5
    w2, h2 = w * 5, h * 5
    img_final = Image.new("RGB", (w2, h2), color = (0,0,0))
    for y in range(h):
        for x in range(w):
            color = img.getpixel((x,y))
            for y2 in range(scl):
                for x2 in range(scl):
                    #print(w2, h2, x*scl+x2, y*scl+y2)
                    img_final.putpixel((x*scl+x2, y*scl+y2), color)
    
    return img_final

def main():

    running = True
    black = (0,0,0)
    x = 0
    y = 0
    test_mode = False
    img_array = []

    #if I need to test anything
    if(test_mode):
        pygame.init()
        screen = pygame.display.set_mode([1800, 900])
        pygame.display.set_caption('Make image from google')
        screen.fill(black)
        PATH = "chromedriver.exe"
        wd = webdriver.Chrome(PATH)
        imgs_arr_ = [get_arr_from_google(wd, ["intended", "ivory2", "station2", "river2"])]
        imgs_arr = []
        for y in range(len(imgs_arr_[0])):
            imgs_arr.append(imgs_arr_[0][y][0])
        print(imgs_arr)
        #imgs_arr = [Image.open("imgs/{}".format(f)) for f in listdir("imgs/") if isfile(join("imgs/", f))]
        img_final = make_img_bigger(Image.open("kurtz.jpg"))
        img_final = make_photomosaics(screen, img_final, imgs_arr)
        
        #display_img(screen, img_final, 0, 0)
        #pygame.display.flip()
        img_final.save("damn{}.jpg".format(random.randint(0, 1000)))
        #time.sleep(10)
        exit()
    else:
        answer_valid = False
        while not answer_valid:
            #check if it looks the words up on the internet or just take the pictures from your personal files
            choose_or_not = input("Choose images from Desktop? y/n: ")
            if(choose_or_not == "y"):
                Desktop_look = True
                answer_valid = True
            elif(choose_or_not == "n"):
                Desktop_look = False
                answer_valid = True
            else:
                print("not a valid answer")
        if(not Desktop_look):
            sentence = input("Input the sentence here: ")
            list_of_words_to_delete = ["some", "had","to", "and", "oh", ",", "'", "is", '"', "in", ";", "-", ".", "by", "the", "am", "i", "he", "she", "we", "they", "become", "of", "on", "more", "for"]
            sentence = sentence.lower()
            #delete unecessary words
            PATH = "chromedriver.exe"
            arr_words_ = []
            last_check = 0
            c_check = 0
            for char in sentence:
                if(char == " "):
                    arr_words_.append(sentence[last_check:c_check])
                    last_check = c_check + 1
                c_check += 1
            arr_words_.append(sentence[last_check:len(sentence)])
            main_word = input("main word of the sentence? ")
            no_sobel_word = input("Fill the entire image up or not?")
            if(no_sobel_word == "no"):
                no_sobel = True
                direction_cut = input("A specific way to trim the image? top/bottom/right/left: ").lower()
            else:
                no_sobel = False
                direction_cut = None
            arr_words = []
            for words in arr_words_:
                if(not words in list_of_words_to_delete):
                    if(words == main_word):
                        arr_words.insert(0, words)
                    else:
                        arr_words.append(words)
            #check if you need to do a photomosaic or not
            if(len(arr_words) <= 2):
                two_words = True
            else:
                two_words = False
                second_word = input("second main word? ")
                if not second_word in arr_words:second_word = arr_words[1]
                main_word = arr_words[0]
                arr_words.pop(0)
                arr_words.pop(arr_words.index(second_word))
                arr_word_extra = arr_words
                arr_words = [main_word, second_word]
                print(arr_words)
            wd = webdriver.Chrome(PATH)
            img_arr = get_arr_from_google(wd, arr_words)
        else:
            #Ask the person to choose two images from their personal computer
            root = tkinter.Tk()
            root.withdraw() #use to hide tkinter window
            currdir = os.getcwd()
            tempdir = tkFileDialog.askopenfile(parent=root, initialdir=currdir, title='Please select the first image')
            image_one = Image.open(tempdir.name)
            tempdir = tkFileDialog.askopenfile(parent=root, initialdir=currdir, title='Please select the second image')
            image_two = Image.open(tempdir.name)
            img_arr = [[image_one], [image_two]]
            answer_valid = False
            #check the number of images needed for the photomosaic
            while not answer_valid:
                how_many_images = input("How many images in total? ")
                try:
                    if(how_many_images == ""):
                        how_many_images == 2
                    else:
                        how_many_images = int(how_many_images)
                    answer_valid = True
                except:
                    print("not a valid answer, please input an integer")
            
            if(how_many_images == 2):
                two_words = True
            else: two_words = False
            if(not two_words):
                current_num_index = how_many_images - 2
                img_arr_mosaic = []
                while current_num_index > 0:
                    img_arr_mosaic.append(Image.open(tkFileDialog.askopenfile(parent=root, initialdir=currdir, title='Please select an image', filetypes=[('Image', '*.png *.jpg *')]).name))
                    current_num_index -= 1
            direction_cut = input("A specific way to trim the image? top/bottom/right/left: ").lower() #cut the image in a specific way to add more things we can control 
            if(not direction_cut in ["up", "bottom", "right", "left"]):
                direction_cut = None
            answer_valid = False
            while not answer_valid:
                no_sobel = input("Have the imaged filled but blurred? y/n: ").lower() #have it do the spiral thing or not
                if(no_sobel == "y"):
                    answer_valid = True
                    no_sobel = True
                elif(no_sobel == "n" or  no_sobel == ""):
                    answer_valid = True
                    no_sobel = False
                else:
                    print("Not a valid answer")
            threshold = input("Specific threshold? ")
            try:
                threshold = float(threshold)
                if(threshold > 1):
                    threshold = None
            except:
                threshold = None
    if not Desktop_look and not two_words:
        img_arr_mosaic_ = get_arr_from_google(wd, arr_word_extra)
        img_arr_mosaic = []
        for i in img_arr_mosaic_:
            img_arr_mosaic.append(i[0])
    
    #wd.close()
    
    #convert to rgb
    for i in range(len(img_arr)):
        img_arr[i][0] = img_arr[i][0].convert("RGB")
    image_x_size = 800
    image_y_size = 800
    #rezise image    
    
    #take size of the first img
    size_img = img_arr[0][0].size
    x_trans = int(size_img[0] * image_x_size/size_img[0])
    y_trans = int(size_img[1] * image_x_size/size_img[0])
    if(y_trans > image_y_size):
        temp_y_trans = y_trans
        y_trans = int(y_trans * image_y_size/y_trans)
        x_trans = int(x_trans * image_y_size/temp_y_trans)
    
    #apply that size to all the other images
    for i in range(len(img_arr)):
        img_arr[i][0] = img_arr[i][0].resize((int(x_trans), int(y_trans)))
    print("resize complete")

    #get image grayscale
    for i in range(len(img_arr)):
        img_arr[i].extend(turn_to_grascale(img_arr[i][0]))
    print("grayscale complete")
    
    #apply sobel operator
    img_arr[0].append(find_edge_sobel(img_arr[0][0], img_arr[0][2]))
    
    print("sobel operator complete")
    if(threshold == None):
        threshold = 0.30
    img_arr[0].append(img_arr[0][0].copy())
    img_arr[0][0] = cut_img(img_arr[0][0], img_arr[0][3], threshold, direction_cut)
    if(not no_sobel):
        X = x_trans + 200
        Y = y_trans + 200
    else:
        X = x_trans
        Y = y_trans
    #put + 200 here ^^
    #city4 sepulchralbackfromthedead

    #init everything
    pygame.init()
    screen = pygame.display.set_mode([X, Y])
    pygame.display.set_caption('Make image from google')
    screen.fill(black)
    img_final = Image.new("RGB", (X, Y), color = (0,0,1))


    spiral_arr = spiral(X, Y)
    #find a way to merge the images
    img_to_paste, width1, height1 = if_two_images(img_arr)
    general_color = get_general_img_color(img_to_paste, height1, width1)
    img_final.paste(img_to_paste, (int(X/2 - width1/2), int((Y/2 - height1/2))))
    index_i = 0
    
    #display the img first
    mode = img_final.mode
    size = img_final.size
    data = img_final.tobytes()
    py_image = pygame.image.fromstring(data, size, mode)
    screen.blit(py_image, (0,0))
    pygame.display.flip()
    threshold_textbox = co.text_box(X-200, 20, 100, 50)
    threshold_picture = co.text_box(X - 200, 80, 100, 50)
    threshold_textbox.text = "0.30"
    threshold_picture.text = "80"
    #button to apply that threshold
    button_done = co.button(X-200, 150, 100, 50, "Done")
    button_next = co.button(X-200, Y - 100, 100, 50, "Next")
    #make the textbox and submit button for the threshold
    while running:
        screen.fill((0,0,0))
        screen.blit(py_image, (0,0))
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render("threshold", True, (255, 255, 255), (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (X - 300, 45)
        screen.blit(text, textRect)
        text = font.render("Opacity", True, (255, 255, 255), (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (X - 300, 105)
        screen.blit(text, textRect)
        button_done.draw(screen)
        button_next.draw(screen)
        threshold_textbox.draw(screen)
        threshold_picture.draw(screen)

        pygame.display.flip()
        for event in pygame.event.get():
            #close when x is pressed
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                #if q is hit
                if(not threshold_textbox.typing and not threshold_picture.typing):
                    if event.key == pygame.K_q:
                        running = False
                else:
                    if(event.key == pygame.K_RETURN):
                        threshold = float(threshold_textbox.text)
                        img_arr[0][0] = img_arr[0][4].copy()
                        img_arr[0][0] = cut_img(img_arr[0][0], img_arr[0][3], threshold, direction_cut)
                        img_to_paste, width1, height1 = if_two_images(img_arr, int(threshold_picture.text))
                        general_color = get_general_img_color(img_to_paste, height1, width1)
                        img_final.paste(img_to_paste, (int(X/2 - width1/2), int((Y/2 - height1/2))))
                        mode = img_final.mode
                        size = img_final.size
                        data = img_final.tobytes()
                        py_image = pygame.image.fromstring(data, size, mode)
                    #do textbox for threshold                    
                    elif(event.key == pygame.K_BACKSPACE):
                        if(len(threshold_textbox.text) > 2 and threshold_textbox.typing):
                            threshold_textbox.text = threshold_textbox.text[0:len(threshold_textbox.text) - 1]
                        if(len(threshold_picture.text) > 0 and threshold_picture.typing):
                            threshold_picture.text = threshold_picture.text[0:len(threshold_picture.text) - 1]
                    else:
                        if(str(pygame.key.name(event.key)) in "0123456789." and threshold_textbox.typing):
                            threshold_textbox.text += pygame.key.name(event.key)
                        if(str(pygame.key.name(event.key)) in "0123456789" and threshold_picture.typing):
                            threshold_picture.text += pygame.key.name(event.key)

            pos = pygame.mouse.get_pos()
            if(button_done.collision_with_mouse(pos[0], pos[1])):
                button_done.hover = True
            else:
                button_done.hover = False
            

            if(button_next.collision_with_mouse(pos[0], pos[1])):
                button_next.hover = True
            else:
                button_next.hover = False
            if event.type == pygame.MOUSEBUTTONUP:
                if(threshold_textbox.collision_with_mouse(pos[0], pos[1])):
                    threshold_textbox.typing = True
                else:
                    threshold_textbox.typing = False
                
                if(threshold_picture.collision_with_mouse(pos[0], pos[1])):
                    threshold_picture.typing = True
                else:
                    threshold_picture.typing = False
                
                if(button_done.collision_with_mouse(pos[0], pos[1])):
                    threshold = float(threshold_textbox.text)
                    img_arr[0][0] = img_arr[0][4].copy()
                    img_arr[0][0] = cut_img(img_arr[0][0], img_arr[0][3], threshold, direction_cut)
                    img_to_paste, width1, height1 = if_two_images(img_arr, int(threshold_picture.text))
                    general_color = get_general_img_color(img_to_paste, height1, width1)
                    img_final.paste(img_to_paste, (int(X/2 - width1/2), int((Y/2 - height1/2))))
                    mode = img_final.mode
                    size = img_final.size
                    data = img_final.tobytes()
                    py_image = pygame.image.fromstring(data, size, mode)

                if(button_next.collision_with_mouse(pos[0], pos[1])):
                    running = False

    running = True
    while index_i < X * Y and running and not no_sobel:
        #do the spiral thing to fill the black spots
        img_final = expand(img_final, int(X/2 + spiral_arr[index_i][0]), int(Y/2 + spiral_arr[index_i][1]), 2, general_color)
        #display final image
        if(index_i % 2000 == 0):
            mode = img_final.mode
            size = img_final.size
            data = img_final.tobytes()
            py_image = pygame.image.fromstring(data, size, mode)
            screen.blit(py_image, (0,0))
            pygame.display.flip()
        for event in pygame.event.get():
            #close when x is pressed
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                #if q is hit
                if event.key == pygame.K_q:
                    running = False
        index_i += 1
    #make the photo mosaic
    if not two_words:
        #make img bigger by 5 times
        img_final = make_img_bigger(img_final)
        img_final = make_photomosaics(screen, img_final, img_arr_mosaic)
        w, h = img_final.size
        display_img(screen, img_final.resize((int(w/5), int(h/5))), 0, 0)
    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            #close when x is pressed
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                #if q is hit
                if event.key == pygame.K_q:
                    running = False
                if event.key == pygame.K_s:
                    name_of_file = input("What would you like to name the file? ")
                    img_final.save("imgs/{}.jpg".format(name_of_file))
        pygame.display.flip()
    if(not test_mode):
        wd.quit()


if __name__ == "__main__": main()