# pylint: disable=invalid-name
# Disable class names that are too long to conform with naming classes after table names
"""This module contains the SQLAlchemy schema of the wanted tables in the warehouse
database."""
from sqlalchemy import DATE, INTEGER, TIME, VARCHAR, Column, ForeignKey
from sqlalchemy.schema import MetaData

from . import Base


# Declarative base class
class BaseWarehouse(Base):
    """A base class for wanted tables in warehouse database."""

    __abstract__ = True
    metadata = MetaData()


# ================
# Dimension Tables
# ================


class DateDim(BaseWarehouse):
    """A metaclass for `date_dim` table."""

    __tablename__ = "date_dim"

    date_key = Column(VARCHAR(8), primary_key=True, autoincrement=False)
    the_date = Column(DATE, nullable=False)
    day = Column(INTEGER, nullable=False)
    month = Column(INTEGER, nullable=False)
    year = Column(INTEGER, nullable=False)
    quater = Column(VARCHAR(2), nullable=False)
    day_of_week = Column(VARCHAR(20), nullable=False)
    month_name = Column(VARCHAR(20), nullable=False)
    is_weekend = Column(VARCHAR(10), nullable=False)


class MonthDim(BaseWarehouse):
    """A metaclass for `month_dim` table."""

    __tablename__ = "month_dim"

    month_key = Column(INTEGER, primary_key=True)
    month = Column(INTEGER, nullable=False)
    quater = Column(INTEGER, nullable=False)
    year = Column(INTEGER, nullable=False)
    month_name = Column(VARCHAR(20), nullable=False)


class TimeDim(BaseWarehouse):
    """A metaclass for `time_dim` table."""

    __tablename__ = "time_dim"

    time_key = Column(INTEGER, primary_key=True)
    the_time = Column(TIME, nullable=False)
    hour = Column(INTEGER, nullable=False)
    minute = Column(INTEGER, nullable=False)
    time_of_day = Column(VARCHAR(20), nullable=False)


class UserDemographicDim(BaseWarehouse):
    """A metaclass for `user_demographic_dim` table."""

    __tablename__ = "user_demographic_dim"

    user_demographic_key = Column(INTEGER, primary_key=True)
    age_range = Column(VARCHAR(20), nullable=False)
    reputation_range = Column(VARCHAR(20), nullable=False)


