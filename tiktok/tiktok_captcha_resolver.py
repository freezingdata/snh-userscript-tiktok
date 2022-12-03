# Python program to read an write an image
import sys; sys.path.insert(0, r"C:\Users\umpan\AppData\Roaming\Python\Python39\site-packages")
import math
from PIL import Image
import requests
from io import BytesIO


from snhwalker_utils import snhwalker, snh_major_version, snh_account_manager
import snhwalker_utils

class TiktokCaptchaDetector:
    def __init__(self):
        pass

    def captcha_visible(self):
        return snhwalker_utils.snh_browser.GetJavascriptInteger('document.querySelectorAll(".captcha_verify_container").length') > 0 

class TiktokCaptchaResolver:
    def __init__(self, max_attemps):
        self.max_attemps = max_attemps
        self.run()


    def sort_helper(self, elem):
        return elem[1]

    def get_circle_pos(self, winkel, radius, middle):
        X1 = int(radius * math.cos(winkel)) + middle
        Y1 = int(radius * math.sin(winkel)) + middle
        return X1, Y1    

    def draw_circle_pixel(self, img, winkel, radius, middle):
        X1 = int(radius * math.cos(winkel)) + middle
        Y1 = int(radius * math.sin(winkel)) + middle

        img.putpixel((X1,Y1), (255,0,0))

    def apply_result(self, captcha_result):
        movex = abs(269/365*(365 - captcha_result[0]))
        js = """
        slider_x = document.querySelector(".secsdk-captcha-drag-sliding").getBoundingClientRect().left;
        slider_y = document.querySelector(".secsdk-captcha-drag-sliding").getBoundingClientRect().top;
        document.querySelector('.secsdk-captcha-drag-sliding').dispatchEvent(new MouseEvent("mousedown",{clientX: slider_x+20,clientY: slider_y+20,bubbles: true}));
        """
        snhwalker_utils.snh_browser.ExecuteJavascript(js)
        snhwalker_utils.snh_browser.WaitMS(3000)

        for pos in range(int(movex)):
            if (pos % 10 == 0):
                js = """
                slider_x = document.querySelector(".secsdk-captcha-drag-sliding").getBoundingClientRect().left;
                slider_y = document.querySelector(".secsdk-captcha-drag-sliding").getBoundingClientRect().top;
                document.querySelector('.secsdk-captcha-drag-sliding').dispatchEvent(new MouseEvent("mousemove",{clientX: slider_x+20+"""+str(10) + """,clientY: slider_y+10,bubbles: true}));
                """
                snhwalker_utils.snh_browser.ExecuteJavascript(js)
                snhwalker_utils.snh_browser.WaitMS(50)
        
        js = """        
        slider_x = document.querySelector(".secsdk-captcha-drag-sliding").getBoundingClientRect().left;
        slider_y = document.querySelector(".secsdk-captcha-drag-sliding").getBoundingClientRect().top;
        document.querySelector('.secsdk-captcha-drag-sliding').dispatchEvent(new MouseEvent("mouseup",{clientX: slider_x+100,clientY: slider_y+10,bubbles: true}));
        """
        snhwalker_utils.snh_browser.ExecuteJavascript(js)

    def solve_capture(self):
        self.load_captcha_images()
        snhwalker_utils.snh_browser.WaitMS(1000)    
        pixel_compare = []

        for roation_winkel in range(255):
            img_innen_rgb = self.img_innen.rotate(roation_winkel).convert('RGB')
            img_aussen_rgb = self.img_aussen.convert('RGB')    
            abweichung = 0
            for alpha in range(255):
                x_innen, y_innen = self.get_circle_pos(alpha, 105, 105)
                x_aussen, y_aussen = self.get_circle_pos(alpha, 107, 173)
                r_i, g_i, b_i = img_innen_rgb.getpixel((x_innen, y_innen) )
                r_a, g_a, b_a = img_aussen_rgb.getpixel((x_aussen, y_aussen ))
                cValue = (abs(r_i-r_a) + abs(g_i-g_a) + abs(b_i-b_a)) / 3
                abweichung += cValue                
            pixel_compare.append((roation_winkel, abs(abweichung/255)))

        pixel_compare.sort(key=self.sort_helper)
        #print(f"Rotation detected: {pixel_compare[0]}")
        self.apply_result(pixel_compare[0])        

    def load_captcha_images(self):
        self.url_in = snhwalker_utils.snh_browser.GetJavascriptString('document.querySelectorAll(".captcha_verify_container img")[0].src')
        self.url_out = snhwalker_utils.snh_browser.GetJavascriptString('document.querySelectorAll(".captcha_verify_container img")[1].src')  
        response = requests.get(self.url_in)
        self.img_aussen = Image.open(BytesIO(response.content))
        response = requests.get(self.url_out)
        self.img_innen = Image.open(BytesIO(response.content))          

    def run(self):
        if TiktokCaptchaDetector().captcha_visible() is False:
            return
        print("[TikTok] Captcha Resolver")
        attempt_count = 0
        while (TiktokCaptchaDetector().captcha_visible() is True) and (attempt_count < self.max_attemps ): 
            attempt_count += 1       
            print(f"Captcha request found. Try to solve it. Attempt {attempt_count} ...")
           
            
            try:
                self.solve_capture()
            except Exception as e:
                print("[ERROR] Unexpected error")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(e, exc_type, exc_tb.tb_lineno)
            snhwalker_utils.snh_browser.WaitMS(3000)

        if TiktokCaptchaDetector().captcha_visible() is False:
            print("[TikTok] Captcha successfully resolved.")   
        else:
            print("[TikTok] Failed to resolve captcha")    
            
