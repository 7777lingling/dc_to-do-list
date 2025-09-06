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

def convert_png_to_ico(png_file, output_file='icon.ico'):
    """
    將 PNG 圖片轉換為 ICO 格式
    """
    try:
        # 開啟 PNG 圖片
        img = Image.open(png_file)
        
        # 轉換為 RGBA 模式（支援透明背景）
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # 調整大小為 256x256（ICO 格式的標準大小）
        img = img.resize((256, 256), Image.Resampling.LANCZOS)
        
        # 儲存為 ICO 檔案，包含多種尺寸
        img.save(output_file, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        
        print(f"成功將 {png_file} 轉換為 {output_file}")
        return True
        
    except Exception as e:
        print(f"轉換失敗：{e}")
        return False

if __name__ == "__main__":
    # 檢查是否有 PNG 檔案
    png_files = [f for f in os.listdir('.') if f.lower().endswith('.png')]
    
    if png_files:
        print(f"找到 PNG 檔案：{png_files}")
        # 使用第一個找到的 PNG 檔案
        convert_png_to_ico(png_files[0])
    else:
        print("未找到 PNG 檔案，使用預設圖示")
        create_icon() 