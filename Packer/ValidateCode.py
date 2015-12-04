#!/usr/bin/env python
# encoding: utf-8

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random, string

_lower_cases = 'abcdefghkjmnpqrstuvwxy'
_upper_cases = _lower_cases.upper()
_numbers = ''.join(map(str, range(3, 10)))
init_chars = ''.join((_lower_cases, _upper_cases,  _numbers))

def generateCode(size=(120, 30), chars=init_chars, length=4, img_type='GIF',
        mode='RGB', bg_color=(255, 255, 255), fg_color=(0, 0, 0),
        font_size=22, font_type='st.ttf', draw_lines=True, n_lines=3, draw_points=True, point_chance=3):
    width, height = size
    im = Image.new(mode, size, bg_color)
    draw = ImageDraw.Draw(im)

    def get_chars():
        ''' 生成随机验证码字符串 '''
        return ''.join(random.choice(chars) for _ in range(length))

    random_strs = get_chars()

    def create_lines():
        ''' 绘制干扰线 '''
        for i in range(n_lines):
            begin = (random.randint(0, width), random.randint(0, height))
            end = (random.randint(0, width), random.randint(0, height))
            draw.line([begin, end], fill=(random.randint(0, 255),
                                          random.randint(0, 255),
                                          random.randint(0, 255)))

    def create_points():
        ''' 绘制干扰点 '''
        chance = min(100, max(0, int(point_chance)))
        for x in xrange(width):
            for y in xrange(height):
                tmp = random.randint(0, 100)
                if tmp > 100 - chance:
                    draw.point((x, y), fill=(random.randint(0, 255),
                                             random.randint(0, 255),
                                             random.randint(0, 255)))

    def create_str():
        ''' 绘制字符串 '''
        font = ImageFont.truetype(font_type, font_size)
        font_width, font_height = font.getsize(random_strs)
        draw.text((random.randint(10, max((width - font_width - 30), 30)),
                   random.randint(0, max((height - font_height - 10), 10))),
                   random_strs, font=font, fill=fg_color)

    if draw_lines:
        create_lines()
    if draw_points:
        create_points()
    create_str()
    # 图形扭曲
    params = [1 - float(random.randint(1, 2)) / 300,
              0,
              0,
              0,
              1 - float(random.randint(1, 10)) / 300,
              float(random.randint(1, 2)) / 500,
              0.001,
              float(random.randint(1, 2)) / 500]
    im = im.transform(size, Image.PERSPECTIVE, params)
    im = im.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return random_strs, im

if __name__ == '__main__':
    code = generateCode()
    print '字符串：' + code[0]
    code[1].save('t.jpg')



