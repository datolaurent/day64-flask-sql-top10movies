from wtforms import StringField, SubmitField, HiddenField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Regexp
from flask_wtf import FlaskForm


# FORM SECTION
class EditMovieForm(FlaskForm):
    rating = StringField('Your rating out of 10', validators=[Regexp(r'(^[1-9][\d]*(?:\.(\d{1,}))?$)|(^$)')])
    review = TextAreaField('Your review')
    id = HiddenField('id')
    cancel = SubmitField('Cancel')
    submit = SubmitField('Update')


class AddMovieForm(FlaskForm):
    new_movie = StringField('Movie title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')

class SelectMovieForm(FlaskForm):
    RadioField('Movie', choices=[('value', 'description'), ('value_two', 'whatever')])
    submit = SubmitField('Select Movie')