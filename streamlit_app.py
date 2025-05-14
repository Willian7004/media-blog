'''
写一个streamlit程序，实现以下功能：
1.当前目录下articles文件夹中有多个包含.md文件的文件夹，文件夹命名包含年、月（例如2025年5月对应的文件夹命名为202505），文件命名依次包含年、月、日和序号（例如2025年5月5日第一篇名称为2025050501）。.md文件内容第一行为标题。当前目录下files文件夹中有与.md文件路径对应的文件夹。
2.在侧边栏创建下拉菜单、输入框和两个复选框。下拉菜单用于选择月份对应的文件夹，较新的排在前面，第一个选项为“全部”，用于选择所有文件夹。在输入框输入文字筛选标题包含特定关键词的文件，通过空格输入多个关键词以筛选同时包含所有关键词的文件。第一个复选框文字为“全文搜索”，选中后搜索文件全文。第二个复选框文字为“显示下载按钮”，选中后在页面上的图片下方添加下载按钮用于下载对应图片。
3.在侧边栏创建单选按钮文字为文件标题，用于选中对应文件。新的文件显示在上方。在每个日期的文件上方添加一个文字为对应日期的选项，用于选中相应日期的最新文件。
4.选中文件后在页面上使用st.markdown显示对应的文件内容（包括标题）,排除图片和html内容。在下方按文件名顺序加载与.md文件对应的文件夹中的图片、视频和音频文件，其中视频设为自动播放、循环播放。

更新：
修改以上程序，在页面上显示图片时，分三列显示 宽度<高度 的图片，分两列显示 宽度=高度 的图片，其它的不分列显示。
'''

import streamlit as st
import os

st.set_page_config(layout="wide")
with st.expander("项目说明"):
    filepath='README.md'
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        st.markdown(content)
st.sidebar.title("Media Blog")

import re
from datetime import datetime
from PIL import Image

def get_month_folders():
    """获取所有符合格式的月份文件夹"""
    articles_dir = 'articles'
    folders = []
    if not os.path.exists(articles_dir):
        return []
    for d in os.listdir(articles_dir):
        path = os.path.join(articles_dir, d)
        if os.path.isdir(path) and re.match(r'\d{6}', d):
            folders.append(d)
    return sorted(folders, reverse=True)

def parse_article_files(month_folder, keywords, full_text_search):
    """解析指定月份下的所有文章文件"""
    articles_dir = 'articles'
    month_path = os.path.join(articles_dir, month_folder)
    files = []
    
    for md_file in os.listdir(month_path):
        if not md_file.endswith('.md'):
            continue
            
        file_path = os.path.join(month_path, md_file)
        prefix = md_file[:10] if len(md_file) >= 12 else md_file.split('.')[0]
        
        if not re.match(r'\d{8}\d*', prefix):
            continue
            
        try:
            date = datetime.strptime(prefix[:8], "%Y%m%d").date()
        except ValueError:
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 提取标题
        first_line = content.split('\n', 1)[0]
        title = re.sub(r'^\s*##\s*', '', first_line).strip()
        
        # 关键词过滤
        if keywords:
            search_text = content if full_text_search else title
            if not all(kw.lower() in search_text.lower() for kw in keywords):
                continue
                
        files.append({
            'title': title,
            'date': date,
            'path': file_path,
            'prefix': prefix,
            'content': content,
            'filename': md_file
        })
    
    # 按日期和序号排序
    return sorted(files, key=lambda x: (x['date'], x['prefix']), reverse=True)

def extract_content(content):
    """提取并清理markdown内容"""
    # 移除标准Markdown图片语法 ![alt](url)
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content, flags=re.DOTALL)
    # 移除HTML图片、视频、音频标签 <img>
    content = re.sub(r'<img\s+.*?>', '', content, flags=re.DOTALL)
    content = re.sub(r'<video\s+.*?>', '', content, flags=re.DOTALL)
    content = re.sub(r'<audio\s+.*?>', '', content, flags=re.DOTALL)
    return content

