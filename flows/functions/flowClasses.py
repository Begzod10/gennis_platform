from ..models import Flow


def flow_classes(flow):
    classes = []
    for student in flow.students.all():
        for group in student.groups_student.all():
            classes.append(group.id)
    classes = list(set(classes))
    flow_obj = Flow.objects.get(id=flow.id)
    flow_obj.classes = classes
    flow_obj.save()
    return True
