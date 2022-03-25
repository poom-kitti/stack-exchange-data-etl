"""This module contains the schema to the `stats` database residing in MS SQL."""
from dataclasses import dataclass, field
from datetime import date, datetime

from sqlalchemy import DATE, INTEGER, TIMESTAMP, VARCHAR
from sqlalchemy.schema import ForeignKeyConstraint, PrimaryKeyConstraint

from . import AlchemyTable


@dataclass(frozen=True)
class Badges(AlchemyTable):
    table_name = "badges"
    table_constraints = [
        PrimaryKeyConstraint("badge_id", name="pk_badges"),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
            use_alter=True,
            name="fk_badges_users_user_id",
        ),
    ]

    badge_id: int = field(metadata={"name": "badge_id", "type_": INTEGER()})
    user_id: int = field(metadata={"name": "user_id", "type_": INTEGER()})
    name: str = field(metadata={"name": "bagde_name", "type_": VARCHAR()})
    granted_time: datetime = field(metadata={"name": "granted_time", "type_": TIMESTAMP()})


@dataclass(frozen=True)
class Comments(AlchemyTable):
    table_name = "comments"
    table_constraints = [
        PrimaryKeyConstraint("comment_id", name="pk_comments"),
        ForeignKeyConstraint(
            ["post_id"],
            ["posts.post_id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
            use_alter=True,
            name="fk_comments_posts_post_id",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            onupdate="CASCADE",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_comments_users_user_id",
        ),
    ]

    comment_id: int = field(metadata={"name": "comment_id", "type_": INTEGER()})
    post_id: int = field(metadata={"name": "post_id", "type_": INTEGER()})
    score: int = field(metadata={"name": "score", "type_": INTEGER()})
    text: str = field(metadata={"name": "text", "type_": VARCHAR()})
    created_time: datetime = field(metadata={"name": "created_time", "type_": TIMESTAMP()})
    user_id: datetime = field(metadata={"name": "user_id", "type_": TIMESTAMP()})
    user_display_name: str = field(metadata={"name": "user_display_name", "type_": VARCHAR()})


@dataclass(frozen=True)
class PostHistories(AlchemyTable):
    table_name = "post_histories"
    table_constraints = [
        PrimaryKeyConstraint("post_history_id", name="pk_postHistories"),
        ForeignKeyConstraint(
            ["post_id"],
            ["posts.post_id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
            use_alter=True,
            name="fk_postHistories_posts_post_id",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            onupdate="CASCADE",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_postHistories_users_user_id",
        ),
    ]

    post_history_id: int = field(metadata={"name": "post_history_id", "type_": INTEGER()})
    post_history_type_id: int = field(metadata={"name": "post_history_type_id", "type_": INTEGER()})
    post_id: int = field(metadata={"name": "post_id", "type_": INTEGER()})
    revision_guid: str = field(metadata={"name": "revision_guid", "type_": VARCHAR()})
    user_id: int = field(metadata={"name": "user_id", "type_": INTEGER()})
    user_display_name: str = field(metadata={"name": "user_id", "type_": VARCHAR()})
    text: str = field(metadata={"name": "text", "type_": VARCHAR()})
    comment: str = field(metadata={"name": "comment", "type_": VARCHAR()})
    created_time: datetime = field(metadata={"name": "created_time", "type_": TIMESTAMP()})


@dataclass(frozen=True)
class PostLinks(AlchemyTable):
    table_name = "post_links"
    table_constraints = [
        PrimaryKeyConstraint("post_link_id", name="pk_postLinks"),
        ForeignKeyConstraint(
            ["post_id"],
            ["posts.post_id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
            use_alter=True,
            name="fk_postLinks_posts_post_id",
        ),
    ]

    post_link_id: int = field(metadata={"name": "post_link_id", "type_": INTEGER()})
    link_type_id: int = field(metadata={"name": "link_type_id", "type_": INTEGER()})
    post_id: int = field(metadata={"name": "post_id", "type_": INTEGER()})
    related_post_id: int = field(metadata={"name": "related_post_id", "type_": INTEGER()})
    created_time: datetime = field(metadata={"name": "created_time", "type_": TIMESTAMP()})


@dataclass(frozen=True)
class Posts(AlchemyTable):
    table_name = "posts"
    table_constraints = [
        PrimaryKeyConstraint("post_id", name="pk_posts"),
        ForeignKeyConstraint(
            ["post_type_id"],
            ["users.user_id"],
            onupdate="CASCADE",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_posts_users_last_editor_user_id",
        ),
        ForeignKeyConstraint(
            ["accepted_answer_id"],
            ["post_id"],
            onupdate="CASCADE",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_posts_accepted_answer_id",
        ),
        ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.user_id"],
            onupdate="CASCADE",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_posts_users_owner_user_id",
        ),
        ForeignKeyConstraint(
            ["last_editor_user_id"],
            ["users.user_id"],
            onupdate="CASCADE",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_posts_users_last_editor_user_id",
        ),
    ]

    post_id: int = field(metadata={"name": "post_id", "type_": INTEGER()})
    post_type_id: int = field(metadata={"name": "post_type_id", "type_": INTEGER()})
    accepted_answer_id: int = field(metadata={"name": "accepted_answer_id", "type_": INTEGER()})
    title: str = field(metadata={"name": "title", "type_": VARCHAR()})
    body: str = field(metadata={"name": "body", "type_": VARCHAR()})
    score: int = field(metadata={"name": "score", "type_": INTEGER()})
    view_count: int = field(metadata={"name": "view_count", "type_": INTEGER()})
    answer_count: int = field(metadata={"name": "answer_count", "type_": INTEGER()})
    comment_count: int = field(metadata={"name": "comment_count", "type_": INTEGER()})
    favorite_count: int = field(metadata={"name": "favorite_count", "type_": INTEGER()})
    owner_user_id: int = field(metadata={"name": "owner_user_id", "type_": INTEGER()})
    owner_display_name: str = field(metadata={"name": "owner_display_name", "type_": VARCHAR()})
    last_editor_user_id: int = field(metadata={"name": "last_editor_user_id", "type_": INTEGER()})
    last_editor_display_name: str = field(metadata={"name": "last_editor_display_name", "type_": VARCHAR()})
    parent_id: int = field(metadata={"name": "parent_id", "type_": INTEGER()})
    created_time: datetime = field(metadata={"name": "created_time", "type_": TIMESTAMP()})
    last_activity_time: datetime = field(metadata={"name": "last_activity_time", "type_": TIMESTAMP()})
    last_edited_time: datetime = field(metadata={"name": "last_edited_time", "type_": TIMESTAMP()})
    community_owned_time: datetime = field(metadata={"name": "community_owned_time", "type_": TIMESTAMP()})
    closed_time: datetime = field(metadata={"name": "closed_time", "type_": TIMESTAMP()})


@dataclass(frozen=True)
class Tags(AlchemyTable):
    table_name = "tags"
    table_constraints = [
        PrimaryKeyConstraint("tag_id", name="pk_tags"),
        ForeignKeyConstraint(
            ["excerpt_post_id"],
            ["posts.post_id"],
            onupdate="CASCADE",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_tags_posts_excerpt_post_id",
        ),
        ForeignKeyConstraint(
            ["wiki_post_id"],
            ["posts.post_id"],
            onupdate="CASCADE",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_tags_posts_wiki_post_id",
        ),
    ]

    tag_id: int = field(metadata={"name": "tag_id", "type_": INTEGER()})
    tag_name: str = field(metadata={"name": "tag_name", "type_": VARCHAR()})
    count: int = field(metadata={"name": "count", "type_": INTEGER()})
    excerpt_post_id: int = field(metadata={"name": "excerpt_post_id", "type_": INTEGER()})
    wiki_post_id: int = field(metadata={"name": "wiki_post_id", "type_": INTEGER()})


@dataclass(frozen=True)
class Users(AlchemyTable):
    table_name = "users"
    table_constraints = [
        PrimaryKeyConstraint("user_id", name="pk_users"),
    ]

    user_id: int = field(metadata={"name": "user_id", "type_": INTEGER()})
    account_id: int = field(metadata={"name": "account_id", "type_": INTEGER()})
    display_name: str = field(metadata={"name": "display_name", "type_": VARCHAR()})
    age: int = field(metadata={"name": "age", "type_": INTEGER()})
    website_url: str = field(metadata={"name": "website_url", "type_": VARCHAR()})
    profile_img_url: str = field(metadata={"name": "profile_img_url", "type_": VARCHAR()})
    location: str = field(metadata={"name": "location", "type_": VARCHAR()})
    about_me: str = field(metadata={"name": "about_me", "type_": VARCHAR()})
    reputation: int = field(metadata={"name": "reputation", "type_": INTEGER()})
    views: int = field(metadata={"name": "views", "type_": INTEGER()})
    up_votes: int = field(metadata={"name": "up_votes", "type_": INTEGER()})
    down_votes: int = field(metadata={"name": "down_votes", "type_": INTEGER()})
    created_time: datetime = field(metadata={"name": "created_time", "type_": TIMESTAMP()})
    last_accessed_time: datetime = field(metadata={"name": "last_accessed_time", "type_": TIMESTAMP()})


@dataclass(frozen=True)
class Votes(AlchemyTable):
    table_name = "votes"
    table_constraints = [
        PrimaryKeyConstraint("vote_id", name="pk_votes"),
        ForeignKeyConstraint(
            ["post_id"],
            ["posts.post_id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
            use_alter=True,
            name="fk_votes_posts_post_id",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
            use_alter=True,
            name="fk_votes_users_user_id",
        ),
    ]

    vote_id: int = field(metadata={"name": "vote_id", "type_": INTEGER()})
    vote_type_id: int = field(metadata={"name": "vote_type_id", "type_": INTEGER()})
    post_id: int = field(metadata={"name": "post_id", "type_": INTEGER()})
    user_id: int = field(metadata={"name": "user_id", "type_": INTEGER()})
    bounty_amount: int = field(metadata={"name": "bounty_amount", "type_": INTEGER()})
    created_date: date = field(metadata={"name": "created_time", "type_": DATE()})
