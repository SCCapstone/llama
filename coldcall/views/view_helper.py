# helper functions used in creation of each view
BASE_TEMPLATE_DIR = "coldcall/"
MOBILE_TEMPLATE_DIR = "mobile/"
def get_template_dir(in_str, mobile):
    if mobile:
        return BASE_TEMPLATE_DIR + MOBILE_TEMPLATE_DIR + in_str + ".html"
    else:
        return BASE_TEMPLATE_DIR + in_str + ".html"
    
#ExportClassFileView constants
STUDENT_ATTRIBUTES = ['usc_id', 'email', 'first_name', 'last_name', 'seating', 'total_calls', 'absent_calls', 'total_score', 'class_id']
RATING_ATTRIBUTES = ['usc_id', 'date', 'attendance', 'prepared', 'score', 'class_id']
