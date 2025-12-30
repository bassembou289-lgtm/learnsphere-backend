# models.py
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base
import json
from pydantic import BaseModel, Field
from typing import Optional, List


# -------------------------
# SQLALCHEMY DATABASE MODEL
# -------------------------
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    avatar = Column(String, default="default_url")
    total_xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    rank = Column(String, default="Beginner")
    topics_completed = Column(Integer, default=0)
    completed_topics_in_rank = Column(Text, default="[]")  # store JSON list

    school = Column(String, nullable=True)
    description = Column(String, nullable=True)

    def get_completed_topics(self):
        try:
            return json.loads(self.completed_topics_in_rank)
        except:
            return []

    def set_completed_topics(self, topics):
        self.completed_topics_in_rank = json.dumps(topics)


# -------------------------
# Pydantic API Schemas
# (camelCase keys)
# -------------------------

# User Response Schema
class User(BaseModel):
    id: int
    username: str
    avatar: str
    total_xp: int = Field(..., alias="total_xp")
    level: int
    rank: str
    topics_completed: int = Field(..., alias="topics_completed")
    completed_topics_in_rank: List[str] = Field(..., alias="completed_topics_in_rank")
    school: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


# Request Bodies
class AuthRequest(BaseModel):
    username: str
    password: Optional[str] = None


class SettingsRequest(BaseModel):
    username: str
    avatar: Optional[str] = None
    school: Optional[str] = None
    description: Optional[str] = None
    newPassword: Optional[str] = None


class XPRequest(BaseModel):
    username: str
    topic: str
    score: int
    level: int


class BonusRequest(BaseModel):
    username: str
    score: int


class DashboardRequest(BaseModel):
    username: str


class LessonRequest(BaseModel):
    topic: str
    language: str
    rank: str
    level: int


class ChatMessage(BaseModel):
    author: str
    content: str


class ChatRequest(BaseModel):
    lessonContent: str
    messages: List[ChatMessage]
    language: str


class TriviaRequest(BaseModel):
    language: str
