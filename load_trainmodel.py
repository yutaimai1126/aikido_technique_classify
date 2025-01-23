import os
import tensorflow as tf
from object_detection.utils import config_util
from object_detection.protos import pipeline_pb2
from google.protobuf import text_format
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder
import cv2 
import numpy as np

WORKSPACE_PATH = 'Tensorflow/workspace'
SCRIPTS_PATH = 'Tensorflow/scripts'
APIMODEL_PATH = 'Tensorflow/models'
ANNOTATION_PATH = WORKSPACE_PATH+'/annotations'
IMAGE_PATH = WORKSPACE_PATH+'/images'
MODEL_PATH = WORKSPACE_PATH+'/models'
PRETRAINED_MODEL_PATH = WORKSPACE_PATH+'/pre-trained-models'
CONFIG_PATH = MODEL_PATH+'/my_ssd_mobnet/pipeline.config'
CHECKPOINT_PATH = MODEL_PATH+'/my_ssd_mobnet/'
CUSTOM_MODEL_NAME = 'my_ssd_mobnet' 
TEST_PATH = WORKSPACE_PATH + '/images/test' 
RESULT_PATH = WORKSPACE_PATH + '/images/result' 

# Load pipeline config and build a detection model
configs = config_util.get_configs_from_pipeline_file(CONFIG_PATH)
detection_model = model_builder.build(model_config=configs['model'], is_training=False)

# Restore checkpoint
ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
ckpt.restore(os.path.join(CHECKPOINT_PATH, 'ckpt-6')).expect_partial()

@tf.function
def detect_fn(image):
    image, shapes = detection_model.preprocess(image)
    prediction_dict = detection_model.predict(image, shapes)
    detections = detection_model.postprocess(prediction_dict, shapes)
    return detections

category_index = label_map_util.create_category_index_from_labelmap(ANNOTATION_PATH+'/label_map.pbtxt')

# 画像の読み込みと前処理
test_pic_list = ['nikyo_14','nikyo_15','sankyo_14','sankyo_15']
for test_pic in test_pic_list:
    frame = cv2.imread(f'{TEST_PATH}/{test_pic}.jpg')
    image_np = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # サイズを小さくする（幅と高さを 20% に縮小する例）
    scale_percent = 20  # 縮小率（%）
    width = int(image_np.shape[1] * scale_percent / 100)
    height = int(image_np.shape[0] * scale_percent / 100)
    dim = (width, height)

    # 画像をリサイズ
    image_np_resized = cv2.resize(image_np, dim, interpolation=cv2.INTER_AREA)

    # 推論
    input_tensor = tf.convert_to_tensor(np.expand_dims(image_np_resized, 0), dtype=tf.float32)
    detections = detect_fn(input_tensor)

    # 結果の整形
    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}
    detections['num_detections'] = num_detections
    detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

    # 描画
    label_id_offset = 1
    image_np_with_detections = image_np_resized.copy()
    viz_utils.visualize_boxes_and_labels_on_image_array(
        image_np_with_detections,
        detections['detection_boxes'],
        detections['detection_classes'] + label_id_offset,
        detections['detection_scores'],
        category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=5,
        min_score_thresh=0.5,
        agnostic_mode=False,
    )

    # 結果をBGR形式に戻して表示
    image_bgr_with_detections = cv2.cvtColor(image_np_with_detections, cv2.COLOR_RGB2BGR)

    cv2.imwrite(f'{RESULT_PATH}/{test_pic}.jpg', image_bgr_with_detections)
    cv2.imshow('object detection', cv2.resize(image_bgr_with_detections, (800, 600)))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# cv2.destroyAllWindows()

# # Setup capture
# cap = cv2.VideoCapture(0)
# width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# while True: 
#     ret, frame = cap.read()
#     image_np = np.array(frame)
    
#     input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
#     detections = detect_fn(input_tensor)
    
#     num_detections = int(detections.pop('num_detections'))
#     detections = {key: value[0, :num_detections].numpy()
#                   for key, value in detections.items()}
#     detections['num_detections'] = num_detections

#     # detection_classes should be ints.
#     detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

#     label_id_offset = 1
#     image_np_with_detections = image_np.copy()

#     viz_utils.visualize_boxes_and_labels_on_image_array(
#                 image_np_with_detections,
#                 detections['detection_boxes'],
#                 detections['detection_classes']+label_id_offset,
#                 detections['detection_scores'],
#                 category_index,
#                 use_normalized_coordinates=True,
#                 max_boxes_to_draw=5,
#                 min_score_thresh=.5,
#                 agnostic_mode=False)

#     cv2.imshow('object detection',  cv2.resize(image_np_with_detections, (800, 600)))
    
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         cap.release()
#         break

