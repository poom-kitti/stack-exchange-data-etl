from pyspark.sql import Row, SparkSession, Window
from pyspark.sql import functions as F

from ..schemas import stats_pyspark_schema as schema
from ..schemas.stats_schema import (Badges, Comments, PostHistoryTypes,
                                    PostHitories, PostLinks, PostLinkTypes,
                                    Posts, PostsAnswers, PostsTags, PostTypes,
                                    Tags, Users, UsersBadges, Votes, VoteTypes)
from ..utils import pyspark_utils
from ..utils.pyspark_utils import JDBCConnectionConfig


def load_users_table(
    spark: SparkSession, source_db_config: JDBCConnectionConfig, destination_db_config: JDBCConnectionConfig
) -> None:
    """Load the `users` table from source to destination database.

    Transformations:
        - Change datetime type (timezone unaware) for `CreationDate` and `LastAccessDate` columns to
            timestamp (timezone aware).
    """
    # Read
    ori_df = pyspark_utils.read_db_table(spark, source_db_config, Users.get_table_name(), {"fetchsize": "10000"})

    # Transform
    users_df = pyspark_utils.from_datetime_to_timestamp(ori_df, "CreationDate", "LastAccessDate")

    # Select
    users_df = pyspark_utils.rename_columns(users_df, schema.users_rename_columns_mapping)
    users_df = Users.select_from_df(users_df)

    pyspark_utils.write_df_to_db_table(
        users_df, destination_db_config, Users.get_table_name(), additional_options={"batchsize": "10000"}
    )


def load_badges_table(
    spark: SparkSession, source_db_config: JDBCConnectionConfig, destination_db_config: JDBCConnectionConfig
) -> None:
    """Derive `badges` table from source and load into destination database.

    Transformations:
        - A badge is a unique badge name in the `badges` table from source database.
        - `badge_id` column will be generated with pyspark, but the id is not guaranteed to be
            sequential.
    """
    # Read
    ori_df = pyspark_utils.read_db_table(spark, source_db_config, "badges", {"fetchsize": "10000"})

    # Transform
    badges_df = ori_df.select("Name").distinct()
    # monotonically_increasing_id() starts from 0, but desire id starting from 1
    badges_df = badges_df.withColumn("badge_id", F.monotonically_increasing_id() + 1)

    # Select
    badges_df = pyspark_utils.rename_columns(badges_df, schema.badges_rename_columns_mapping)

    pyspark_utils.write_df_to_db_table(badges_df, destination_db_config, Badges.get_table_name())


def load_users_badges_table(
    spark: SparkSession, source_db_config: JDBCConnectionConfig, destination_db_config: JDBCConnectionConfig
) -> None:
    """Derive `users_badges` table from source and load into destination database.

    Transformations:
        - Refer to the badge using `badge_id` instead.
        - Change `Date` column from datetime (timezone unaware) to timestamp (timezone aware).
    """
    # Read
    ori_df = pyspark_utils.read_db_table(spark, source_db_config, "badges")
    badges_df = pyspark_utils.read_db_table(
        spark, destination_db_config, Badges.get_table_name()
    )  # Info on badge_id and name

    # Transform
    users_badges_df = ori_df.join(badges_df, on=ori_df["Name"] == badges_df[Badges.name.name])
    users_badges_df = users_badges_df.withColumn(UsersBadges.badge_granted_id.name, F.monotonically_increasing_id() + 1)
    users_badges_df = pyspark_utils.from_datetime_to_timestamp(users_badges_df, "Date")

    # Select
    users_badges_df = pyspark_utils.rename_columns(users_badges_df, schema.users_badges_rename_columns_mapping)
    users_badges_df = UsersBadges.select_from_df(users_badges_df)

    pyspark_utils.write_df_to_db_table(users_badges_df, destination_db_config, UsersBadges.get_table_name())


def load_post_types_table(spark: SparkSession, destination_db_config: JDBCConnectionConfig) -> None:
    """Derive the `post_types` table from source and load into destination database.

    Transformations:
        - Manually add designated rows. The definition of the post type is a guess from
            doing data exploration.
        - PostTypeId = 3, 4, and 6 are ignored as they are connected with tags and will
            be derived later (Signify `Tag info for generic tag`, `Tag excerpt`, and `Tag wiki page`,
          accordingly).
        - PostTypeId = 6 and 7 are ignored as they are connected to Cross Validated team
            (Signify `Message from modulators` and `Cross Validated site info`, accordingly)
    """
    post_types_df = spark.createDataFrame(
        [
            Row(post_type_id=1, name="Question", description="The question post."),
            Row(post_type_id=2, name="Answer", description="The answer to a question post."),
        ]
    )

    pyspark_utils.write_df_to_db_table(post_types_df, destination_db_config, PostTypes.get_table_name())


