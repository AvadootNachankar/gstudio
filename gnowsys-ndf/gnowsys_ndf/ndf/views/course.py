from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response #render  uncomment when to use
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django_mongokit import get_database


try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from gnowsys_ndf.settings import GAPPS, MEDIA_ROOT
from gnowsys_ndf.ndf.models import GSystemType, Node 
from gnowsys_ndf.ndf.views.methods import get_node_common_fields

db = get_database()
collection = db[Node.collection_name]
GST_COLLECTION = db[GSystemType.collection_name]
GST_COURSE = GST_COLLECTION.GSystemType.one({'name': GAPPS[7]})

def course(request, group_name, course_id):
    """
   * Renders a list of all 'courses' available within the database.
    """
    if GST_COURSE._id == ObjectId(course_id):
        title = GST_COURSE.name
        course_coll = collection.GSystem.find({'member_of': {'$all': [ObjectId(course_id)]}, 'group_set': {'$all': [group_name]}})
        template = "ndf/course.html"
        variable = RequestContext(request, {'course_coll': course_coll })
        return render_to_response(template, variable)

@login_required
def create_edit(request, group_name, node_id = None):
    """Creates/Modifies details about the given quiz-item.
    """

    context_variables = { 'title': GST_COURSE.name,
                          'group_name': group_name
                      }

    if node_id:
        course_node = collection.Node.one({'_type': u'GSystem', '_id': ObjectId(node_id)})
    else:
        course_node = collection.GSystem()

    if request.method == "POST":
        get_node_common_fields(request, course_node, group_name, GST_COURSE)
        course_node.save()
        #return HttpResponseRedirect(reverse('ndf.views.course.course',kwargs={'group_name': group_name, 'course_id': course_node._id}))
        return HttpResponseRedirect(reverse('course', kwargs={'group_name': group_name, 'course_id': GST_COURSE._id}))
        
    else:
        if node_id:
            context_variables['node'] = course_node
            
        return render_to_response("ndf/course_create_edit.html",
                                  context_variables,
                                  context_instance=RequestContext(request)
                              )

def course_detail(request, group_name, _id):
    course_node = collection.Node.one({"_id": ObjectId(_id)})
    return render_to_response("ndf/course_detail.html",
                                  { 'node': course_node,
                                    'group_name': group_name
                                  },
                                  context_instance = RequestContext(request)
        )
