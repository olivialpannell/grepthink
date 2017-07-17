"""
Teamwork: courses

Database Models for the objects: Course, Enrollment
"""
#Build-in modules
from __future__ import unicode_literals

import datetime
import random
import string
#Other imports
import uuid

from django.contrib import auth
# Django modules
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone

# import of project models
from teamwork.apps.projects.models import Project

class Assignment(models.Model):
    due_date = models.CharField(max_length=255, default="20991231")
    ass_date=models.CharField(max_length=255, default="20000101")
    ass_type=models.CharField(max_length=255, default='TSR')
    ass_name=models.CharField(max_length=255, default="TSR for Sprint X")

def get_user_courses(self):
    """
    Added to auth so that a user object can easily retrieve enrolled courses
    Gets a list of course objects that the user is in
    """

    if self.profile.isProf:
        my_courses = Course.objects.filter(creator=self.username)
    else:
        #Gets current user's enrollments, by looking for user in  Enrollment table
        myEnrollment = Enrollment.objects.filter(user=self)

        #print("myEnrollment:")
        #print(myEnrollment)

        #Filters for courses based on enrollment
        my_courses = Course.objects.filter(enrollment__in=myEnrollment)

    return my_courses


# Add method to function that returns a list of users enrolled courses
auth.models.User.add_to_class('get_user_courses', get_user_courses)


# Generates add code
def rand_code(size):
    # Usees a random choice from lowercase, uppercase, and digits
    return ''.join([
        random.choice(string.ascii_letters + string.digits) for i in range(size)
    ])


class Course(models.Model):
    """
    Course: A database model (object) for courses.

    Fields:
        name: the name of the course.
        info: the course description
        term: the school term this course is offered
        students: many to many field of users
        slug: unique URL slug used to identify the project

        creator: the instructor of the course
        addCode: generated unique code used to enroll in the course
        now: gets current datetime
        year: gets current year from datetime
        limit_creation: boolean that dictates wether only professors can create projects

        limit_weights: boolean that dictates if all member projects must follow
        given weights for selection
        weight_interest: weight [0-5] given to user interest in project
        weight_know: weight [0-5] given for skills user has
        weight_learn: weight [0-5] given for skills user wants to learn

    Methods:
        __str__(self):                  Human readeable representation of the course object.
        save(self, *args, **kwargs):    Overides the default save operator...
        get_my_courses():               Gets a list of stored course objects of the current user.
        get_created_courses():          Gets a list of courses created by user

    """
    # define the terms for the multiple choice
    Term_Choice = (('Winter', 'Winter'), ('Spring', 'Spring'),
                   ('Summer', 'Summer'), ('Fall', 'Fall'), )

    Lower_Boundary_Choice = ((0, 'No Preference'), (2, '01:00'), (4, '02:00'), (6, '03:00'),
                       (8, '04:00'), (10, '05:00'), (12, '06:00'), (14, '07:00'),
                       (16, '08:00'), (18, '09:00'), (20, '10:00'), (22, '11:00'),
                       (24, '12:00'), )

    Upper_Boundary_Choice = ((48, 'No Preference'), (26, '13:00'), (28, '14:00'), (30, '15:00'),
                       (32, '16:00'), (34, '17:00'), (36, '18:00'), (38, '19:00'),
                       (40, '20:00'), (42, '21:00'), (44, '22:00'), (46, '23:00'), )

    # The title of the course. Should not be null, but default is provided.
    name = models.CharField(max_length=255, default="No Course Title Provided")
    # Course info, string
    info = models.CharField(
        # with max length 300
        max_length=300,
        # default as "There is no Course Description"
        default="There is no Course Description")
    # Term, string
    term = models.CharField(
        # with max length 6
        max_length=6,
        # choices defined by term choice
        choices=Term_Choice,
        # defaulted to none
        default='None')
    # Slug for course, string
    slug = models.CharField(
        # with max length 20
        max_length=20,
        # must be unique
        unique=True)

    # Students in course, manytomany
    students = models.ManyToManyField(
        # to User model
        User,
        # through the enrollment table
        through='Enrollment')

    #projects in course, manytomany
    projects = models.ManyToManyField(
        # to project model
        Project)
    assignments=models.ManyToManyField(
        Assignment
    )

    # RYAN
    # creator needs to be a foreign key for a simpler linking
    # but student and creator  both have backwards relations to user, so
    # I need to go through our current code and setup a related name for all
    # uses of either of these. Cant dedicate time to it now but needs to get done.
    # creator = models.ForeignKey(User)

    # Creator of course, string
    creator = models.CharField(
        # with max length 255
        max_length=255,
        # defaulted to "Default"
        default="Default")
    # addCode for course, string
    addCode = models.CharField(
        # with length 10
        max_length=10,
        # that is unique
        unique=True)
    # get the current date for the year
    now = datetime.datetime.now()
    # year course was created, string
    year = models.CharField(
        # with max length 4
        max_length=20,
        # defaulted to current year
        default=now.year)
    # limit creation, boolean
    limit_creation = models.BooleanField(
        #defaulted to False
        default=False)

    # limits student from showing interest
    limit_interest = models.BooleanField(
        #defaulted to false
        default=False)

    limit_weights = models.BooleanField(default=False)
    weigh_interest = models.IntegerField(default=1)
    weigh_know = models.IntegerField(default=1)
    weigh_learn = models.IntegerField(default=1)
    csv_file = models.FileField(upload_to='csv_files/', default="")

    # The Meta class provides some extra information about the Project model.
    class Meta:
        # Verbose name is the same as class name in this case.
        verbose_name = "Course"
        # Multiple Project objects are referred to as Projects.
        verbose_name_plural = "Courses"

    def __str__(self):
        """
        Human readeable representation of the Course object. Might need to update when we add more attributes.
        Maybe something like, return u'%s %s' % (self.course, self.title)
        """
        return self.name + "(slug: " + self.slug + ")"

    def save(self, *args, **kwargs):
        """
        Overides the default save operator...
        Bassically a way to check if the Course object exists in the database. Will be helpful later.
        self.pk is the primary key of the Course object in the database!
        """

        # try catch to ensure the unique property is met
        try:
            # if the addcode has not been assigned yet get one
            if self.addCode is None or len(self.addCode) == 0:
                self.addCode = rand_code(10)

        except IntegrityError as e:
            # if we fail the unique property get a new addCode until one doesnt exist
            while Course.objects.filter(addCode=self.addCode).exists():
                self.addCode = rand_code(10)

        # Generate URL slug if not specified
        if self.slug is None or len(self.slug) == 0:
            newslug = self.name + "-" + self.term
            newslug = slugify(newslug)[0:20]
            while Course.objects.filter(slug=newslug).exists():
                newslug = self.name + "-" + self.term
                newslug = slugify(newslug[0:16] + "-" + rand_code(3))
            self.slug = newslug

        self.slug = slugify(self.slug)

        super(Course, self).save(*args, **kwargs)

    @staticmethod
    def get_my_courses(user):
        """
        Gets a list of course objects that the user is in
        """
        #Gets current user's enrollments
        myEnrollment = Enrollment.objects.filter(user=user)

        #Filters for courses based on enrollment
        my_courses = Course.objects.filter(enrollment__in=myEnrollment)

        return my_courses

    @staticmethod
    def get_my_created_courses(user):
        """
        Gets a list ofcourse objects the current user has created
        """
        #filters through courses the user has created
        created_courses = Course.objects.filter(creator=user.username)

        return created_courses

    def get_updates(self):
        """
        Gets list of updates for course
        """
        return CourseUpdate.objects.filter(course=self)

    def get_updates_by_date(self):
        """
        Gets list of dicts, where each dict has keys 'date' and 'updates'
        Updates is a list of updates for the specific day
        Useful for timeline HTML view
        """
        updates = self.get_updates()
        unique_dates = sorted(
            set(update.date_post.date() for update in updates), reverse=True)
        updates_by_date = []  # Feel like this could be done better
        for d in unique_dates:
            updates_by_date.append({
                'date':
                d,
                'updates': [u for u in updates if u.date_post.date() == d]
            })
        return updates_by_date


