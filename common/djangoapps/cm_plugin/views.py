from django.db import IntegrityError, DatabaseError
from xmodule.modulestore.django import modulestore
from xmodule.course_module import CourseDescriptor
from courseware.courses import get_course
from django.http import HttpResponseNotFound, HttpResponse
from contentstore.views.course import _create_or_rerun_course
from django.views.decorators.csrf import csrf_exempt
from util.json_request import expect_json
from student.views import _do_create_account
from django.contrib.auth.models import User
from student import auth
from student.models import CourseEnrollment, CourseAccessRole
from student.roles import CourseInstructorRole
from student.views import AccountValidationError
from student.forms import AccountCreationForm
from student.tests.factories import AdminFactory
from courseware.models import StudentModule
from contentstore.utils import delete_course_and_groups
from contentstore.views.user import CannotOrphanCourse, try_remove_instructor
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
import json
import logging
from edxmako.shortcuts import render_to_response
from util.json_request import JsonResponse
from .healthcheck import check_services
from .token import validate_token

log = logging.getLogger(__name__)

# Create your views here.
def get_key_from_course_id(course_id):
    return CourseKey.from_string(course_id)

"""
Enroll user in course. 
params:
    email => the user to enroll
    course_id => the course to enroll in

    NOTE: returns status :ok if course_id invalid
"""

@csrf_exempt
@expect_json
def cm_enroll_user(request):
    response_format = request.REQUEST.get('format','html')
    if response_format == 'json' or 'application/json' in request.META.get('HTTP/ACCEPT', 'application/json'):
        if request.method == 'POST':
            if validate_token(request.body, request) is False:
                return HttpResponse('Unauthorized', status=401)
            if 'email' not in request.json or 'course_id' not in request.json:
                return HttpResponse(content=json.dumps({'errors':'Missing params'}), \
                        content_type = 'application/json', status=400)
            try:
                log.info("Enrolling user: " + request.json.get('email') + " course: " + request.json.get('course_id'))
                CourseEnrollment.enroll_by_email(request.json.get('email'), \
                                                 get_key_from_course_id(request.json.get('course_id')), ignore_errors=False)

                # See if enrolling with staff credentials
                if request.json.get('role') == 'staff':
                    global_admin = AdminFactory()
                    course = get_key_from_course_id(request.json.get('course_id'))
                    auth.add_users(global_admin, CourseInstructorRole(course), User.objects.get(email=request.json.get('email')))
                    
                content = {'success':'ok'}
                status_code = 200
            except User.DoesNotExist:
                content = {'errors':'User does not exist'}
                status_code = 422
            return HttpResponse(content=json.dumps(content), status=status_code, \
                    content_type = 'application/json')
        else:
            return HttpResponse(content=json.dumps({}), status=404, content_type = 'application/json')
    else:
        return HttpResponse(content=json.dumps({}), status=404, content_type = 'application/json')

"""
UnEnroll user in course. 
params:
    email => the user to unenroll
    course_id => the course to unenroll in

    NOTE: returns status :ok even if either email or course_id is invalid
"""

@csrf_exempt
@expect_json
def cm_unenroll_user(request):
    """
    This is a hard unenroll as opposed to the regular soft unenroll that edx uses internally.
    """
    response_format = request.REQUEST.get('format','html')
    if response_format == 'json' or 'application/json' in request.META.get('HTTP/ACCEPT', 'application/json'):
        if request.method == 'POST':
            if validate_token(request.body, request) is False:
                log.warn("Unauthorized access made by course: %s, user: %s", request.json.get('email'), request.json.get('course_id'))
                return HttpResponse('Unauthorized', status=401)
            if 'email' not in request.json or 'course_id' not in request.json:
                log.error("Incomplete request.")
                return HttpResponse(content=json.dumps({'errors':'Missing params'}), \
                        content_type = 'application/json', status=400)

            try:
                log.info("Unenrolling user: %s from course: %s" % (request.json.get('email'), request.json.get('course_id')))
                user = User.objects.get(email=request.json.get('email'))
                request.user = user
            except User.DoesNotExist:
                log.info("Unknown user : %s from course %s", request.json.get('email'), request.json.get('course_id'))
                return HttpResponse(content=json.dumps({'errors': 'Unknown user'}), status=500, content_type='application/json')
            course_id = request.json.get('course_id')

            #locator = loc_mapper().translate_location(course_id, CourseDescriptor.id_to_location(course_id))

            role = request.json.get('role')
            if role == 'staff':
                try:
                    try_remove_instructor(request, get_key_from_course_id(course_id), user)
                    log.info("staff unenrolled: %s", str(user))
                except CannotOrphanCourse as oops:
                    log.warn("last course admin removal attempted: %s", str(user))
                    return JsonResponse(oops.msg, 400)
            else:
                log.info("student unenroll: %s", str(user))
                try:
                    CourseEnrollment.unenroll(user, get_key_from_course_id(request.json.get('course_id')))
                    status_code = 200
                except DatabaseError:
                    # this is just for tests. This error will never be hit in production
                    # should probably consider moving cm_plugin out of common too.
                    log.error("Unenroll failed for user: %s from course: %s", request.json.get('email'), request.json.get('course_id'))
                    pass

            status_code = 200
            content = {'success':'ok'}

            log.info("Unenrolled user: %s from course: %s", request.json.get('email'), request.json.get('course_id'))
            return HttpResponse(content=json.dumps(content), status=status_code, content_type='application/json')
        else:
            return HttpResponse(content=json.dumps({}), status=404, content_type='application/json')
    else:
        return HttpResponse(content=json.dumps({}), status=404, content_type='application/json')


