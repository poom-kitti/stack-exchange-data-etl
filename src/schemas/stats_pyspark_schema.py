"""This module contains information to be used when modifying dataframes in
pyspark to get the desired schema in the destination database."""
from .stats_schema import (Badges, Comments, PostHitories, PostLinks, Posts,
                           PostsAnswers, PostsTags, Tags, Users, UsersBadges,
                           Votes)

users_rename_columns_mapping = {
    "Id": Users.user_id.name,
    "Reputation": Users.reputation.name,
    "CreationDate": Users.created_time.name,
    "DisplayName": Users.display_name.name,
    "LastAccessDate": Users.last_accessed_time.name,
    "WebsiteUrl": Users.website_url.name,
    "Location": Users.location.name,
    "AboutMe": Users.about_me.name,
    "Views": Users.views.name,
    "UpVotes": Users.upvotes.name,
    "DownVotes": Users.downvotes.name,
    "AccountId": Users.display_id.name,
    "Age": Users.age.name,
    "ProfileImageUrl": Users.profile_image_url.name,
}

badges_rename_columns_mapping = {"Name": Badges.name.name}

users_badges_rename_columns_mapping = {"UserId": UsersBadges.user_id.name, "Date": UsersBadges.granted_time.name}

posts_rename_columns_mapping = {
    "Id": Posts.post_id.name,
    "PostTypeId": Posts.post_type_id.name,
    "CreaionDate": Posts.created_time.name,
    "Score": Posts.score.name,
    "ViewCount": Posts.view_count.name,
    "Body": Posts.body.name,
    "OwnerUserId": Posts.owner_user_id.name,
    "LasActivityDate": Posts.last_activity_time.name,
    "Title": Posts.title.name,
    "AnswerCount": Posts.answer_count.name,
    "CommentCount": Posts.comment_count.name,
    "FavoriteCount": Posts.favorite_count.name,
    "LastEditorUserId": Posts.last_editor_user_id.name,
    "LastEditDate": Posts.last_edited_time.name,
    "CommunityOwnedDate": Posts.community_owned_time.name,
    "ClosedDate": Posts.closed_time.name,
    "OwnerDisplayName": Posts.owner_diplay_name.name,
    "LastEditorDisplayName": Posts.last_editor_display_name.name,
}

posts_answers_columns_mapping = {
    "Id": PostsAnswers.answer_post_id.name,
    "ParentId": PostsAnswers.post_id.name,
    "CreaionDate": PostsAnswers.answered_time.name,
}

comments_columns_mapping = {
    "Id": Comments.comment_id.name,
    "PostId": Comments.post_id.name,
    "Score": Comments.score.name,
    "Text": Comments.body.name,
    "CreationDate": Comments.created_time.name,
    "UserId": Comments.user_id.name,
    "UserDisplayName": Comments.user_display_name.name,
}

tags_columns_mapping = {"Id": Tags.tag_id.name, "TagName": Tags.name.name, "Count": Tags.usage_count.name}

posts_tags_columns_mapping = {"PostId": PostsTags.post_id.name, "CreationDate": PostsTags.tagged_time.name}

votes_columns_mapping = {
    "Id": Votes.vote_id.name,
    "PostId": Votes.post_id.name,
    "VoteTypeId": Votes.vote_type_id.name,
    "CreationDate": Votes.created_time.name,
    "UserId": Votes.user_id.name,
    "BountyAmount": Votes.bounty_amount.name,
}

post_links_columns_mapping = {
    "Id": PostLinks.post_link_id.name,
    "CreationDate": PostLinks.created_time.name,
    "PostId": PostLinks.post_id.name,
    "RelatedPostId": PostLinks.related_post_id.name,
    "LinkTypeId": PostLinks.link_type_id.name,
}

post_histories_columns_mapping = {
    "Id": PostHitories.post_history_id.name,
    "PostHistoryTypeId": PostHitories.post_history_type_id.name,
    "PostId": PostHitories.post_id.name,
    "RevisionGUID": PostHitories.revision_guid.name,
    "CreationDate": PostHitories.created_time.name,
    "UserId": PostHitories.user_id.name,
    "Text": PostHitories.text.name,
    "Comment": PostHitories.comment.name,
    "UserDisplayName": PostHitories.user_display_name.name,
}
