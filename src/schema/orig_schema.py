"""This module contains the schema of the original `stats` database from MariaDB."""
from pyspark.sql.types import (DateType, IntegerType, StringType, StructField,
                               StructType, TimestampType)

table_names = ["badges", "comments", "postHistory", "postLinks", "posts", "tags", "users", "votes"]

badges_schema = StructType(
    [
        StructField("Id", IntegerType(), False),
        StructField("UserId", IntegerType()),
        StructField("Name", StringType()),
        StructField("Date", TimestampType()),  # datetime
    ]
)

comments_schema = StructType(
    [
        StructField("Id", IntegerType(), False),
        StructField("PostId", IntegerType()),
        StructField("Score", IntegerType()),
        StructField("Text", StringType()),  # longtext
        StructField("CreationDate", TimestampType()),  # datetime
        StructField("UserId", IntegerType()),
        StructField("UserDisplayName", StringType()),
    ]
)

post_history_schema = StructType(
    [
        StructField("Id", IntegerType(), False),
        StructField("PostHistoryTypeId", IntegerType()),
        StructField("PostId", IntegerType()),
        StructField("RevisionGUID", StringType()),
        StructField("CreationDate", TimestampType()),  # datetime
        StructField("UserId", IntegerType()),
        StructField("Text", StringType()),  # longtext
        StructField("Comment", StringType()),  # text
        StructField("UserDisplayName", StringType()),
    ]
)

post_links_schema = StructType(
    [
        StructField("Id", IntegerType(), False),
        StructField("CreationDate", TimestampType()),  # datetime
        StructField("PostId", IntegerType()),
        StructField("RelatedPostId", IntegerType()),
        StructField("LinkTypeId", IntegerType()),
    ]
)

posts_schema = StructType(
    [
        StructField("Id", IntegerType(), False),
        StructField("PostTypeId", IntegerType()),
        StructField("AcceptedAnserId", IntegerType()),
        StructField("CreaionDate", TimestampType()),  # datetime
        StructField("Score", IntegerType()),
        StructField("ViewCount", IntegerType()),
        StructField("Body", StringType()),  # longtext
        StructField("OwnerUserId", IntegerType()),
        StructField("LasActivityDate", TimestampType()),  # datetime
        StructField("Title", StringType()),
        StructField("Tags", StringType()),
        StructField("AnswerCount", IntegerType()),
        StructField("CommentCount", IntegerType()),
        StructField("FavoriteCount", IntegerType()),
        StructField("LastEditorUserId", IntegerType()),
        StructField("LastEditDate", TimestampType()),  # datetime
        StructField("CommunityOwnedDate", TimestampType()),  # datetime
        StructField("ParentId", IntegerType()),
        StructField("ClosedDate", TimestampType()),  # datetime
        StructField("OwnerDisplayName", StringType()),
        StructField("LastEditorDisplayName", StringType()),
    ]
)

tags_schema = StructType(
    [
        StructField("Id", IntegerType(), False),
        StructField("TagName", StringType()),
        StructField("Count", IntegerType()),
        StructField("ExcerptPostId", IntegerType()),
        StructField("WikiPostId", IntegerType()),
    ]
)

users_schema = StructType(
    [
        StructField("Id", IntegerType(), False),
        StructField("Reputation", IntegerType()),
        StructField("CreationDate", TimestampType()),  # datetime
        StructField("DisplayName", StringType()),
        StructField("LastAccessDate", TimestampType()),  # datetime
        StructField("WebsiteUrl", StringType()),
        StructField("Location", StringType()),
        StructField("AboutMe", StringType()),  # longtext
        StructField("Views", IntegerType()),
        StructField("UpVotes", IntegerType()),
        StructField("DownVotes", IntegerType()),
        StructField("AccountId", IntegerType()),
        StructField("Age", IntegerType()),
        StructField("ProfileImageUrl", StringType()),
    ]
)

votes_schema = StructType(
    [
        StructField("Id", IntegerType(), False),
        StructField("PostId", IntegerType()),
        StructField("VoteTypeId", IntegerType()),
        StructField("CreationDate", DateType()),
        StructField("UserId", IntegerType()),
        StructField("BountyAmount", IntegerType()),
    ]
)
