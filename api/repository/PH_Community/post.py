from typing import Optional
from dotenv import load_dotenv

from api.repository.repository import connect
from api.model.PH_Community.post import Post

load_dotenv()
db = connect()

post_collection = db['post']

async def get_items(community_id: str, skip: int = 0, limit: int = 10):
    return await post_collection.find({'communityId': community_id}).sort('createdAt', -1).skip(skip).limit(limit).to_list(1000)

async def get_item(id: str):
    return await post_collection.find_one({'_id': id})

async def insert_item(content: Post):
    return await post_collection.insert_one(content)

async def update_item(post: Post, id: str):
    return await post_collection.update_one({'_id': id}, {'$set': post})

async def delete_item(id: str):
    return await post_collection.delete_one({'_id': id})
    