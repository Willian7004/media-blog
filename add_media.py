'''
写一个python程序，实现以下功能：
1.当前目录下articles文件夹中有多个包含.md文件的文件夹。当前目录下files文件夹中有与.md文件路径对应的包含图片、视频或音频的文件夹。
2.把文件夹中的图片、视频或音频文件添加到对应的.md文件，图片使用markdown语法，但 宽度<高度 的图片使用html添加，宽度500像素，居中显示，每行2张图。音频和视频使用html添加。如果.md文件已有重复内容则不添加。添加时把路径转换为 https://github.com/Willian7004/media-blog 仓库中的相应路径并使用raw=true 加载文件。
'''
import os
from PIL import Image
from PIL import UnidentifiedImageError

def get_image_size(filepath):
    try:
        with Image.open(filepath) as img:
            return img.size  # (width, height)
    except (IOError, OSError, UnidentifiedImageError):
        return None

def generate_content_blocks(media_dir):
    image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    video_exts = {'.mp4', '.mov', '.avi', '.mkv'}
    audio_exts = {'.mp3', '.wav', '.ogg'}
    
    content_blocks = []
    portrait_images = []
    landscape_images = []
    videos = []
    audios = []

    # Collect and classify media files
    for entry in os.scandir(media_dir):
        if not entry.is_file():
            continue
            
        filepath = entry.path
        filename = entry.name
        ext = os.path.splitext(filename)[1].lower()
        
        # Generate GitHub URL
        rel_path = os.path.relpath(filepath, 'files').replace('\\', '/')
        url = f'https://github.com/Willian7004/media-blog/blob/main/files/{rel_path}?raw=true'

        if ext in image_exts:
            size = get_image_size(filepath)
            if not size:
                continue
                
            width, height = size
            if width < height:
                portrait_images.append(url)
            else:
                landscape_images.append((url, filename))
                
        elif ext in video_exts:
            videos.append(url)
        elif ext in audio_exts:
            audios.append(url)

    # Process portrait images (vertical)
    for i in range(0, len(portrait_images), 2):
        group = portrait_images[i:i+2]
        imgs = [f'<img src="{url}" style="width:500px;" />' for url in group]
        div_html = f'<div style="display: flex; justify-content: center; gap: 10px; margin: 10px 0;">\n' + '\n'.join(imgs) + '\n</div>'
        content_blocks.append(div_html)

    # Process landscape images (horizontal)
    for url, filename in landscape_images:
        content_blocks.append(f'![{filename}]({url})')

    # Process videos
    for url in videos:
        content_blocks.append(f'<video src="{url}" controls style="max-width: 100%;"></video>')

    # Process audios
    for url in audios:
        content_blocks.append(f'<audio src="{url}" controls></audio>')

    return content_blocks

def main():
    for root, dirs, files in os.walk('articles'):
        for file in files:
            if not file.endswith('.md'):
                continue
                
            md_path = os.path.join(root, file)
            
            # Get corresponding media directory
            rel_path = os.path.relpath(md_path, 'articles')
            base_name = os.path.splitext(rel_path)[0]
            media_dir = os.path.join('files', base_name)
            
            if not os.path.exists(media_dir):
                continue

            # Generate content blocks
            content_blocks = generate_content_blocks(media_dir)
            if not content_blocks:
                continue

            # Read existing content
            with open(md_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()

            # Filter new content
            new_content = []
            for block in content_blocks:
                if block not in existing_content:
                    new_content.append(block)

            # Append new content
            if new_content:
                with open(md_path, 'a', encoding='utf-8') as f:
                    f.write('\n\n' + '\n\n'.join(new_content))

if __name__ == '__main__':
    main()
