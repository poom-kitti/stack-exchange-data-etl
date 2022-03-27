"""This module contains the SQLAlchemy schema of the wanted tables in the destination
database."""
from sqlalchemy import BOOLEAN, INTEGER, TIMESTAMP, VARCHAR, Column, ForeignKey
from sqlalchemy.schema import MetaData
from sqlalchemy.sql import functions as func

from . import Base


# Declarative base class
class BaseStats(Base):
    """A base class for wanted tables in `stats` destination database."""

    __abstract__ = True
    metadata = MetaData()


class Users(BaseStats):
    """A metaclass for `users` table."""

    __tablename__ = "users"

    user_id = Column(INTEGER, primary_key=True, autoincrement=False)
    display_id = Column(INTEGER)
    display_name = Column(VARCHAR(255), nullable=False)
    age = Column(INTEGER)
    about_me = Column(VARCHAR(None))
    location = Column(VARCHAR(255))
    website_url = Column(VARCHAR(255))
    profile_image_url = Column(VARCHAR(255))
    reputation = Column(INTEGER, default=0)
    views = Column(INTEGER, default=0)
    upvotes = Column(INTEGER, default=0)
    downvotes = Column(INTEGER, default=0)
    created_time = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_accessed_time = Column(TIMESTAMP(timezone=True))


class Badges(BaseStats):
    """A metaclass for `badges` table."""

    __tablename__ = "badges"

    badge_id = Column(INTEGER, primary_key=True, autoincrement=False)
    name = Column(VARCHAR(255), nullable=False)