def load_posts_table(
    spark: SparkSession, source_db_config: JDBCConnectionConfig, destination_db_config: JDBCConnectionConfig
) -> None:
    """Load `posts` table from source and load into destination database.

    Transformations:
        - Only select rows that are questions or anwers
        - Change `CreaionDate`, `LasActivityDate`, `LastEditDate`, `CommunityOwnedDate` and `ClosedDate` columns
            from datetime (timezone unaware) to timestamp (timezone aware).
    """
    # Read
    ori_df = pyspark_utils.read_db_table(spark, source_db_config, "posts", {"fetchsize": "10000"})

    # Transform
    posts_df = ori_df.where((F.col("PostTypeId") == 1) | (F.col("PostTypeId") == 2))
    posts_df = pyspark_utils.from_datetime_to_timestamp(
        posts_df, "CreaionDate", "LasActivityDate", "LastEditDate", "CommunityOwnedDate", "ClosedDate"
    )

    # Select
    posts_df = pyspark_utils.rename_columns(posts_df, schema.posts_rename_columns_mapping)
    posts_df = Posts.select_from_df(posts_df)

    pyspark_utils.write_df_to_db_table(
        posts_df, destination_db_config, Posts.get_table_name(), additional_options={"batchsize": "10000"}
    )


def load_posts_answers_table(
    spark: SparkSession, source_db_config: JDBCConnectionConfig, destination_db_config: JDBCConnectionConfig
) -> None:
    """Derive `posts_answers` table from source and load into destination database.

    Transformations:
        - Derive relationship between question and answer posts
        - Derive whether an answer post is the accepted answer
        - Change `CreaionDate` column from datetime (timezone unaware) to timestamp (timezone aware).
    """
    # Read
    ori_df = pyspark_utils.read_db_table(spark, source_db_config, "posts", {"fetchsize": "10000"})

    # Transform
    # Filter only answer posts
    posts_answers_df = ori_df.where(F.col("PostTypeId") == 2).select("Id", "ParentId", "CreaionDate")
    posts_answers_df = pyspark_utils.from_datetime_to_timestamp(posts_answers_df, "CreaionDate")
    # Filter accepted answers
    accpeted_answers_df = ori_df.where(F.col("AcceptedAnswerId").isNotNull()).select("AcceptedAnswerId")
    # Find whether answer is accepted answer
    posts_answers_df = posts_answers_df.join(
        accpeted_answers_df, on=posts_answers_df["Id"] == accpeted_answers_df["AcceptedAnswerId"], how="left"
    )
    posts_answers_df = posts_answers_df.withColumn("is_accepted_answer", F.col("AcceptedAnswerId").isNotNull())

    # Select
    posts_answers_df = pyspark_utils.rename_columns(posts_answers_df, schema.posts_answers_columns_mapping)
    posts_answers_df = PostsAnswers.select_from_df(posts_answers_df)

    pyspark_utils.write_df_to_db_table(
        posts_answers_df,
        destination_db_config,
        PostsAnswers.get_table_name(),
        additional_options={"batchsize": "10000"},
    )


def load_comments_table(
    spark: SparkSession, source_db_config: JDBCConnectionConfig, destination_db_config: JDBCConnectionConfig
) -> None:
    """Load `comments` table from source and load into destination database.

    Transformations:
        - Remove any comments that are not related to question or answer posts.
        - Change `CreationDate` column from datetime (timezone unaware) to timestamp (timezone aware).
    """
    # Read
    ori_df = pyspark_utils.read_db_table(spark, source_db_config, "comments", additional_options={"fetchsize": "10000"})
    posts_df = pyspark_utils.read_db_table(
        spark, destination_db_config, Posts.get_table_name(), additional_options={"fetchsize": "10000"}
    )

    # Transform
    # Remove rows that refer to non-existing posts
    comments_df = ori_df.join(posts_df, on=ori_df["PostId"] == posts_df[Posts.post_id.name], how="semi")
    comments_df = pyspark_utils.from_datetime_to_timestamp(comments_df, "CreationDate")

    # Select
    comments_df = pyspark_utils.rename_columns(comments_df, schema.comments_columns_mapping)

    pyspark_utils.write_df_to_db_table(
        comments_df,
        destination_db_config,
        Comments.get_table_name(),
        additional_options={"batchsize": "10000"},
    )


