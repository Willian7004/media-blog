'''
写一个python程序，实现以下功能：
1.当前目录下articles文件夹中有多个包含.md文件的文件夹。当前目录下files文件夹中有与.md文件路径对应的包含图片、视频或音频的文件夹。
2.把文件夹中的图片、视频或音频文件添加到对应的.md文件，图片使用markdown语法，但 宽度<高度 的图片使用html添加，宽度500像素，居中显示，每行2张图。音频和视频使用html添加。如果.md文件已有重复内容则不添加。添加时把路径转换为 https://github.com/Willian7004/media-blog 仓库中的相应路径并使用raw=true 加载文件。
'''
import os
from PIL import Image

def process_articles():
    # 遍历articles目录中的所有.md文件
    for root, dirs, files in os.walk('articles'):
        for file in files:
            if not file.lower().endswith('.md'):
                continue
            
            md_path = os.path.join(root, file)
            
            # 构建对应的files目录路径
            relative_md = os.path.relpath(md_path, 'articles')
            media_folder = os.path.splitext(relative_md)[0]
            media_dir = os.path.join('files', media_folder)
            
            if not os.path.exists(media_dir):
                continue
            
            # 读取.md文件内容
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            vertical_images = []
            new_content = []
            
            # 处理媒体文件
            for media_file in sorted(os.listdir(media_dir)):
                media_path = os.path.join(media_dir, media_file)
                if not os.path.isfile(media_path):
                    continue
                
                # 生成GitHub URL
                relative_path = os.path.relpath(media_path, 'files')
                github_url = (
                    "https://github.com/Willian7004/media-blog/blob/main/"
                    f"{relative_path.replace(os.sep, '/')}?raw=true"
                )
                
                # 跳过已存在的内容
                if github_url in content:
                    continue
                
                # 根据文件类型处理
                ext = os.path.splitext(media_file)[1].lower()
                
                # 处理图片
                if ext in {'.jpg', '.jpeg', '.png', '.gif'}:
                    try:
                        with Image.open(media_path) as img:
                            width, height = img.size
                    except:
                        continue
                    
                    if width < height:
                        vertical_images.append(github_url)
                    else:
                        new_content.append(f"![{media_file}]({github_url})")
                
                # 处理视频
                elif ext in {'.mp4', '.mov', '.avi', '.webm'}:
                    new_content.append(
                        f'<video src="{github_url}" controls style="'
                        'display: block; margin: 20px auto; width: 500px;"></video>'
                    )
                
                # 处理音频
                elif ext in {'.mp3', '.wav', '.ogg'}:
                    new_content.append(
                        f'<audio src="{github_url}" controls style="'
                        'display: block; margin: 20px auto;"></audio>'
                    )
            
            # 处理竖版图片分组
            for i in range(0, len(vertical_images), 2):
                group = vertical_images[i:i+2]
                imgs = [f'<img src="{url}" width="500" style="display: inline-block;">' 
                       for url in group]
                new_content.append(
                    f'<div style="text-align: center;">\n' +
                    '\n'.join(imgs) +
                    '\n</div>'
                )
            
            # 追加新内容到文件
            if new_content:
                with open(md_path, 'a', encoding='utf-8') as f:
                    f.write('\n\n' + '\n\n'.join(new_content))

if __name__ == '__main__':
    process_articles()