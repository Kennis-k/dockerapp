from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, TextAreaField, SelectField, DateTimeField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))


CHOICES = [('1', '吹水台'), ('2', '高登熱'), ('3', '硬件台'), ('4', '手機台'), ('5', '音樂台'), ('6', '飲食台'),
           ('7', '上班台'), ('8', '寵物台'), ('9', '買賣台'), ('10', '活動台')]


class TopicForm(FlaskForm):
    pid = HiddenField()
    tag = SelectField('tag', choices=CHOICES)
    topic = StringField(_l('Topic'), validators=[DataRequired(Length(1, 64))])
    post = TextAreaField(_l('Content'), validators=[Length(min=0, max=140)])
    timestamp = HiddenField("Timestamp", default=datetime.utcnow, validators=[DataRequired()])
    user_id = HiddenField()
    user_name = HiddenField()
    submit = SubmitField(_l('Submit'))


class ReplyForm(FlaskForm):
    id = HiddenField()
    post = TextAreaField(_l('Content'), validators=[Length(min=0, max=140)])
    timestamp = HiddenField("Timestamp", default=datetime.utcnow, validators=[DataRequired()])
    user_id = HiddenField()
    name = HiddenField()
    submit = SubmitField(_l('Submit'))
