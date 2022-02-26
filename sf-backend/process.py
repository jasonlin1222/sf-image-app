import sqlite3
import torch
import clip
import requests

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device, jit=False)

DATABASE = "app.db"

def create_image_embeddings_transformer(image_paths):
	conn = sqlite3.connect(DATABASE)
	for img_path in image_paths:
		processed_image = preprocess_image(img_path)
		with torch.no_grad():
			embed = model.encode_image(processed_image).detach().numpy()
		embed = embed.tostring()

		## Insert data into sqlite3
		query = "INSERT INTO image_embeds(image_path, embedding) VALUES(?, ?);"
		conn.execute(query, (img_path, embed))
		conn.commit()
		print('Inserted', img_path)
	return 'success'

def create_image_embeddings_lstm(image_paths): #need fix
	conn = sqlite3.connect(DATABASE)
	for img_path in image_paths:
		processed_image = preprocess_image(img_path)
		with torch.no_grad():
			embed = model.encode_image(processed_image).detach().numpy()
		embed = embed.tostring()

		## Insert data into sqlite3
		query = "INSERT INTO image_embeds(image_path, embedding) VALUES(?, ?);"
		conn.execute(query, (img_path, embed))
		conn.commit()
		print('Inserted', img_path)
	return 'success'

def search_lstm(query):
    return

def search_trans(query):
    text = clip.tokenize(query).to(device)
    conn = sqlite3.connect(DATABASE)
    return

def cal_sim(feat1, feat2):
	img_embed = np.fromstring(feat2, dtype=np.float32)
	img_embed = img_embed.reshape((1, img_embed.shape[0]))
	sim = cosine_similarity(feat1, img_embed)
	return sim[0][0]

