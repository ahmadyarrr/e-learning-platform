from os.path import join


def get_path(instance,filename):
    
    course_id = instance.course.id
    student_id  = instance.student.id
    
    return f'course/{course_id}/hw/{student_id}'