# Enrollment class that manytomanys between User and Course
class Enrollment(models.Model):
    #User, which is a foriegn key to
    user = models.ForeignKey(
        # the User model
        User,
        # on deletion, delete child objects
        on_delete=models.CASCADE,
        # with a default of 0
        default=0)

    # Course, which is a foregin key to
    course = models.ForeignKey(
        # the course model
        Course,
        # on deletion, delete child objects
        on_delete=models.CASCADE,
        # with a default of 0
        default=0)

    # user role in a course
    role = models.CharField(max_length=24, default="student")

    def __str__(self):
        """
        Human readeable representation of the Enrollment object. Might need to update when we add more attributes.
        Maybe something like, return u'%s %s' % (self.course, self.title)
        """
        return ("%s"%(self.user.username))


class CourseUpdate(models.Model):
    """
    CourseUpdate objects are announcement postings for a course

    Attributes:
        course:     ForeignKey to course
        title:      Title of post
        content:    Content of post
        date_post:  Date published, can be future date (only shows past dates)
        date_edit:  Date last edited
        creator:    ForeignKey to user who wrote post

    """
    course = models.ForeignKey(Course)
    title = models.CharField(max_length=255, default="No Title Provided")
    content = models.TextField(max_length=2000, default="*No Content Provided*")
    date_post = models.DateTimeField(editable=True)
    date_edit = models.DateTimeField(editable=True)
    creator = models.ForeignKey(User)

    class Meta:
        verbose_name = "Course Update"
        verbose_name_plural = verbose_name + "s"
        ordering = ("-date_post", "-date_edit", "title")

    def __str__(self):
        return '{0} - {1}'.format(self.creator.username, self.title)

    def save(self, *args, **kwargs):
        """
        Overrides default save
        """

        if self.date_post is None:
            self.date_post = datetime.datetime.now()
            self.date_edit = self.date_post
        else:
            self.date_edit = datetime.datetime.now()

        super(CourseUpdate, self).save(*args, **kwargs)
