import streamlit as st
import os
import re
from PIL import Image
import shutil #フォルダを中身毎削除

#ocr
from pathlib import Path
from llama_index import download_loader

#スクレイピング
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep


st.markdown('### 配送関連情報取得app')
st.caption('llamaindex ocr')

os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']

# 画像を保存する一時的なディレクトリを作成
temp_dir = Path("temp")
temp_dir.mkdir(exist_ok=True)

#ファイルのアップロード
uploaded_file = st.file_uploader("画像ファイルをアップロードしてください", type=["png", "jpeg"])

image_path = ''
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    image_path = temp_dir / uploaded_file.name
    image.save(image_path)
else:
    st.warning("PNGファイルをアップロードしてください")

ImageReader = download_loader("ImageReader")

# If the Image has key-value pairs text, use text_type = "key_value"
loader = ImageReader(text_type = "plain text")
# file_path = Path(r'C:\Users\hskw1\git_space\llamaindex_ocr\data\送り状番号画像.PNG')
documents = loader.load_data(file=image_path)

#リスト内の要素を抽出
doc = documents[0]
#textを抽出（xml形式）
doc_text = doc.text

# 正規表現を使用して数字のつながりを抽出します
pattern = r"\d+"
num = re.findall(pattern, doc_text) #リスト形式
num = num[0]

st.markdown('###### 濃飛運輸倉庫 問い合わせNo')
st.code(num)

##########################selenium
driver = webdriver.Chrome(executable_path=r'C:\Users\hskw1\git_space\llamaindex_ocr\chromedriver')
driver.get('https://www3.nohhi.co.jp/rktrace/trace.html')

#name属性で要素を検索する
search_bar = driver.find_element_by_name("command5")
#入力場所に問い合わせ番号を入力
search_bar.send_keys(num)
#enter
search_bar.submit()

#配達状況
situation1 = driver.find_element(\
    by=By.XPATH, value='/html/body/table/tbody/tr/td/table[1]/tbody/tr[3]/td[2]/font')

situation1 = situation1.text

#営業所着時間
if situation1 == '配達完了':
    situation = driver.find_element(\
    by=By.XPATH, value='/html/body/table/tbody/tr/td/table[1]/tbody/tr[3]/td[2]')

    situation = situation.text

else:
    situation = ''

#配送業者
deliverly_company = driver.find_element(\
    by=By.XPATH, value='/html/body/table/tbody/tr/td/table[1]/tbody/tr[4]/td[2]')

deliverly_company = deliverly_company.text

#問い合わせ番号
toiawse_num = driver.find_element(\
    by=By.XPATH, value='/html/body/table/tbody/tr/td/table[1]/tbody/tr[5]/td[2]')

toiawse_num = toiawse_num.text

#電話番号
tel = driver.find_element(\
    by=By.XPATH, value='/html/body/table/tbody/tr/td/table[1]/tbody/tr[6]/td[2]')

tel = tel.text

#個数
cnt = driver.find_element(\
    by=By.XPATH, value='/html/body/table/tbody/tr/td/table[1]/tbody/tr[10]/td[2]')

cnt = cnt.text

#重量
weight = driver.find_element(\
    by=By.XPATH, value='/html/body/table/tbody/tr/td/table[1]/tbody/tr[11]/td[2]')

weight = weight.text

st.markdown('###### 配送関連情報')
st.code(f'【最新状況】{situation}\n【配送業者】{deliverly_company}\n【問い合わせ番号】{toiawse_num}\n\
        【電話番号】{tel}\n【個数】{cnt}\n【重量】{weight}kg\
        ')

# 全ての処理が完了した後にtemp_dirと中の画像ファイルを削除
shutil.rmtree(temp_dir)