def load_tags_table(
    spark: SparkSession, source_db_config: JDBCConnectionConfig, destination_db_config: JDBCConnectionConfig
) -> None:
    """Load `tags` table from source and load into destination database.

    Transformations:
        - Get the tag's excerpt from the `posts` table (excerpt post) in source database.
        - Get the tag's description from the `posts` table (wiki post) in source database.
    """
    # Read
    ori_tags_df = pyspark_utils.read_db_table(spark, source_db_config, "tags").alias("tags")
    ori_posts_df = pyspark_utils.read_db_table(spark, source_db_config, "posts", {"fetchsize": "10000"})

    # Transform
    tags_df = ori_tags_df.join(
        ori_posts_df.alias("excerpt"), on=ori_tags_df["ExcerptPostId"] == ori_posts_df["Id"], how="left"
    ).select("tags.*", F.col("excerpt.body").alias(Tags.excerpt.name))
    tags_df = (
        tags_df.alias("tags")
        .join(ori_posts_df.alias("wiki"), on=ori_tags_df["WikiPostId"] == ori_posts_df["Id"], how="left")
        .select("tags.*", F.col("wiki.body").alias(Tags.description.name))
    )

    # Select
    tags_df = pyspark_utils.rename_columns(tags_df, schema.tags_columns_mapping)
    tags_df = Tags.select_from_df(tags_df)

    pyspark_utils.write_df_to_db_table(
        tags_df,
        destination_db_config,
        Tags.get_table_name(),
    )


def load_posts_tags_table(
    spark: SparkSession, source_db_config: JDBCConnectionConfig, destination_db_config: JDBCConnectionConfig
) -> None:
    """Derive `posts_tags` table from source and load into destination database.

    Transformations:
        - Get the latest tags from `postHistory.Text` and expand to multiple rows, where
            each row has a single tag name.
        - Refer the tag name to the correct tag_id. Remove the tag if it does not exists
          in `tags` table.
        - Change `postHistory.CreationDate` column from datetime (timezone unaware) to
            timestamp (timezone aware).
    """
    # Read
    ori_post_hist_df = pyspark_utils.read_db_table(spark, source_db_config, "posthistory", {"fetchsize": "10000"})
    tags_df = pyspark_utils.read_db_table(spark, destination_db_config, Tags.get_table_name())

    # Transform
    # Get latest changes to post tags for question posts.
    # postHistory.postHistoryTypeId = 3 for initial tags, 6 for edited tags
    post_id_window = Window.partitionBy(F.col("PostId")).orderBy(F.col("CreationDate").desc())
    posts_tags_df = ori_post_hist_df.where(F.col("PostHistoryTypeId").isin([3, 6])).withColumn(
        "row_number", F.row_number().over(post_id_window)
    )
    posts_tags_df = posts_tags_df.where(F.col("row_number") == 1)
    # Replace the tags to comma separated tag names
    # e.g., "<tag_a> <tag_b>" --> "tag_a>tag_b>" --> "tag_a,tag_b"
    posts_tags_df = posts_tags_df.withColumn(
        "tag_name", F.regexp_replace(F.regexp_replace("Text", "[\\s]{0,}<", ""), ">", ",")
    )
    # Make the tags into list (e.g., ["tag_a", "tag_b"])
    posts_tags_df = posts_tags_df.withColumn("tag_name", F.split("tag_name", ","))
    # Expand each tag value to individual row
    posts_tags_df = posts_tags_df.withColumn("tag_name", F.explode("tag_name"))
    posts_tags_df = posts_tags_df.join(tags_df, on=posts_tags_df["tag_name"] == tags_df[Tags.name.name])

    # Deal with datetime
    posts_tags_df = pyspark_utils.from_datetime_to_timestamp(posts_tags_df, "CreationDate")

    # Select
    posts_tags_df = pyspark_utils.rename_columns(posts_tags_df, schema.posts_tags_columns_mapping)
    posts_tags_df = PostsTags.select_from_df(posts_tags_df)

    pyspark_utils.write_df_to_db_table(
        posts_tags_df,
        destination_db_config,
        PostsTags.get_table_name(),
        additional_options={"batchsize": "10000"},
    )


