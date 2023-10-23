from datetime import datetime
from fastapi import APIRouter, Security, File, UploadFile

from api.model.PH_Main.user import User
from api.model.PH_Event.event import Event
from api.service.PH_Main import user as user_service
from api.service.PH_Event import event as event_service
from typing import Optional

router = APIRouter(
    prefix='/api/v1',
    tags=['event'],
)


@router.get('/events')
async def get_events(
    current_user: User = Security(
        user_service.get_current_active_user, scopes=['me', 'logout']),
    skip : int = 0,
    limit : int = 10
):
    events = await event_service.get_events(skip, limit)
    result = {
        'accessed_by': f"{current_user['user']['username']}",
        'content': events
    }
    return result

@router.get('/events/search')
async def search_events_controller(
    name: str,
    current_user: User = Security(
    user_service.get_current_active_user, scopes=['me', 'logout']),
    skip : int = 0,
    limit : int = 10
):
    events = await event_service.get_events_by_name(name, skip, limit)
    result = {
        'accessed_by': f"{current_user['user']['username']}",
        'content': events
    }
    return result

@router.get('/event/{id}')
async def get_specific_event(
    id: str,
    current_user: User = Security(
        user_service.get_current_active_user, scopes=['me', 'logout'])
):
    event = await event_service.get_event(id)
    result = {
        'accessed_by': f"{current_user['user']['username']}",
        'content': event
    }
    return result


@router.post('/event')
async def create_event(
    form_data: Event,
    file: Optional[UploadFile] = File(None),
    current_user: User = Security(
        user_service.get_current_active_user, scopes=['me', 'logout'])
    ):
    return await event_service.create_event(current_user['user']['email'], file, form_data)


@router.put('/event/{id}')
async def update_event(
    id: str,
    form_data: Event,
    file: Optional[UploadFile] = File(None),   
    current_user: User = Security(
        user_service.get_current_active_user, scopes=['me', 'logout'])
):
    return await event_service.update_event(current_user['user']['email'], form_data, id, file)


@router.delete('/event/{id}')
async def delete_event(
    id: str,
    current_user: User = Security(
        user_service.get_current_active_user, scopes=['me', 'logout'])
):
    return await event_service.delete_event(current_user['user']['email'], id)

@router.put("/event/{id}/bookmark")
async def event_bookmark(
    id: str,
    current_user: User = Security(
        user_service.get_current_active_user, scopes=['me', 'logout'])
):
    return await event_service.event_bookmark(current_user['user']['email'], id)

@router.put("/event/{id}/unbookmark")
async def event_unbookmark(
    id: str,
    current_user: User = Security(
        user_service.get_current_active_user, scopes=['me', 'logout'])
):
    return await event_service.event_unbookmark(current_user['user']['email'], id)

@router.get('/this-months-events')
async def this_month_events(
    current_month : str,
    current_year : str,
    current_user: User = Security(
        user_service.get_current_active_user, scopes=['me', 'logout']),
    skip : int = 0,
    limit : int = 5,
    ):
    events = await event_service.get_events_by_month_year(current_month, current_year, skip, limit)
    result = {
        'accessed_by': f"{current_user['user']['username']}",
        'content': events
    }
    return result