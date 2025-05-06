# Media Blog

### 项目说明

##### 创建原因

我的new-blog项目转向了markdown形式，文字内容方便编写但图片内容添加流程复杂。另外，图片较多时可能因为超出访问频率限制无法在GitHub外加载图片。因此本项目改为直接在Streamlit读取图片。

图片加载上，本项目直接使用与文章同名的文件夹保存和加载文件，简化了编写流程但排版自由度差一些。另外使用程序把图片自动添加到对应的markdown文件以便在github上查看。除了图片外，也会支持其它媒体内容。

##### 目录结构

streamlit_app.py和add_media.py分别用于显示界面和添加媒体文件到markdown文件中。

articles文件夹为md文件，按月份分组；files文件夹为媒体文件，文件夹与md文件的路径对应。

##### 其它说明

本项目已部署到Streamlit Cloud,域名为 https://willian7004-media-blog.streamlit.app

### 本地部署

##### 使用python部署
1.安装依赖
```bash
pip install -r requirements.txt
```
2.运行应用
```
streamlit run streamlit_app.py
```

##### 使用docker部署
1.创建docker
```bash
docker build . -t new-homepage
```
2.运行docker
```bash
docker run -p 8501:8501 new-homepage
```
