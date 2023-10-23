from ...model.PH_Community.community_models import CommunityModel, ManageMemberModel, ManageMemberOption
from ...repository.PH_Community.community_repo import add_community_to_user, create_new_community, find_community_with_name, find_new_community, get_all_communities_from_db, get_certain_community_from_db, delete_one_community_from_db, get_community_with_name, update_community_from_db, add_community_to_user, join_community_add_user_to_community, leave_community_remove_community_from_user, leave_community_remove_user_from_community
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import Body, HTTPException, status, UploadFile
from typing import Optional
import cloudinary
import cloudinary.uploader

def user_not_enrolled(user_email: str, community: dict):
    if user_email == community["admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"user is the admin of {community['name']}"
        )
    print(user_email)
    print(community["publicMembers"])
    print(community["pendingMembers"])
    if user_email in community["publicMembers"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"user is a member of {community['name']}"
        )
    if user_email in community["pendingMembers"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"user is not the admin of community {community['name']}"
        )
    return True


def user_is_community_admin(user_email: str, community: dict):
    if user_email != community["admin"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"user is not the admin of {community['name']}"
        )
    return True



async def create_community(community: CommunityModel, file:Optional[UploadFile], user_email: str):
    community = jsonable_encoder(community)
    name = community['name']
    community["admin"] = user_email
    # Check the uniqueness from the name of the group
    if(await find_community_with_name(name)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Community with the name '{name}' already exists")
    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.svg')):
        upload_file = cloudinary.uploader.upload(
            file.file,
            folder = 'community_assets',
            allowed_formats = ['jpg', 'png', 'jpeg', 'svg']
        )
        url = upload_file.get('secure_url')
        community['image'] = url
    elif file and (not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.svg'))):
        return JSONResponse(
            status_code = 403,
            content = 'File type not allowed'
        )
    new_community = await create_new_community(community)
    created_community = await find_new_community(new_community)
    await add_community_to_user(user_email, created_community['_id'])
    return created_community

async def get_all_communities(skip, limit):
    communities = await get_all_communities_from_db(skip, limit)
    return communities


async def get_certain_community(id: str):
    if(community := await get_certain_community_from_db(id)) is not None:
        return community
    raise HTTPException(status_code=404, detail=f"Community {id} not found")


async def update_community(user_email: str, id: str, file:Optional[UploadFile], data: dict):
    if(community := await get_certain_community_from_db(id)):
        if user_is_community_admin(user_email, community):
            if file is not None:
                await upload_image(data, file)
            else:
                data['image'] = community['image']
            await update_community_from_db(id, data)
            if(updated_community := await get_certain_community_from_db(id)) is not None:
                return updated_community

    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"community {id} not found"
        )

async def upload_image(data: dict,file:Optional[UploadFile]):
    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.svg')):
        upload_file = cloudinary.uploader.upload(
            file.file,
            folder = 'community_assets',
            allowed_formats = ['jpg', 'png', 'jpeg', 'svg']
        )
        url = upload_file.get('secure_url')
        data['image'] = url
    elif file and (not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.svg'))):
        return JSONResponse(
            status_code = 403,
            content = 'File type not allowed'
        )


async def delete_community(id: str):
    delete_result = await delete_one_community_from_db(id)

    if delete_result.deleted_count == 1:
        return True
    else:
        return False


async def get_communities_by_name(name: str, skip: int, limit: int):
    if(communities := await get_community_with_name(name, skip, limit)) is not None:
        return communities


async def join_community(user_email: str, id: str):
    community = await get_certain_community_from_db(id)
    if community:
        if user_not_enrolled(user_email, community):
            await join_community_add_user_to_community(user_email, id)

        if(updated_community := await get_certain_community_from_db(id)) is not None:
            return updated_community

    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"community {id} not found"
        )


async def approve_reject_member(community: dict, data: ManageMemberModel):
    option = data.option
    member_email = data.email
    if member_email in community['pendingMembers']:
        community['pendingMembers'].remove(member_email)
        if option == ManageMemberOption.approve and user_not_enrolled(member_email, community):
            await add_community_to_user(member_email, community['_id'])
            community['publicMembers'].append(member_email)
            community['totalMembers'] += 1
        await update_community_from_db(community['_id'], community)
        return community

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"{member_email} not in pending member list"
    )


async def manage_member(admin_email: str, community_id: str, data: ManageMemberModel):
    if community := await get_certain_community_from_db(community_id):
        if user_is_community_admin(admin_email, community):
            option = data.option
            if option == ManageMemberOption.remove:
                return await leave_community(data.email, community_id)
            else:
                return await approve_reject_member(community, data)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"community {community_id} not found"
    )


async def leave_community(user_email: str, id: str):
    community = await get_certain_community_from_db(id)
    if community:
        if user_email in community["publicMembers"]:
            await leave_community_remove_user_from_community(user_email, id)
            await leave_community_remove_community_from_user(user_email, id)
            community['totalMembers'] -= 1
            community['publicMembers'].remove(user_email)
            await update_community_from_db(id, community)

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{user_email} not a member of this community"
            )

        if(updated_community := await get_certain_community_from_db(id)) is not None:
            return updated_community

    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"community {id} not found"
        )
