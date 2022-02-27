import sqlite3
import torch
import clip
import requests
import tensorflow as tf
import tensorflow_text
import keras
import os
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device, jit=False)
trans_vision = keras.models.load_model("vision_encoder")
trans_text = keras.models.load_model("text_encoder")
image_paths = []
imgemb_clip = []

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
		image_path = images_dir + "/COCO_train2014_" + "%012d.jpg" % (element["image_id"])
		image_path_to_caption[image_path].append(caption)

	image_paths = list(image_path_to_caption.keys())
	print("processing complete")

def create_image_embeddings_clip(image_paths):
	for image in image_paths:
		imgemb_clip.append(preprocess(Image.open(image)).unsqueeze(0).to(device))

def create_image_embeddings_transformer(image_paths):
	fvision_encoder.predict(
    	tf.data.Dataset.from_tensor_slices(image_paths).map(read_image).batch(batch_size),
    	verbose=1,
	)
	return

def create_image_embeddings_lstm(image_paths):
	return

def read_image(image_path):
    image_array = tf.image.decode_jpeg(tf.io.read_file(image_path), channels=3)
    return tf.image.resize(image_array, (224, 224))

def search_clip(query, images = imgemb_clip, k=9):
	text = clip.tokenize(query).to(device)
	with torch.no_grad():
		image_embeddings = model.encode_image(images)
		query_embeddings = model.encode_text(text)
		image_embeddings /= image_embeddings.norm(dim=-1, keepdim = true)
		text_embeddings /= text_embeddings.norm(dim=-1, keepdim = true)

	dot_similarity = tf.matmul(query_embedding, image_embeddings, transpose_b=True)
	results = tf.math.top_k(dot_similarity, k).indices.numpy()
	return [[image_paths[idx] for idx in indices] for indices in results]

def search_lstm(image_embeddings, query, k=9, normalize=True):
    query_embedding = lstm_text(tf.convert_to_tensor(query))
    if normalize:
        image_embeddings = tf.math.l2_normalize(image_embeddings, axis=1)
        query_embedding = tf.math.l2_normalize(query_embedding, axis=1)
    dot_similarity = tf.matmul(query_embedding, image_embeddings, transpose_b=True)
    results = tf.math.top_k(dot_similarity, k).indices.numpy()
    return [[image_paths[idx] for idx in indices] for indices in results]

def search_trans(image_embeddings, query, k=9, normalize=True):
    query_embedding = trans_text(tf.convert_to_tensor(query))
    if normalize:
        image_embeddings = tf.math.l2_normalize(image_embeddings, axis=1)
        query_embedding = tf.math.l2_normalize(query_embedding, axis=1)
    dot_similarity = tf.matmul(query_embedding, image_embeddings, transpose_b=True)
    results = tf.math.top_k(dot_similarity, k).indices.numpy()
    return [[image_paths[idx] for idx in indices] for indices in results]