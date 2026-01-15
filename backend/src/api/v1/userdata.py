from fastapi import APIRouter, HTTPException, Depends, status
from ..deps import get_session, get_gemini_service, get_current_user
from ...models import User, Interest, UserInterest
from ...schemas import UsernameData, EmailData, InterestData
from sqlalchemy.orm import Session
from ...db import get_db
from fastapi.responses import JSONResponse
from supertokens_python.recipe.session import SessionContainer 
from ...services.gemini_service import GeminiService
import random

router = APIRouter(prefix="/userdata", tags=["UserData"])

@router.post("/name", response_class=JSONResponse)
async def set_username(
   username_data: UsernameData,
   db: Session = Depends(get_db),
   user: User = Depends(get_current_user)
):
   existing_user: User | None = db.query(User).filter(
      User.handle == username_data.username, 
      User.id != user.id
   ).first()

   if existing_user:
      raise HTTPException(
         status_code=status.HTTP_409_CONFLICT, 
         detail="Username already taken"
      )
   
   user.handle = username_data.username
   db.commit()
   db.refresh(user)

   return JSONResponse(
      status_code=status.HTTP_200_OK,
      content = {
         "message": "Username updated successfully", 
         'username': username_data.username
      }
   )

@router.post("/email", response_class=JSONResponse)
async def set_email(
   email_data: EmailData,
   db: Session = Depends(get_db),
   user: User = Depends(get_current_user)
):
   user.email = email_data.email

   db.commit()
   db.refresh(user)

   return JSONResponse(
      status_code=status.HTTP_200_OK,
      content={
         "message": "Email updated successfully", 
         'email': email_data.email
      }
   )

@router.post("/interests", response_class=JSONResponse)
async def set_interests(
   interest_data: InterestData,
   db: Session = Depends(get_db),
   user: User = Depends(get_current_user)
):
   unadded_interests : list[str] = []
   added_interests : list[UserInterest] = []
   
   for interest in interest_data.interests:

      interest_category: Interest | None = db.query(Interest).filter(
         Interest.name.ilike(interest.strip().lower())
      ).first()

      if interest_category is None:
         unadded_interests.append(interest)
         continue

      user_interest_exists: UserInterest | None = db.query(UserInterest).filter(
         UserInterest.user_id == user.id,
         UserInterest.interest_id == interest_category.id
      ).first()

      if user_interest_exists is not None:
         unadded_interests.append(interest)
         continue

      new_user_interest = UserInterest(
         user_id=user.id,
         interest_id=interest_category.id
      )

      added_interests.append(new_user_interest)

   try:
      db.add_all(added_interests)
      db.commit()
   except Exception as e:
      db.rollback()
      raise HTTPException(
         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
         detail=f"Error adding interests."
      )
   
   if len(unadded_interests) == 0:
      return JSONResponse(
         status_code=status.HTTP_200_OK,
         content={
            "message": "All interests updated successfully", 
            'interests': interest_data.interests
         }
      )
   elif len(unadded_interests) == len(interest_data.interests):
      raise HTTPException(
         status_code=status.HTTP_400_BAD_REQUEST, 
         detail="No interests were found to add or they don't match existing categories in DB"
      )

   else:
      added_interests_str = [
         interest for interest in interest_data.interests 
         if interest not in unadded_interests
      ]
      return JSONResponse(
         status_code=status.HTTP_207_MULTI_STATUS,
         content={
            "message": "Some interests were not found and/or could not be added", 
            'added_interests': added_interests_str,
            'unadded_interests': unadded_interests
         }
      )

@router.get("/topic", response_class=JSONResponse)
async def get_speaking_topic(
   db: Session = Depends(get_db),
   user: User = Depends(get_current_user),
   gemini_service: GeminiService = Depends(get_gemini_service)
):
   user_interests: list[UserInterest] = db.query(UserInterest).filter(
      UserInterest.user_id == user.id
   ).all()

   if not user_interests:
      raise HTTPException(
         status_code=status.HTTP_400_BAD_REQUEST,
         detail="User has no interests selected"
      )

   interests_list : list[str] = []

   for user_interest in user_interests:
      interest_category: Interest | None = db.query(Interest).filter(
         Interest.id == user_interest.interest_id
      ).first()

      if interest_category:
         interests_list.append(interest_category.name)

   interest = random.choice(interests_list)

   try:
      topic = await gemini_service.generate_topic(interest, user.preferred_lang)
   except Exception as e:
      raise HTTPException(
         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
         detail=f"Error generating interest & topic: {str(e)}"
      )
   
   return JSONResponse(
      status_code=status.HTTP_200_OK,
      content={
         "interest": interest,
         "topic": topic
      }
   )