class UsersBadges(BaseStats):
    """A metaclass for `users_badges` table."""

    __tablename__ = "users_badges"

    badge_granted_id = Column(INTEGER, primary_key=True, autoincrement=False)
    user_id = Column(
        INTEGER,
        ForeignKey(Users.user_id, name="fk_usersBadges_users_user_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    badge_id = Column(
        INTEGER,
        ForeignKey(Badges.badge_id, name="fk_usersBadges_badges_badge_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    granted_time = Column(TIMESTAMP(timezone=True), server_default=func.now())


class PostTypes(BaseStats):
    """A metaclass for `post_types` table."""

    __tablename__ = "post_types"

    post_type_id = Column(INTEGER, primary_key=True, autoincrement=False)
    name = Column(VARCHAR(255), nullable=False)
    description = Column(VARCHAR(None))


class Posts(BaseStats):
    """A metaclass for `posts` table."""

    __tablename__ = "posts"

    post_id = Column(INTEGER, primary_key=True, autoincrement=False)
    post_type_id = Column(
        INTEGER,
        ForeignKey(
            PostTypes.post_type_id,
            name="fk_posts_postTypes_post_type_id",
            use_alter=True,
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        nullable=False,
    )
    owner_user_id = Column(
        INTEGER,
        ForeignKey(
            Users.user_id, name="fk_posts_users_owner_user_id", use_alter=True, onupdate="CASCADE", ondelete="SET NULL"
        ),
    )
    owner_diplay_name = Column(VARCHAR(255))
    title = Column(VARCHAR(None))
    body = Column(VARCHAR(None))
    score = Column(INTEGER, default=0)
    view_count = Column(INTEGER, default=0)
    answer_count = Column(INTEGER, default=0)
    comment_count = Column(INTEGER, default=0)
    favorite_count = Column(INTEGER, default=0)
    last_editor_user_id = Column(
        INTEGER,
        ForeignKey(
            Users.user_id,
            name="fk_posts_users_last_editor_user_id",
            use_alter=True,
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
    )
    last_editor_display_name = Column(VARCHAR(255))
    created_time = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_activity_time = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    last_edited_time = Column(TIMESTAMP(timezone=True))
    community_owned_time = Column(TIMESTAMP(timezone=True))
    closed_time = Column(TIMESTAMP(timezone=True))


class PostsAnswers(BaseStats):
    """A metaclass for `posts_answers` table."""

    __tablename__ = "posts_answers"

    post_id = Column(
        INTEGER,
        ForeignKey(Posts.post_id, name="fk_postsAnswers_posts_post_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )
    answer_post_id = Column(
        INTEGER,
        ForeignKey(Posts.post_id, name="fk_postsAnswers_posts_answer_post_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )
    is_accepted_answer = Column(BOOLEAN, default=False)
    answered_time = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Comments(BaseStats):
    """A metaclass for `comments` table."""

    __tablename__ = "comments"

    comment_id = Column(INTEGER, primary_key=True, autoincrement=False)
    post_id = Column(
        INTEGER,
        ForeignKey(
            Posts.post_id, name="fk_comments_posts_post_id", use_alter=True, onupdate="CASCADE", ondelete="CASCADE"
        ),
    )
    user_id = Column(
        INTEGER,
        ForeignKey(
            Users.user_id, name="fk_comments_users_user_id", use_alter=True, onupdate="CASCADE", ondelete="SET NULL"
        ),
    )
    user_display_name = Column(VARCHAR(255))
    body = Column(VARCHAR(None))
    score = Column(INTEGER, default=0)
    created_time = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Tags(BaseStats):
    """A metaclass for `tags` table."""

    __tablename__ = "tags"

    tag_id = Column(INTEGER, primary_key=True, autoincrement=False)
    name = Column(VARCHAR(255), nullable=False)
    usage_count = Column(INTEGER, default=0)
    excerpt = Column(VARCHAR(None))
    description = Column(VARCHAR(None))


class PostsTags(BaseStats):
    """A metaclass for `posts_tags` table."""

    __tablename__ = "posts_tags"

    post_id = Column(
        INTEGER,
        ForeignKey(Posts.post_id, name="fk_postsTags_posts_post_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )
    tag_id = Column(
        INTEGER,
        ForeignKey(Tags.tag_id, name="fk_postsTags_tags_tag_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )
    tagged_time = Column(TIMESTAMP(timezone=True), server_default=func.now())


class VoteTypes(BaseStats):
    """A metaclass for `vote_types` table."""

    __tablename__ = "vote_types"

    vote_type_id = Column(INTEGER, primary_key=True, autoincrement=False)
    name = Column(VARCHAR(255), nullable=False)
    description = Column(VARCHAR(None))


class Votes(BaseStats):
    """A metaclass for `votes` table."""

    __tablename__ = "votes"

    vote_id = Column(INTEGER, primary_key=True, autoincrement=False)
    user_id = Column(
        INTEGER, ForeignKey(Users.user_id, name="fk_votes_users_user_id", onupdate="CASCADE", ondelete="CASCADE")
    )
    post_id = Column(
        INTEGER, ForeignKey(Posts.post_id, name="fk_votes_posts_post_id", onupdate="CASCADE", ondelete="CASCADE")
    )
    vote_type_id = Column(
        INTEGER,
        ForeignKey(
            VoteTypes.vote_type_id, name="fk_votes_voteTypes_vote_type_id", onupdate="CASCADE", ondelete="CASCADE"
        ),
    )
    bounty_amount = Column(INTEGER)
    created_time = Column(TIMESTAMP(timezone=True), server_default=func.now())


class PostLinkTypes(BaseStats):
    """A metaclass for `post_link_types` table."""

    __tablename__ = "post_link_types"

    link_type_id = Column(INTEGER, primary_key=True, autoincrement=False)
    name = Column(VARCHAR(255), nullable=False)
    description = Column(VARCHAR(None))


class PostLinks(BaseStats):
    """A metaclass for `post_links` table."""

    __tablename__ = "post_links"

    post_link_id = Column(INTEGER, primary_key=True, autoincrement=False)
    link_type_id = Column(
        INTEGER,
        ForeignKey(
            PostLinkTypes.link_type_id,
            name="fk_postLinks_postLinkTypes_link_type_id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
    )
    post_id = Column(
        INTEGER, ForeignKey(Posts.post_id, name="fk_postLinks_posts_post_id", onupdate="CASCADE", ondelete="CASCADE")
    )
    related_post_id = Column(
        INTEGER,
        ForeignKey(Posts.post_id, name="fk_postLinks_post_related_post_id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    created_time = Column(TIMESTAMP(timezone=True), server_default=func.now())


class PostHistoryTypes(BaseStats):
    """A metaclass for `post_history_types` table."""

    __tablename__ = "post_history_types"

    post_history_type_id = Column(INTEGER, primary_key=True, autoincrement=False)
    name = Column(VARCHAR(255), nullable=False)
    description = Column(VARCHAR(None))


class PostHitories(BaseStats):
    """A metaclass for `post_histories` table."""

    __tablename__ = "post_histories"

    post_history_id = Column(INTEGER, primary_key=True, autoincrement=False)
    post_history_type_id = Column(
        INTEGER,
        ForeignKey(
            PostHistoryTypes.post_history_type_id,
            name="fk_postHistories_postHistoryTypes_post_history_type_id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
    )
    revision_guid = Column(VARCHAR(255), nullable=False)
    user_id = Column(
        INTEGER,
        ForeignKey(Users.user_id, name="fk_postHistories_users_user_id", onupdate="CASCADE", ondelete="SET NULL"),
    )
    user_display_name = Column(VARCHAR(255))
    post_id = Column(
        INTEGER,
        ForeignKey(Posts.post_id, name="fk_postHistories_posts_post_id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    text = Column(VARCHAR(None))
    comment = Column(VARCHAR(None))
    created_time = Column(TIMESTAMP(timezone=True), server_default=func.now())