def load_vote_types_table(spark: SparkSession, destination_db_config: JDBCConnectionConfig) -> None:
    """Derive the `vote_types` table from source and load into destination database.

    Transformations:
        - Manually add designated rows. The definition of the vote type is a guess from
            doing data exploration.
        - VoteTypeId = 1, 6, 7, 9, 10, 11, 15, and 16 will be ignored as not enough
            information to guess what they are.
    """
    vote_types_df = spark.createDataFrame(
        [
            Row(vote_type_id=2, name="Upvote", description="Upvote a question or answer post."),
            Row(vote_type_id=3, name="Downvote", description="Downvote a question or answer post."),
            Row(vote_type_id=5, name="Favorite", description="Add a question or answer post as favorite."),
            Row(vote_type_id=8, name="Bounty", description="Place a bounty on a question post."),
        ]
    )

    pyspark_utils.write_df_to_db_table(
        vote_types_df,
        destination_db_config,
        VoteTypes.get_table_name(),
    )


def load_votes_table(
    spark: SparkSession, source_db_config: JDBCConnectionConfig, destination_db_config: JDBCConnectionConfig
) -> None:
    """Load `votes` table from source and load into destination database.

    Transformations:
        - Remove posts that are not question or answer posts.
        - Remove unwanted `VoteTypeId`.
        - Change `CreationDate` column from datetime (timezone unaware) to timestamp (timezone aware).
    """
    # Read
    ori_df = pyspark_utils.read_db_table(spark, source_db_config, "votes", {"fetchsize": "10000"})
    vote_types_df = pyspark_utils.read_db_table(spark, destination_db_config, VoteTypes.get_table_name())
    posts_df = pyspark_utils.read_db_table(spark, destination_db_config, Posts.get_table_name(), {"fetchsize": "10000"})

    # Transform
    votes_df = ori_df.join(
        F.broadcast(vote_types_df), on=ori_df["VoteTypeId"] == vote_types_df[VoteTypes.vote_type_id.name], how="semi"
    )
    votes_df = votes_df.join(posts_df, on=votes_df["PostId"] == posts_df[Posts.post_id.name], how="semi")
    votes_df = pyspark_utils.from_datetime_to_timestamp(votes_df, "CreationDate")

    # Select
    votes_df = pyspark_utils.rename_columns(votes_df, schema.votes_columns_mapping)

    pyspark_utils.write_df_to_db_table(
        votes_df,
        destination_db_config,
        Votes.get_table_name(),
        additional_options={"batchsize": "10000"},
    )


def load_post_link_types_table(spark: SparkSession, destination_db_config: JDBCConnectionConfig) -> None:
    """Derive the `post_link_types` table from source and load into destination database.

    Transformations:
        - Manually add designated rows. The definition of the post link type is a guess from
            doing data exploration.
    """
    post_link_types = spark.createDataFrame(
        [
            Row(link_type_id=1, name="Related", description="The question post is related to another question post."),
            Row(
                link_type_id=3,
                name="Duplicate",
                description="The question post is a possible duplicate of another question post.",
            ),
        ]
    )

    pyspark_utils.write_df_to_db_table(
        post_link_types,
        destination_db_config,
        PostLinkTypes.get_table_name(),
    )


def load_post_links_table(
    spark: SparkSession, source_db_config: JDBCConnectionConfig, destination_db_config: JDBCConnectionConfig
) -> None:
    """Load `post_links` table from source and load into destination database.

    Transformations:
        - Remove links to posts that are not question or answer posts.
        - Change `CreationDate` column from datetime (timezone unaware) to timestamp (timezone aware).
    """
    # Read
    ori_df = pyspark_utils.read_db_table(spark, source_db_config, "postLinks")
    posts_df = pyspark_utils.read_db_table(spark, destination_db_config, Posts.get_table_name(), {"fetchsize": "10000"})

    # Transform
    post_links_df = ori_df.join(posts_df, on=ori_df["PostId"] == posts_df[Posts.post_id.name], how="semi")
    post_links_df = post_links_df.join(
        posts_df, on=post_links_df["RelatedPostId"] == posts_df[Posts.post_id.name], how="semi"
    )
    post_links_df = pyspark_utils.from_datetime_to_timestamp(post_links_df, "CreationDate")

    # Select
    post_links_df = pyspark_utils.rename_columns(post_links_df, schema.post_links_columns_mapping)

    pyspark_utils.write_df_to_db_table(
        post_links_df,
        destination_db_config,
        PostLinks.get_table_name(),
    )


