from django.test import TestCase
from django.conf import settings
import unittest
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory
from student.models import CourseEnrollment
from student.roles import CourseInstructorRole
from student.tests.factories import AdminFactory
from student.roles import CourseStaffRole
from student import auth
from courseware.access import has_access
if not settings.LMS_TEST_ENV:
    from .views import *
from unittest import skipIf
import requests, json


@skipIf(settings.LMS_TEST_ENV, "only invoked from cms")
class EnrollTest(ModuleStoreTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.course = CourseFactory.create(org="test",course="courseid", \
            display_name="run1")
        self.user = User.objects.create_user(username='uname', \
            email='user@email.com', password = 'password') 
        self.cm_secret_token = 'cm_secret_token'
     
    def test_user_enrollment(self):
        request = self.factory.post('/cm/enroll', \
            json.dumps({'cm_secret_token':self.cm_secret_token, \
            'email':self.user.email, 'course_id':self.course.id.to_deprecated_string()}), \
            content_type = 'application/json')
        response = cm_enroll_user(request)
        self.assertEqual(response.status_code,200)
        response_object = json.loads(response.content)
        self.assertEqual(response_object['success'],'ok')
        self.assertFalse(has_access(self.user, 'staff', self.course))

    def test_staff_enrollment(self):
        request = self.factory.post('/cm/enroll', \
            json.dumps({'cm_secret_token':self.cm_secret_token, \
            'email':self.user.email, \
            'role':'staff', \
            'course_id':self.course.id.to_deprecated_string()}), \
            content_type = 'application/json')
        response = cm_enroll_user(request)
        self.assertEqual(response.status_code,200)
        response_object = json.loads(response.content)
        self.assertEqual(response_object['success'],'ok')
        self.assertTrue(has_access(self.user, 'staff', self.course))
        
    def test_user_enrollment_non_existent_user(self):
        request = self.factory.post('/cm/enroll', \
            json.dumps({'cm_secret_token':self.cm_secret_token, \
            'email':'xx@xx.com', 'course_id':self.course.id.to_deprecated_string()}), \
            content_type = 'application/json')
        response = cm_enroll_user(request)
        self.assertEqual(response.status_code, 422)
        response_object = json.loads(response.content)
        self.assertEqual(response_object['errors'], 'User does not exist')

    def test_user_enrollment_bad_params(self):
        request = self.factory.post('/cm/enroll', \
            json.dumps({'cm_secret_token': self.cm_secret_token, \
            'email':self.user.email}), \
            content_type = 'application/json')
        response = cm_enroll_user(request)
        self.assertEqual(response.status_code, 400)
        response_object = json.loads(response.content)
        self.assertEqual(response_object['errors'], 'Missing params')

        request = self.factory.post('/cm/enroll', \
            json.dumps({'cm_secret_token':self.cm_secret_token, \
            'course_id':self.course.id.to_deprecated_string()}), \
            content_type = 'application/json')
        response = cm_enroll_user(request)
        self.assertEqual(response.status_code, 400)
        response_object = json.loads(response.content)
        self.assertEqual(response_object['errors'], 'Missing params')

@skipIf(settings.LMS_TEST_ENV, "only invoked from cms")
class UnEnrollTest(TestCase):
    def setUp(self):
        self.cm_secret_token = 'cm_secret_token'
        self.factory = RequestFactory()
        self.course = CourseFactory.create(org="test",course="courseid", \
            display_name="run1")
        self.user = User.objects.create_user(username='uname', \
            email='user@email.com', password = 'password') 
        course_key = get_key_from_course_id(self.course.id.to_deprecated_string())
        CourseEnrollment.enroll(self.user, course_key)

    def test_user_unenrollment(self):
        request = self.factory.post('/cm/unenroll', \
            json.dumps({'cm_secret_token':self.cm_secret_token, \
            'email':self.user.email, 'course_id':self.course.id.to_deprecated_string()}), \
            content_type = 'application/json')
        response = cm_unenroll_user(request)
        self.assertEqual(response.status_code,200)
        response_object = json.loads(response.content)
        self.assertEqual(response_object['success'],'ok')

    def test_staff_unenrollment(self):
        request = self.factory.post('/cm/enroll', \
            json.dumps({'cm_secret_token':self.cm_secret_token, \
            'email':self.user.email, \
            'role':'staff', \
            'course_id':self.course.id.to_deprecated_string()}), \
            content_type = 'application/json')
        response = cm_unenroll_user(request)
        self.assertEqual(response.status_code,200)
        response_object = json.loads(response.content)
        self.assertEqual(response_object['success'],'ok')
        self.assertFalse(has_access(self.user, 'staff', self.course))

    def test_user_unenrollment_bad_params(self):
        request = self.factory.post('/cm/unenroll', \
            json.dumps({'cm_secret_token':self.cm_secret_token, \
            'email':self.user.email}), \
            content_type = 'application/json')
        response = cm_unenroll_user(request)
        self.assertEqual(response.status_code, 400)
        response_object = json.loads(response.content)
        self.assertEqual(response_object['errors'],'Missing params')

        request = self.factory.post('/cm/unenroll', \
            json.dumps({'cm_secret_token':self.cm_secret_token, \
            'course_id':self.course.id.to_deprecated_string()}), \
            content_type = 'application/json')
        response = cm_unenroll_user(request)
        self.assertEqual(response.status_code, 400)
        response_object = json.loads(response.content)
        self.assertEqual(response_object['errors'],'Missing params')

@skipIf(settings.LMS_TEST_ENV, "only invoked from cms")
class UserCreationTest(TestCase):
    def setUp(self):
        self.cm_secret_token = 'cm_secret_token'
        self.factory = RequestFactory()
        self.user_creation_options = {'username':'uname', \
              'email':'email@email.com', \
              'password':'pwd123!123', \
              'name':'name', \
              'cm_secret_token': self.cm_secret_token}
      
    def test_user_creation(self):
        request = self.factory.post('/cm/user', \
                json.dumps(self.user_creation_options), content_type='application/json')
        response = cm_create_new_user(request)
        self.assertEqual(response.status_code, 200)
        response_object = json.loads(response.content)
        self.assertTrue('email@email.com' in response_object['id'])

    def test_bad_params_user_error(self):
        request = self.factory.post('/cm/user', \
            json.dumps({'cm_secret_token':self.cm_secret_token, \
            'username':'uname','email':'email@email.com', \
                'password':'password'}), content_type='application/json')
        response = cm_create_new_user(request)
        self.assertEqual(response.status_code, 400)
        response_object = json.loads(response.content)
        self.assertTrue('Bad Request' in response_object['errors'])

    def test_duplicate_email_user_error(self):
        request = self.factory.post('/cm/user', \
                json.dumps(self.user_creation_options), \
                content_type = 'application/json')
        first_response = cm_create_new_user(request)

        # again
        response = cm_create_new_user(request)
        self.assertEqual(response.status_code, 200)
        response_object = json.loads(response.content)
        print response_object
        self.assertTrue(('email@email.com') in response_object['id'])

@skipIf(settings.LMS_TEST_ENV, "only invoked from cms")
class CourseDeletionTest(TestCase):
    def setUp(self):
        self.cm_secret_token = 'cm_secret_token'
        self.factory = RequestFactory()

    def test_deleting_course(self):
        course = CourseFactory.create(org="test",course="courseid", \
                                           display_name="run1")
        course_id = course.id
        user = User.objects.create_user(username='uname', \
                                             email='user@email.com', password = 'password')
        CourseInstructorRole(course.id).add_users(user)
        course_deletion_options = {'email': user.email,
                                        'cm_secret_token': self.cm_secret_token}
        url = '/cm/delete_course/' + str(course.id)
        request = self.factory.post(url, json.dumps(course_deletion_options),
                                    content_type='application/json')
        response = cm_course_delete(request, str(course_id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), u'{"message": "successfully deleted course"}')


    def test_deleting_non_existent_course(self):
        url = '/cm/delete_course/'
        user = User.objects.create_user(username='uname', \
                                            email='someuser@mail.com', password = 'password')
        course_deletion_options = {'email': 'someuser@mail.com',
                                   'cm_secret_token': self.cm_secret_token}
        request = self.factory.post(url + "1", json.dumps(course_deletion_options), content_type='application/json')
        response = cm_course_delete(request, "1")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content), u'{"error": "Course Key not found for course id: 1"}')

    def test_deletion_by_non_instructor(self):
        course = CourseFactory.create(org="test",course="courseid", \
                                      display_name="run1")
        course_id = course.id
        user = User.objects.create_user(username='uname', \
                                        email='user1@email.com', password = 'password')

        course_deletion_options = {'email': user.email,
                                   'cm_secret_token': self.cm_secret_token}
        url = '/cm/delete_course/' + str(course.id)
        request = self.factory.post(url, json.dumps(course_deletion_options), content_type='application/json')
        response = cm_course_delete(request, str(course_id))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.content), u'{"error": "course deletion attempted by unauthorized user"}')