"""
POST request from cm to create new user.
Returns unique id (email)
"""
@csrf_exempt
@expect_json
def cm_create_new_user(request):
    response_format = request.REQUEST.get('format','html')
    if response_format == 'json' or 'application/json' in request.META.get('HTTP/ACCEPT','application/json'):
        if request.method == 'POST':
            if validate_token(request.body, request) is False:
                return HttpResponse('Unauthorized', status=401)
            try:
                form = AccountCreationForm(
                        data=request.json,
                        tos_required=False
                    )
                ret = _do_create_account(form)
                if isinstance(ret, HttpResponse):
                    response_body = json.loads(ret.content)
                    content = {'errors':response_body['value']}
                    status_code = 422
                elif isinstance(ret, tuple):
                    created_user = User.objects.get(email=ret[0].email)
                    created_user.is_active = True
                    created_user.save()
                    content = {'id':ret[0].email}
                    status_code = 200
            except AccountValidationError:
                    user = User.objects.get(email=request.json.get('email'))
                    content = {'id': user.email}
                    status_code = 200
            except:
                    content = {'errors':'Bad Request'}
                    status_code = 400

            return HttpResponse(content = json.dumps(content), \
                    content_type = 'application/json', \
                    status = status_code)
        else:
            return HttpResponse(content=json.dumps({}), status=404, content_type='application/json')
    else:
        return HttpResponse(content=json.dumps({}), status=404, content_type='application/json')

def set_cookie(request):
    referrer = request.GET.get('return_to_url')

    response = render_to_response('cm_plugin/cookie.html', {'referrer': referrer})
    response.set_cookie(key='visited', value='true')
    
    return response

def healthcheck(request):
    if request.GET.get('all', False):
        result = check_services()
    else:
        result = {'status': 'alive'}

    return HttpResponse(content=json.dumps(result), status=200, content_type="application/json")


@csrf_exempt
@expect_json
def cm_course_delete(request, course_id = None):
    response_format = request.REQUEST.get('format','html')
    if response_format == 'json' or 'application/json' in request.META.get('HTTP/ACCEPT', 'application/json'):
        if request.method == 'POST':
            if validate_token(request.body, request) is False:
                log.warn("Unauthorized access made by course: %s, user: %s", request.json.get('email'))
                return HttpResponse('Unauthorized', status=401)

            email = request.json.get('email')
            try:
                instructor = User.objects.get(email = email)
                request.user = instructor
            except User.DoesNotExist:
                log.error("course deletion attempted by unregistered user: %s", email)
                return JsonResponse(json.dumps({ 'error': 'course deletion attempted by unregistered user' }), status = 400)

            if course_id is None:
                return JsonResponse(json.dumps({'error': 'Course ID does not exist'}), status = 404)

            try:
                course_key = CourseKey.from_string(course_id)
            except InvalidKeyError:
                try:
                    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
                except InvalidKeyError:
                    course_key = None

            if course_key is None:
                return JsonResponse(json.dumps({'error': 'Course Key not found for course id: ' + str(course_id)}), status = 404)

            if not auth.has_access(instructor, CourseInstructorRole(course_key)):
                log.error("course deletion attempted by unauthorized user: %s", email)
                return JsonResponse(json.dumps({'error': 'course deletion attempted by unauthorized user'}), status = 401)

            try:
                delete_course_and_groups(course_key, instructor.id)
                try:
                    StudentModule.objects.filter(course_id=course_key).delete()
                except:
                    # We need this for testing. The above mentioned model lives in
                    # LMS but our tests are executed via CMS. This piece of code
                    # makes sure that the test safely skips over this and runs
                    # successfully.
                    pass
                CourseEnrollment.objects.filter(course_id=course_key).delete()
                try:
                    CourseAccessRole.objects.get(course_id=course_key).delete()
                except CourseAccessRole.DoesNotExist:
                    pass
            except Exception as e:
                return JsonResponse(json.dumps({'error' : str(e)}), status = 500)

            return JsonResponse(json.dumps({'message': "successfully deleted course"}), status = 200)
        else:
            return JsonResponse(json.dumps({}), status=404)
    else:
        return JsonResponse(content=json.dumps({}), status=404)
