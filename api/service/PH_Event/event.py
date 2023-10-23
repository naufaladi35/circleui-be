import pytz
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status, UploadFile, File

from api.model.PH_Event.event import Event 
from api.repository.PH_Event import event as event_repository
from api.repository.PH_Main import user as user_repository
from typing import Optional
import cloudinary
import cloudinary.uploader


async def get_events(skip, limit):
    return await event_repository.get_items(skip, limit)

async def get_events_by_name(name, skip, limit):
    if(events := await event_repository.get_items_by_name(name, skip, limit)) is not None:
        return events

async def get_event(id: str):
    if(event := await event_repository.get_item(id)) is not None:
        return event
    raise HTTPException(status_code=404, detail=f"event {id} not found")

async def get_events_by_month_year(month, year, skip, limit):
    if int(month) < 1 or int(month) > 12:
        raise HTTPException(status_code=400, detail="please enter valid month")
    if(events := await event_repository.get_items_by_month(month, year, skip, limit)) is not None:
        return events

async def create_event(organizer: str, file:Optional[UploadFile], form_data: Event):
    now = datetime.now().astimezone(pytz.timezone(
        'Asia/Jakarta')).isoformat(timespec='seconds')
    event = jsonable_encoder(form_data)
    event['organizer'] = organizer
    event['createdAt'] = now
    event['updatedAt'] = now
    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.svg')):
        upload_file = cloudinary.uploader.upload(
            file.file,
            folder = 'event_assets',
            allowed_formats = ['jpg', 'png', 'jpeg', 'svg']
        )
        url = upload_file.get('secure_url')
        event['image'] = url
    elif file and (not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.svg'))):
        return JSONResponse(
            status_code = 403,
            content = 'File type not allowed'
        )
    insert_event = await event_repository.insert_item(content=event)
    status_code = status.HTTP_201_CREATED
    content = {
        'status': 'accepted',
        'acknowledged': insert_event.acknowledged,
        'inserted_id': insert_event.inserted_id
    }
    return JSONResponse(
        status_code=status_code,
        content=content
    )


async def update_event(updater: str, form_data: Event, id: str, file: Optional[UploadFile] = File(None)):
    status_code = ''
    content = ''
    now = datetime.now().astimezone(pytz.timezone(
        'Asia/Jakarta')).isoformat(timespec='seconds')

    event = await event_repository.get_item(id)
    if event and (event['organizer'] == updater):
        update = jsonable_encoder(form_data)
        update['updatedAt'] = now
        if file is not None:
            if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.svg')):
                upload_file = cloudinary.uploader.upload(
                    file.file,
                    folder = 'event_assets',
                    allowed_formats = ['jpg', 'png', 'jpeg', 'svg']
                )
                url = upload_file.get('secure_url')
                update['image'] = url
            elif file and (not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.svg'))):
                return JSONResponse(
                    status_code = 403,
                    content = 'File type not allowed'
                )
        else:
            update['image'] = event['image']
        update_post = await event_repository.update_item(update, id)
    
        if update_post:
            status_code = status.HTTP_200_OK
            content = {
                'status': 'updated',
                'message': 'your event is successfully updated'
            }
    elif event and (event['organizer'] != updater):
        status_code = status.HTTP_403_FORBIDDEN
        content = {
            'status': 'prohibited',
            'message': 'you are not the organizer of this event'
        }
    else:
        status_code = status.HTTP_404_NOT_FOUND
        content = {
            'status': 'not found',
            'message': f'event {id} not found'
        }

    return JSONResponse(
        status_code=status_code,
        content=content
    )


async def delete_event(deleter: str, id: str):
    status_code = ''
    content = ''
    event = await event_repository.get_item(id)

    if event and (event['organizer'] == deleter):
        delete_event = await event_repository.delete_item(id)
        status_code = status.HTTP_204_NO_CONTENT
        content = {
            'status': 'deleted',
            'acknowledged': delete_event.acknowledged,
            'deleted_count': delete_event.deleted_count
        }
    elif event and (event['organizer'] != deleter):
        status_code = status.HTTP_403_FORBIDDEN
        content = {
            'status': 'forbidden',
            'message': 'you are not the organizer of this event'
        }
    else:
        status_code = status.HTTP_404_NOT_FOUND
        content = {
            'status': 'not found',
            'message': f'event {id} not found'
        }
    
    return JSONResponse(
        status_code = status_code,
        content = content
    )

async def event_bookmark(user_email: str, id: str):
    event = await event_repository.get_item(id)
    user = await user_repository.get_specific_user_by_email(user_email)
    if event:
        if id in user["eventEnrolled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"user has already bookmark {event['name']}"
            )
        else:
            await event_repository.event_bookmark(user_email, id)
            event['numberOfBookmark'] += 1
            await event_repository.update_item(event, id)
            return event
            
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"event {id} not found"
        )

async def event_unbookmark(user_email: str, id: str):
    event = await event_repository.get_item(id)
    user = await user_repository.get_specific_user_by_email(user_email)
    if event:
        if id in user["eventEnrolled"]:
            await event_repository.event_unbookmark(user_email, id)
            event['numberOfBookmark'] -= 1
            await event_repository.update_item(event, id)
            return event
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"event {id} not found"
        )