def load_post_history_types_table(spark: SparkSession, destination_db_config: JDBCConnectionConfig) -> None:
    """Derive the `post_history_types` table from source and load into destination database.

    Transformations:
        - Manually add designated rows. The definition of the post history type is a guess from
            doing data exploration.
        - PostHistoryTypeId = 14, 15 and 19 will be ignored as not enough information to
            guess what they are.
    """
    post_history_types_df = spark.createDataFrame(
        [
            Row(post_history_type_id=1, name="Initiate Title", description="Initiate title when post first created."),
            Row(post_history_type_id=2, name="Initiate Body", description="Initiate body when post first created."),
            Row(post_history_type_id=3, name="Initiate Tags", description="Initiate tags when post first created."),
            Row(post_history_type_id=4, name="Edit Title", description="Edit the post's title."),
            Row(post_history_type_id=5, name="Edit Body", description="Edit the post's body."),
            Row(post_history_type_id=6, name="Edit Tags", description="Edit the post's tags."),
            Row(
                post_history_type_id=7,
                name="Rollback Title",
                description="Rollback the post's title edit to a certain commit.",
            ),
            Row(
                post_history_type_id=8,
                name="Rollback Body",
                description="Rollback the post's body edit to a certain commit.",
            ),
            Row(
                post_history_type_id=9,
                name="Rollback Tags",
                description="Rollback the post's tags edit to a certain commit.",
            ),
            Row(post_history_type_id=10, name="Close Question", description="Close the question post."),
            Row(post_history_type_id=11, name="Reopen Question", description="Reopen the question post."),
            Row(post_history_type_id=12, name="Close Answer", description="Close the answer post."),
            Row(post_history_type_id=13, name="Reopen Answer", description="Reopen the answer post."),
            Row(
                post_history_type_id=16, name="Community Owned", description="Transfer the post to be community owned."
            ),
            Row(
                post_history_type_id=24,
                name="Approve Proposed Edit",
                description="Approved the edit proposed by another user.",
            ),
            Row(post_history_type_id=25, name="Post Twitter", description="Post the question post to Twitter."),
            Row(post_history_type_id=33, name="Accept Answer", description="Accept an answer for a question post."),
            Row(
                post_history_type_id=34,
                name="Change Accepted Answer",
                description="Change the accepted answer for a question post.",
            ),
            Row(
                post_history_type_id=35,
                name="Transfer To Other Stack Overflow Page",
                description="Transfer the question post to another Stack Overflow page.",
            ),
            Row(
                post_history_type_id=36,
                name="Get From Other Stack Overflow Page",
                description="Get the question post from another Stack Overflow page.",
            ),
            Row(
                post_history_type_id=37,
                name="Transfer To Stats.StackExchange",
                description="Transfer the question post to stats.statexchange.",
            ),
            Row(
                post_history_type_id=38,
                name="Get From Stats.StackExchange",
                description="Get the question post from stats.statexchange.",
            ),
        ]
    )

    pyspark_utils.write_df_to_db_table(
        post_history_types_df,
        destination_db_config,
        PostHistoryTypes.get_table_name(),
    )


def load_post_histories_table(
    spark: SparkSession, source_db_config: JDBCConnectionConfig, destination_db_config: JDBCConnectionConfig
) -> None:
    """Load `post_histories` table from source and load into destination database.

    Transformations:
        - Remove post history of an unknown post history type.
        - Remove histories of posts that are not question or answer posts.
        - Replace empty `UserDisplayName` with NULL.
        - Change `CreationDate` column from datetime (timezone unaware) to timestamp (timezone aware).
    """
    # Read
    ori_df = pyspark_utils.read_db_table(spark, source_db_config, "postHistory", {"fetchsize": "10000"})
    post_history_types_df = pyspark_utils.read_db_table(spark, destination_db_config, PostHistoryTypes.get_table_name())
    posts_df = pyspark_utils.read_db_table(spark, destination_db_config, Posts.get_table_name(), {"fetchsize": "10000"})

    # Transform
    post_histories_df = ori_df.join(
        F.broadcast(post_history_types_df),
        on=ori_df["PostHistoryTypeId"] == post_history_types_df[PostHistoryTypes.post_history_type_id.name],
        how="semi",
    )
    post_histories_df = post_histories_df.join(
        posts_df, on=post_histories_df["PostId"] == posts_df[Posts.post_id.name], how="semi"
    )
    post_histories_df = post_histories_df.withColumn(
        "UserDisplayName", F.when(F.col("UserDisplayName") != "", F.col("UserDisplayName")).otherwise(None)
    )
    post_histories_df = pyspark_utils.from_datetime_to_timestamp(post_histories_df, "CreationDate")

    # Select
    post_histories_df = pyspark_utils.rename_columns(post_histories_df, schema.post_histories_columns_mapping)

    pyspark_utils.write_df_to_db_table(
        post_histories_df,
        destination_db_config,
        PostHitories.get_table_name(),
        additional_options={"batchsize": "10000"},
    )
