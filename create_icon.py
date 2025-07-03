from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # 創建 256x256 的圖示
    size = 256
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 繪製圓角矩形背景
    margin = 20
    draw.rounded_rectangle(
        [margin, margin, size-margin, size-margin],
        radius=30,
        fill=(108, 117, 125, 255)
    )
    
    # 繪製勾選框
    box_size = 80
    box_x = (size - box_size) // 2
    box_y = (size - box_size) // 2 - 20
    
    # 外框
    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_size, box_y + box_size],
        radius=8,
        outline=(255, 255, 255, 255),
        width=4
    )
    
    # 勾選記號
    check_points = [
        (box_x + 20, box_y + 40),
        (box_x + 35, box_y + 55),
        (box_x + 60, box_y + 25)
    ]
    draw.line(check_points, fill=(255, 255, 255, 255), width=6)
    
    # 儲存為 ICO 檔案
    img.save('icon.ico', format='ICO', sizes=[(256, 256)])

if __name__ == "__main__":
    create_icon() 