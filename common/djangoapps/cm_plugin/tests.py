from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory
from student.models import CourseEnrollment
from courseware.access import has_access
from .views import *
import requests, json

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
        self.assertEqual(response.status_code, 422)
        response_object = json.loads(response.content)
        self.assertTrue(('Data Integrity Error') in response_object['errors'])

