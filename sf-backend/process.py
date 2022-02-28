from ast import Bytes
import sqlite3
import torch
import clip
import pandas as pd
import numpy as np
from io import BytesIO
import requests
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize
# import tensorflow as tf
# import tensorflow_text
# import keras
import os
from PIL import Image
# wget https://github.com/haltakov/natural-language-image-search/releases/download/1.0.0/photo_ids.csv -O unsplash-dataset/photo_ids.csv
# wget https://github.com/haltakov/natural-language-image-search/releases/download/1.0.0/features.npy -O unsplash-dataset/features.npy


device = "cuda" if torch.cuda.is_available() else "cpu"
# trans_vision = keras.models.load_model("vision_encoder")
# trans_text = keras.models.load_model("text_encoder")
model, preprocess = clip.load("ViT-B/32", device=device)
model2, preprocess2 = clip.load("RN50x64", device=device)
photo_ids = pd.read_csv("unsplash-dataset/photo_ids.csv")
photo_ids = list(photo_ids['photo_id'])
photo_features = np.load("unsplash-dataset/features.npy")
photo_features = torch.from_numpy(photo_features).float().to(device)


def load_dataset():
    root_dir = "data_image"
    annotations_dir = os.path.join(root_dir, "annotations")
    images_dir = os.path.join(root_dir, "train2014")
    tfrecords_dir = os.path.join(root_dir, "tfrecords")
    annotation_file = os.path.join(annotations_dir, "captions_train2014.json")
    print("loading data")
    if not os.path.exists(annotations_dir):
        annotation_zip = tf.keras.utils.get_file(
            "captions.zip",
            cache_dir=os.path.abspath("."),
            origin="http://images.cocodataset.org/annotations/annotations_trainval2014.zip",
            extract=True,
        )
        os.remove(annotation_zip)

    if not os.path.exists(images_dir):
        image_zip = tf.keras.utils.get_file(
            "train2014.zip",
            cache_dir=os.path.abspath("."),
            origin="http://images.cocodataset.org/zips/train2014.zip",
            extract=True,
        )
        os.remove(image_zip)

    print("download complete")

    with open(annotation_file, "r") as f:
        annotations = json.load(f)["annotations"]

    image_path_to_caption = collections.defaultdict(list)
    for element in annotations:
        caption = f"{element['caption'].lower().rstrip('.')}"
        image_path = images_dir + "/COCO_train2014_" + \
            "%012d.jpg" % (element["image_id"])
        image_path_to_caption[image_path].append(caption)

    image_paths = list(image_path_to_caption.keys())
    print("processing complete")
    
def search_clip(query):
    text = clip.tokenize(query).to(device)
    with torch.no_grad():
        query_embeddings = model.encode_text(text)
        query_embeddings /= query_embeddings.norm(dim=-1, keepdim=True)
    
    sim = (photo_features @ query_embeddings.T).squeeze(1)
    idx = (-sim).argsort()
    image_list = []

    for i in idx[:9]:
        image_list.append(photo_ids[i])
    print("search done")
    return image_list

def search_clip_less(query):
    text = clip.tokenize(query).to(device)
    with torch.no_grad():
        query_embeddings = model2.encode_text(text)
        query_embeddings /= query_embeddings.norm(dim=-1, keepdim=True)
    
    sim = (photo_features @ query_embeddings.T).squeeze(1)
    idx = (-sim).argsort()
    image_list = []

    for i in idx[:9]:
        image_list.append(photo_ids[i])
    print("search done")
    return image_list
    

def search_lstm(image_embeddings, query, k=9, normalize=True):
    query_embedding = lstm_text(tf.convert_to_tensor(query))
    if normalize:
        image_embeddings = tf.math.l2_normalize(image_embeddings, axis=1)
        query_embedding = tf.math.l2_normalize(query_embedding, axis=1)
    dot_similarity = tf.matmul(
        query_embedding, image_embeddings, transpose_b=True)
    results = tf.math.top_k(dot_similarity, k).indices.numpy()
    return [[image_paths[idx] for idx in indices] for indices in results]


def search_trans(image_embeddings, query, k=9, normalize=True):
    query_embedding = trans_text(tf.convert_to_tensor(query))
    if normalize:
        image_embeddings = tf.math.l2_normalize(image_embeddings, axis=1)
        query_embedding = tf.math.l2_normalize(query_embedding, axis=1)
    dot_similarity = tf.matmul(
        query_embedding, image_embeddings, transpose_b=True)
    results = tf.math.top_k(dot_similarity, k).indices.numpy()
    return [[image_paths[idx] for idx in indices] for indices in results]