def main():
    
    # 月份选择
    month_folders = get_month_folders()
    selected_month = st.sidebar.selectbox("选择月份", ['全部'] + month_folders)
    
    # 关键词搜索
    keyword_input = st.sidebar.text_input("关键词搜索（空格分隔）", "")
    keywords = [k.strip() for k in keyword_input.split() if k.strip()]
    
    # 搜索选项
    full_text_search = st.sidebar.checkbox("全文搜索")
    show_download = st.sidebar.checkbox("显示下载按钮")
    
    # 收集所有符合条件的文件
    all_files = []
    if selected_month == '全部':
        for month in month_folders:
            all_files.extend(parse_article_files(month, keywords, full_text_search))
    else:
        all_files = parse_article_files(selected_month, keywords, full_text_search)
    
    if not all_files:
        st.warning("没有找到符合条件的文件")
        return

    # 按日期分组
    files_by_date = {}
    for file in all_files:
        date_key = file['date'].strftime("%Y-%m-%d")
        if date_key not in files_by_date:
            files_by_date[date_key] = []
        files_by_date[date_key].append(file)
    sorted_dates = sorted(files_by_date.keys(), reverse=True)
    
    # 构建侧边栏选项
    sidebar_options = []
    option_to_file = {}
    
    for date_key in sorted_dates:
        date_files = files_by_date[date_key]
        # 日期选项
        date_option = f"📅 {date_key}"
        sidebar_options.append(date_option)
        option_to_file[date_option] = date_files[0]  # 最新文件
        
        # 文件标题选项
        for file in date_files:
            file_option = f"📄 {file['title']}"
            sidebar_options.append(file_option)
            option_to_file[file_option] = file
    
    # 侧边栏单选按钮
    selected_sidebar = st.sidebar.radio("选择文件", sidebar_options)
    
    # 获取选中文件
    selected_file = option_to_file.get(selected_sidebar)
    if not selected_file:
        st.warning("请选择一个文件")
        return
    
    # 显示文档内容
    cleaned_content = extract_content(selected_file['content'])
    st.markdown(cleaned_content)
    
   # 显示媒体文件
    media_folder = selected_file['path'].replace('articles', 'files', 1).rsplit('.', 1)[0]
    
    if os.path.exists(media_folder) and os.path.isdir(media_folder):
        media_files = sorted(os.listdir(media_folder))
        
        # 初始化列状态变量
        current_col_type = None
        current_columns = None
        current_col_index = 0

        for media_file in media_files:
            file_path = os.path.join(media_folder, media_file)
            ext = media_file.split('.')[-1].lower()
            
            try:
                if ext in ['png', 'jpg', 'jpeg', 'gif']:
                    # 获取图片尺寸
                    try:
                        with Image.open(file_path) as img:
                            width, height = img.size
                    except Exception as e:
                        st.error(f"无法读取图片尺寸：{media_file} - {str(e)}")
                        continue

                    # 判断列类型
                    if width < height:
                        col_type = 3
                    elif width == height:
                        col_type = 2
                    else:
                        col_type = 1

                    # 分列显示逻辑
                    if col_type in [3, 2]:
                        if current_col_type != col_type or current_col_index >= col_type:
                            current_columns = st.columns(col_type)
                            current_col_type = col_type
                            current_col_index = 0
                        
                        with current_columns[current_col_index]:
                            st.image(file_path)
                            if show_download:
                                with open(file_path, "rb") as f:
                                    st.download_button(
                                        label=f"下载",
                                        data=f.read(),
                                        file_name=media_file,
                                        mime=f"image/{ext}",
                                        key=f"img_{media_file}_{current_col_index}"
                                    )
                        current_col_index += 1
                    else:
                        # 单列显示
                        st.image(file_path)
                        if show_download:
                            with open(file_path, "rb") as f:
                                st.download_button(
                                    label=f"下载",
                                    data=f.read(),
                                    file_name=media_file,
                                    mime=f"image/{ext}",
                                    key=f"img_{media_file}"
                                )
                        # 重置列状态
                        current_col_type = None
                        current_columns = None
                        current_col_index = 0

                elif ext in ['mp4', 'webm']:
                    st.video(file_path, autoplay=True, loop=True, muted=True)
                elif ext in ['mp3', 'wav']:
                    st.audio(file_path)
            except Exception as e:
                st.error(f"无法加载文件 {media_file}: {str(e)}")
    else:
        st.info("没有找到对应的媒体文件夹")

if __name__ == "__main__":
    main()