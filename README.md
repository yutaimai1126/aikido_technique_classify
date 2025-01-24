# 合気道の技の種類判定
## 背景
日本の伝統武道である合気道には演武という技を披露する機会があるが、合気道をやったことない観客にとっては何が起きているかよくわからず、「なにがすごいのかわからない」という感想になることがある。
これは普段から合気道を稽古する私にとって、とても悔しい。合気道には骨格の弱点や重心移動を利用することで身体の小さい人が大きい人に勝つ理合がある。
合気道家はその理合を体得するために、先人が残した「型」をひたすら繰り返し稽古する。その型稽古を対外的に披露する舞台が「演武」であり、合気道のことを外部の人に知ってもらう絶好のチャンスである。
演武で合気道の技を観客に理解してもらうために、リアルタイムで技を解説するシステムを開発したい。
その第一歩として、物体検知モデルである"Tensorflow Object Detection API"を用いて、技の種類を判定するアプリを開発する。

## 合気道の関節技
合気道には多数の上肢立関節技があり、代表的な技である「小手返し」では相手の手首を回外・掌屈、肘を屈曲、肩を外旋させることで相手を投げる[1]。
他にも、手首を回内・掌屈、肘を屈曲、肩を外転・内旋させる「三教」や手首を回内・背屈、肘を屈曲、肩を外転・内旋させる「三教」などの技がある(図は[1]より引用)。

<img src="other_pic/enatsu_2022/table_1.png" width="50%">

<img src="other_pic/enatsu_2022/nikyo.png" width="25%">
<img src="other_pic/enatsu_2022/nikyo_joint.png" width="25%">

<img src="other_pic/enatsu_2022/sankyo.png" width="25%">
<img src="other_pic/enatsu_2022/sankyo_joint.png" width="25%">

## 合気道の流し技
合気道の技には、上肢立関節技だけでなく、相手の攻撃を受け流しながら相手の重心を崩して投げる技もある。代表的な技に「呼吸投げ」とよばれる、相手の攻撃のタイミングと力の向きに合わせて相手を投げる技がある。

## データの収集とモデル作成
### 環境構築
#### venvで仮想環境をつくる
```shell
$ python -m venv .venv
$ venv .venv/bin/activate
```   
#### ラベリングツールとTensorflow Object Detection APIをgitclone
```shell
$ cd Tensorflow  
$ git clone https://github.com/HumanSignal/labelImg.git
$ git clone https://github.com/tensorflow/models.git
$ cd ..
```  
#### Tensorflowのバージョンを指定する
```Tensorflow/models/offical/pip_package/setup.py```の23,24行目
```python
version = '2.13.1'
tf_version = '2.13.1'
```

#### 依存関係をインストール
##### labelImgの依存関係
```shell
$ pip install -r Tensorflow/labelImg/requirements/requirements-linux-python3.txt
$ pyrcc5 -o Tensorflow/labelImg/resources.py Tensorflow/labelImg/resources.qrc
$ mv Tensorflow/labelImg/resources.py Tensorflow/labelImg/resources.qrc Tensorflow/labelImg/libs/
```
```Tensorflow/labelImg/resources.py```168,179,213行目を修正
```python
# 168行目のif Qt.RightButton & ev.buttons():を修正:
if ev.buttons() & Qt.RightButton == Qt.RightButton:
# 179行目のif Qt.LeftButton & ev.buttons():を修正
if ev.buttons() & Qt.LeftButton == Qt.LeftButton:
# 213行目のself.dock.setFeatures(self.dock.features() ^ self.dock_features)を修正
self.dock.setFeatures(self.dock_features)
```
##### Tensorflowの依存関係
```shell
$ python Tensorflow/models/official/pip_package/setup.py install
```

### ラベリング
```shell
$ python Tensorflow/labelImg/labelImg.py
```
実行後、labelImgのウィンドウが開く
<img src="other_pic/labelImg/labelImg_home.png" width="100%">

「ディレクトリを開く」と「保存先を変更する」で画像を保存しているフォルダを選択
<img src="other_pic/labelImg/labelImg_serect_dir.png" width="100%">

"w"を押して範囲選択モードに切り替え、ラベルづけしたい範囲を選択
<img src="other_pic/labelImg/labelImg_labeling.png" width="100%">

ラベル名を入力する
<img src="other_pic/labelImg/labelImg_naming.png" width="100%">

ラベリング後、画像を保存していたフォルダに```.xml```ファイルが作成されている。  
```Tensorflow/workspace/Images```内に、トレーニングデータ用とテスト用のディレクトリを作成し、画像と```.xml```ファイルのセットを振り分ける。
















#### Labelmapを作成
```shell
$ python create_label.py
```  

#### TFrecordを作成
```shell
$ python Tensorflow/scripts/generate_tfrecord.py -x Tensorflow/workspace/images/train -l Tensorflow/workspace/annotations/label_map.pbtxt -o Tensorflow/workspace/annotations/train.record
$ python Tensorflow/scripts/generate_tfrecord.py -x Tensorflow/workspace/images/test -l Tensorflow/workspace/annotations/label_map.pbtxt -o Tensorflow/workspace/annotations/test.record
```

#### Model configを作成
```shell
$ mkdir Tensorflow\workspace\modelsmy_ssd_mobnet
$ cp Tensorflow/workspace/pre-trained-models/ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8/pipeline.config Tensorflow/workspace/models/my_ssd_mobnet
```

#### Model configを更新
```shell
$ python update_config.py
```  

#### Modelを学習 
```shell
$ export PYTHONPATH=$PYTHONPATH:$/Tensorflow/models/
$ python Tensorflow/models/research/object_detection/model_main_tf2.py --model_dir=Tensorflow/workspace/models/my_ssd_mobnet --pipeline_config_path=Tensorflow/workspace/models/my_ssd_mobnet/pipeline.config --num_train_steps=5000
```  

## 検証結果

<img src="Tensorflow/workspace/images/result/nikyo_14.jpg" width="100%">
<!-- <img src="Tensorflow/workspace/images/result/nikyo_15.jpg" width="40%"> -->

<img src="Tensorflow/workspace/images/result/sankyo_14.jpg" width="100%">
<!-- <img src="Tensorflow/workspace/images/result/sankyo_15.jpg" width="40%"> -->


## 参考文献
[1][江夏怜. (2022). 日本武術の上肢立関節技における関節運動方向による分類. 武道学研究, 54(2), 141-148.](https://www.jstage.jst.go.jp/article/budo/54/2/54_2113/_article/-char/ja)

## 機械学習の参考にした教材
- [Nicholas Renotte, Tensorflow Object Detection in 5 Hours with Python | Full Course with 3 Projects](https://www.youtube.com/watch?v=yqkISICHH-U&t=1461s)