from typing import List

from ninja import ModelSchema, Schema

from apps.course.models import Course, Chapter, Comment, Video
from apps.user.schemas import UserInfo


class CourseSchema(ModelSchema):
    class Meta:
        model = Course
        fields = "__all__"


class VideoSchema(ModelSchema):
    class Meta:
        model = Video
        fields = "__all__"





class ChapterSchema(ModelSchema):
    videos: List[VideoSchema] = None


    

    class Meta:
        model = Chapter
        fields = "__all__"


class CommentSchema(ModelSchema):
    user: UserInfo = None

    class Meta:
        model = Comment
        fields = "__all__"


class CommentCreate(Schema):
    content: str
    course_id: int