class UserDim(BaseWarehouse):
    """A metaclass for `user_dim` table."""

    __tablename__ = "user_dim"

    user_key = Column(INTEGER, primary_key=True)
    user_id = Column(INTEGER, nullable=False)
    display_id = Column(INTEGER)
    display_name = Column(VARCHAR(255), nullable=False)
    location = Column(VARCHAR(255))
    user_demographic_key = Column(
        INTEGER,
        ForeignKey(
            UserDemographicDim.user_demographic_key,
            name="fk_userDim_userDemographicDim_user_demographic_key",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        nullable=False,
    )
    created_date_key = Column(
        VARCHAR(8),
        ForeignKey(
            DateDim.date_key, name="fk_userDim_dateDim_created_date_key", onupdate="CASCADE", ondelete="SET NULL"
        ),
        nullable=False,
    )
    created_time_key = Column(
        INTEGER,
        ForeignKey(
            TimeDim.time_key, name="fk_userDim_timeDim_created_time_key", onupdate="CASCADE", ondelete="SET NULL"
        ),
        nullable=False,
    )


class QuestionPostDim(BaseWarehouse):
    """A metaclass for `question_post_dim` table."""

    __tablename__ = "question_post_dim"

    question_post_key = Column(INTEGER, primary_key=True)
    question_post_id = Column(INTEGER, nullable=False)
    title = Column(VARCHAR(None))
    body = Column(VARCHAR(None))
    created_date_key = Column(
        VARCHAR(8),
        ForeignKey(
            DateDim.date_key,
            name="fk_questionPostDim_dateDim_created_date_key",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        nullable=False,
    )
    created_time_key = Column(
        INTEGER,
        ForeignKey(
            TimeDim.time_key,
            name="fk_questionPostDim_timeDim_created_time_key",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        nullable=False,
    )


class TagDim(BaseWarehouse):
    """A metaclass for `tag_dim` table."""

    __tablename__ = "tag_dim"

    tag_key = Column(INTEGER, primary_key=True)
    tag_id = Column(INTEGER, nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    excerpt = Column(VARCHAR(None))
    description = Column(VARCHAR(None))


class QuestionPostTagBridge(BaseWarehouse):
    """A metaclass for `question_post_tag_bridge` table."""

    __tablename__ = "question_post_tag_bridge"

    question_post_key = Column(
        INTEGER,
        ForeignKey(
            QuestionPostDim.question_post_key,
            name="fk_questionPostTagBridge_questionPostDim_question_post_key",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    tag_key = Column(
        INTEGER,
        ForeignKey(
            TagDim.tag_key, name="fk_questionPostTagBridge_tagDim_tag_key", onupdate="CASCADE", ondelete="CASCADE"
        ),
        nullable=False,
    )


class UserActivityTypeDim(BaseWarehouse):
    """A metaclass for `user_activity_type_dim` table."""

    __tablename__ = "user_activity_type_dim"

    user_activity_type_key = Column(INTEGER, primary_key=True)
    user_activity_type_id = Column(INTEGER, nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    description = Column(VARCHAR(None))


# ===========
# Fact Tables
# ===========


class UserActivitiesFact(BaseWarehouse):
    """A metaclass for `user_activities_fact` table."""

    __tablename__ = "user_activities_fact"

    user_key = Column(
        INTEGER,
        ForeignKey(
            UserDim.user_key, name="fk_userActivitiesFact_userDim_user_key", onupdate="CASCADE", ondelete="NO ACTION"
        ),
        primary_key=True,
    )
    question_post_key = Column(
        INTEGER,
        ForeignKey(
            QuestionPostDim.question_post_key,
            name="fk_userActivitiesFact_questionPostDim_question_post_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
        primary_key=True,
    )
    user_demographic_key = Column(
        INTEGER,
        ForeignKey(
            UserDemographicDim.user_demographic_key,
            name="fk_userActivitiesFact_userDemographicDim_user_demographic_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
        nullable=False,
    )
    user_activity_type_key = Column(
        INTEGER,
        ForeignKey(
            UserActivityTypeDim.user_activity_type_key,
            name="fk_userActivitiesFact_userActivityTypeDim_user_activity_type_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
        primary_key=True,
    )
    activity_date_key = Column(
        VARCHAR(8),
        ForeignKey(
            DateDim.date_key,
            name="fk_userActivitiesFact_dateDim_activity_date_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
        primary_key=True,
    )
    activity_time_key = Column(
        INTEGER,
        ForeignKey(
            TimeDim.time_key,
            name="fk_userActivitiesFact_timeDim_activity_time_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
        primary_key=True,
    )
    user_activity_id = Column(INTEGER, nullable=False)


class MonthlyUserActivitiesFact(BaseWarehouse):
    """A metaclass for `monthly_activities_fact` table."""

    __tablename__ = "monthly_activities_fact"

    user_key = Column(
        INTEGER,
        ForeignKey(
            UserDim.user_key,
            name="fk_monthlyUserActivitiesFact_userDim_user_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
        primary_key=True,
    )
    user_demographic_key = Column(
        INTEGER,
        ForeignKey(
            UserDemographicDim.user_demographic_key,
            name="fk_monthlyUserActivitiesFact_userDemographicDim_user_demographic_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
        nullable=False,
    )
    month_key = Column(
        INTEGER,
        ForeignKey(
            MonthDim.month_key,
            name="fk_monthlyUserActivitiesFact_monthDim_month_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
        primary_key=True,
    )
    total_question_posts = Column(INTEGER, default=0)
    total_answers = Column(INTEGER, default=0)
    total_comments = Column(INTEGER, default=0)
    total_votes = Column(INTEGER, default=0)
    total_activities = Column(INTEGER, default=0)
    average_daily_activity_frequency = Column(INTEGER, default=0)


class QuestionPostLifeCycleFact(BaseWarehouse):
    """A metaclass for `question_post_life_cycle_fact` table."""

    __tablename__ = "question_post_life_cycle_fact"

    question_post_key = Column(
        INTEGER,
        ForeignKey(
            QuestionPostDim.question_post_key,
            name="fk_questionPostLifeCycleFact_questionPostDim_question_post_key",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    owner_user_key = Column(
        INTEGER,
        ForeignKey(
            UserDim.user_key,
            name="fk_questionPostLifeCycleFact_userDim_owner_user_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
        nullable=False,
    )
    owner_user_demographic_key = Column(
        INTEGER,
        ForeignKey(
            UserDemographicDim.user_demographic_key,
            name="fk_questionPostLifeCycleFact_userDemographicDim_owner_user_demographic_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
        nullable=False,
    )
    question_post_id = Column(INTEGER, nullable=False)
    created_date_key = Column(
        VARCHAR(8),
        ForeignKey(
            DateDim.date_key,
            name="fk_questionPostLifeCycleFact_dateDim_created_date_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
        nullable=False,
    )
    created_time_key = Column(
        INTEGER,
        ForeignKey(
            TimeDim.time_key,
            name="fk_questionPostLifeCycleFact_timeDim_created_time_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
        nullable=False,
    )
    first_activity_date_key = Column(
        VARCHAR(8),
        ForeignKey(
            DateDim.date_key,
            name="fk_questionPostLifeCycleFact_dateDim_first_activity_date_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
    )
    first_activity_time_key = Column(
        INTEGER,
        ForeignKey(
            TimeDim.time_key,
            name="fk_questionPostLifeCycleFact_timeDim_first_activity_time_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
    )
    latest_activity_date_key = Column(
        VARCHAR(8),
        ForeignKey(
            DateDim.date_key,
            name="fk_questionPostLifeCycleFact_dateDim_latest_activity_date_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
    )
    latest_activity_time_key = Column(
        INTEGER,
        ForeignKey(
            TimeDim.time_key,
            name="fk_questionPostLifeCycleFact_timeDim_latest_activity_time_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
    )
    first_answer_date_key = Column(
        VARCHAR(8),
        ForeignKey(
            DateDim.date_key,
            name="fk_questionPostLifeCycleFact_dateDim_first_answer_date_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
    )
    first_answer_time_key = Column(
        INTEGER,
        ForeignKey(
            TimeDim.time_key,
            name="fk_questionPostLifeCycleFact_timeDim_first_answer_time_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
    )
    accepted_answer_date_key = Column(
        VARCHAR(8),
        ForeignKey(
            DateDim.date_key,
            name="fk_questionPostLifeCycleFact_dateDim_accepted_answer_date_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
    )
    accepted_answer_time_key = Column(
        INTEGER,
        ForeignKey(
            TimeDim.time_key,
            name="fk_questionPostLifeCycleFact_timeDim_accepted_answer_time_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
    )
    community_owned_date_key = Column(
        VARCHAR(8),
        ForeignKey(
            DateDim.date_key,
            name="fk_questionPostLifeCycleFact_dateDim_community_owned_date_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
    )
    community_owned_time_key = Column(
        INTEGER,
        ForeignKey(
            TimeDim.time_key,
            name="fk_questionPostLifeCycleFact_timeDim_community_owned_time_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
    )
    closed_date_key = Column(
        VARCHAR(8),
        ForeignKey(
            DateDim.date_key,
            name="fk_questionPostLifeCycleFact_dateDim_closed_date_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
    )
    closed_time_key = Column(
        INTEGER,
        ForeignKey(
            TimeDim.time_key,
            name="fk_questionPostLifeCycleFact_timeDim_closed_time_key",
            onupdate="CASCADE",
            ondelete="NO ACTION",
        ),
    )
    created_to_first_activity_time_lag = Column(INTEGER)
    created_to_first_answer_time_lag = Column(INTEGER)
    first_activity_to_latest_activity_time_lag = Column(INTEGER)
    first_answer_to_accepted_answer_time_lag = Column(INTEGER)
    created_to_accepted_answer_time_lag = Column(INTEGER)
    created_to_community_owned_time_lag = Column(INTEGER)
    created_to_closed_time_lag = Column(INTEGER)
    view_count = Column(INTEGER, default=0)
    answer_count = Column(INTEGER, default=0)
    comment_count = Column(INTEGER, default=0)
    favorite_count = Column(INTEGER, default=0)
