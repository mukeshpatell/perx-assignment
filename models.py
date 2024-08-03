# models.py
# This file contains the SQLAlchemy models for the database.

from sqlalchemy import Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import Mapped, mapped_column
from typing import List, Optional

Base = declarative_base()

class Campaign(Base):
    __tablename__ = 'campaign'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(255))
    reward_campaign: Mapped[List["RewardCampaign"]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )
    def __repr__(self) -> str:
        return f"Campaign(id={self.id}, name={self.name}, status={self.status})"
    
    @classmethod
    def get_columns(cls):
        return [column.name for column in cls.__table__.columns]
    
    @classmethod
    def get_table(cls):
        return cls.__tablename__


class RewardCampaign(Base):
    __tablename__ = 'reward_campaign'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reward_name: Mapped[str] = mapped_column(String(255))
    updated_at: Mapped[Optional[str]] = mapped_column(TIMESTAMP)
    campaign_id: Mapped[int] = mapped_column(ForeignKey('campaign.id'))
    campaign: Mapped["Campaign"] = relationship(back_populates="reward_campaign")
    reward_transaction: Mapped[List["RewardTransaction"]] = relationship(
        back_populates="reward_campaign", cascade="all, delete-orphan"
    )
    def __repr__(self) -> str:
        return f"RewardCampaign(id={self.id}, reward_name={self.reward_name}, updated_at={self.updated_at})"
    
    @classmethod
    def get_columns(cls):
        return [column.name for column in cls.__table__.columns]

    @classmethod
    def get_table(cls):
        return cls.__tablename__

class RewardTransaction(Base):
    __tablename__ = 'reward_transaction'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(255))
    updated_at: Mapped[Optional[str]] = mapped_column(TIMESTAMP)
    reward_campaign_id: Mapped[int] = mapped_column(ForeignKey('reward_campaign.id'))
    reward_campaign: Mapped["RewardCampaign"] = relationship(back_populates="reward_transaction")
    def __repr__(self) -> str:
        return f"RewardTransaction(id={self.id}, status={self.status}, updated_at={self.updated_at})"
    
    @classmethod
    def get_columns(cls):
        return [column.name for column in cls.__table__.columns]

    @classmethod
    def get_table(cls):
        return cls.__tablename__

class HTTPLog(Base):
    __tablename__ = 'http_log'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[Optional[str]] = mapped_column(TIMESTAMP)
    http_method: Mapped[str] = mapped_column(String(10))
    http_path: Mapped[str] = mapped_column(String)
    user_id: Mapped[Optional[str]] = mapped_column(String(50))
    def __repr__(self) -> str:
        return f"HTTPLog(timestamp={self.timestamp}, http_method={self.http_method}, http_path={self.http_path}, user_id={self.user_id})"
    
    @classmethod
    def get_columns(cls):
        return [column.name for column in cls.__table__.columns]

    @classmethod
    def get_table(cls):
        return cls.__tablename__

class RewardCampaignRelationship(Base):
    __tablename__ = 'reward_campaign_relationship'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[Optional[str]] = mapped_column(String(50), primary_key=True)
    reward_id: Mapped[Optional[str]] = mapped_column(String(50), primary_key=True)
    def __repr__(self) -> str:
        return f"RewardCampaignRelationship(campaign_id={self.campaign_id}, reward_id={self.reward_id})"
    
    @classmethod
    def get_columns(cls):
        return [column.name for column in cls.__table__.columns]

    @classmethod
    def get_table(cls):
        return cls.__tablename__

