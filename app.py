from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.controller.PH_Main import (
  user,
)

from api.controller.PH_Community import (
  community_controller,
  post,
  comment_controller,
  announcement_controller
)

from api.controller.PH_Event import (
  event
)

app = FastAPI(title = 'Circle UI')
app.include_router(user.router)
app.include_router(community_controller.router)
app.include_router(post.router)
app.include_router(comment_controller.router)
app.include_router(event.router)
app.include_router(announcement_controller.router)

origins = [
   "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)