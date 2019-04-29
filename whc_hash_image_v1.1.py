# 该修改图片hash值脚本请使用python3运行，并且需要安装依赖库Pillow，执行命令：pip3 install Pillow即可

from PIL import Image
from multiprocessing import Pool, Lock
from PIL import ImageFile
import random
import os
import types

ImageFile.LOAD_TRUNCATED_IMAGES = True
lock = Lock()
SUFFIXES = {1000: ['KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],
    1024: ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']}

class ChangeImageColor(object):

    quality = 100
    ischangeColor = 'y'

    @classmethod
    def image_size(self, size):
        if size < 0:
            return '0KiB'

        multiple = 1024
        for suffix in SUFFIXES[multiple]:
            size /= multiple
            if size < multiple:
                return  '{0:.1f} {1}'.format(size, suffix)
        
        return '0KiB'

    @classmethod
    def file_extension(self, path):
        return os.path.splitext(path)[1].lower()

    @classmethod
    def file_name(self, name):
        return os.path.splitext(name)[0]

    @classmethod
    def multiProcessExce(self, files, root, dirs, isorigin, path):
        imageCount = 0
        imageSumSize = 0
        for file_name in files:
            if file_name != '.DS_Store' and (ChangeImageColor.file_extension(file_name) == '.png' or ChangeImageColor.file_extension(file_name) == '.jpg' or ChangeImageColor.file_extension(file_name) == '.jpeg'):
                imagePath = root + '/' + file_name
                try:
                    image = Image.open(imagePath)
                    if image is not None:
                        imageCount += 1
                        imageSumSize += os.path.getsize(imagePath)
                        print('name: ' + file_name + ' ------- 大小：' +  self.image_size(imageSumSize))
                        if image.mode != 'RGB':
                            image = image.convert('RGBA')
                        image_width, image_height = image.size
                        newImage = Image.new(image.mode, (image_width, image_height))
                        for i in range(image_width):
                            for j in range(image_height):
                                xy = (i,j)
                                color = image.getpixel(xy)
                                if not isinstance(color,int):
                                    color_num = len(color)
                                    r_num = random.randint(1,12)
                                    g_num = random.randint(1,12)
                                    b_num = random.randint(1,12)
                                    if color_num == 4:
                                        r, g, b, a = color
                                        if a >= 0.1:
                                            if self.ischangeColor == 'y':
                                                if r + r_num > 255:
                                                    r = r - r_num
                                                else:
                                                    r = r + r_num

                                                if g + g_num > 255:
                                                    g = g - g_num
                                                else:
                                                    g = g + g_num

                                                if b + b_num > 255:
                                                    b = b - b_num
                                                else:
                                                    b = b + b_num
                                                newImage.putpixel(xy, (r, g, b, a))
                                            else:
                                                newImage.putpixel(xy, (r, g, b, a))
                                    elif color_num == 3:
                                        r, g, b = color
                                        if self.ischangeColor == 'y':
                                            if r + r_num > 255:
                                                r = r - r_num
                                            else:
                                                r = r + r_num

                                            if g + g_num > 255:
                                                g = g - g_num
                                            else:
                                                g = g + g_num

                                            if b + b_num > 255:
                                                b = b - b_num
                                            else:
                                                b = b + b_num
                                            newImage.putpixel(xy, (r, g, b))
                                        else:
                                            newImage.putpixel(xy, (r, g, b))
                                    else:
                                        newImage.putpixel(xy, color)
                                else:
                                    newImage.putpixel(xy,color)
                        if isorigin:
                            os.remove(root + '/' + file_name)
                            newImage.save(root + '/' + file_name, 'PNG', quality = self.quality)
                        else:
                            newImage.save(path + ChangeImageColor.file_name(file_name) + '.png', 'PNG', quality = self.quality)
                    else:
                        print('不存在路径：' + imagePath)
                except ZeroDivisionError as e:
                    print('except:', e)
                    continue
        return (imageCount, imageSumSize)


    @classmethod
    def startHandle(self, path, isorigin = False):
        walks = os.walk(path)
        walks_len = len(list(walks))
        max_process = min(20, walks_len)
        print('总共开启' + str(max_process) + '个进程进行图片像素处理')
        pool = Pool(processes=max_process)
        sum_count = 0
        sum_size = 0
        results = []
        for root, dirs, files in os.walk(path):
            result = pool.apply_async(self.multiProcessExce, args=(files, root, dirs, isorigin, path))
            results.append(result)
        for result in results:
            imageCount, imageSumSize = result.get()
            sum_count += imageCount
            sum_size += imageSumSize
        pool.close()
        pool.join()
        print('所有图片总大小：' + str(self.image_size(sum_size)))
        print('总共处理图片数量：' + str(sum_count))

    @classmethod
    def hex2rgb(self, hexcolor):
        rgb = ((hexcolor >> 16) & 0xff,
               (hexcolor >> 8) & 0xff,
               hexcolor & 0xff
               )
        return rgb

if __name__ == '__main__':
    path = input('请输入图片目录根路径:')
    if path == '':
        print('请输入有效目录地址')
    else:
        imageCount = 0
        ChangeImageColor.quality = random.randint(6,70)
        ChangeImageColor.startHandle(path.strip(), True)
        print('复制所有图片完成')
