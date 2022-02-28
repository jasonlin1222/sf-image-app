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

device = "cuda" if torch.cuda.is_available() else "cpu"
# trans_vision = keras.models.load_model("vision_encoder")
# trans_text = keras.models.load_model("text_encoder")
model = torch.jit.load("model.pt").cpu().eval()
input_resolution = model.input_resolution.item()
context_length = model.context_length.item()
vocab_size = model.vocab_size.item()

preprocess = Compose([
    Resize(input_resolution, interpolation=Image.BICUBIC),
    CenterCrop(input_resolution),
    ToTensor()
])

image_mean = torch.tensor([0.48145466, 0.4578275, 0.40821073]).to(device)
image_std = torch.tensor([0.26862954, 0.26130258, 0.27577711]).to(device)

clip_image_emb = []
image_paths = []


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

def get_dataset():
    df = pd.read_csv('../Train_GCC-training.tsv', sep='\t')
    for image in df['Url']:
        image_paths.append(image)

    
def create_image_embeddings_clip(image_paths):
    for image in image_paths[:10]:
        response = requests.get(image)
        clip_image_emb.append(Image.open(BytesIO(response.content)).convert("RGB"))
    images = [preprocess(im)  for im in clip_image_emb]
    image_input = torch.tensor(np.stack(images)).to(device)
    image_input -= image_mean[:, None, None]
    image_input /= image_std[:, None, None]
    return image_input

def search_clip(query):
    clip_images = create_image_embeddings_clip(image_paths)
    print("image embedding done")
    text = clip.tokenize(query).to(device)
    with torch.no_grad():
        image_embeddings = model.encode_image(clip_images).float()
        query_embeddings = model.encode_text(text).float()
        image_embeddings /= image_embeddings.norm(dim=-1, keepdim=True)
        query_embeddings /= query_embeddings.norm(dim=-1, keepdim=True)
    sim = query_embeddings.cpu().numpy() @ image_embeddings.cpu().numpy().T
    sim = sim[0]
    print("encoding done")
    results = zip(range(len(sim)), sim)
    results = sorted(results, key=lambda x: x[1],reverse= True)
    top_N_images = []
    scores=[]
    for index,score in results[:9]:
        scores.append(score)
        top_N_images.append(clip_image_emb[index])
    return top_N_images

    

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
