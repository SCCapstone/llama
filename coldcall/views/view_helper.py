# helper functions used in creation of each view
BASE_TEMPLATE_DIR = "coldcall/"
MOBILE_TEMPLATE_DIR = "mobile/"
def get_template_dir(in_str, mobile):
    if mobile:
        return BASE_TEMPLATE_DIR + MOBILE_TEMPLATE_DIR + in_str + ".html"
    else:
        return BASE_TEMPLATE_DIR + in_str + ".html"
    
def get_demo_dir():
    return BASE_TEMPLATE_DIR + "demo/demo.html"
    
#ExportClassFileView constants
STUDENT_ATTRIBUTES = ['usc_id', 'email', 'first_name', 'last_name', 'seating', 'total_calls', 'absent_calls', 'total_score', 'class_id']
RATING_ATTRIBUTES = ['usc_id', 'date', 'attendance', 'prepared', 'score', 'class_id']
SAMPLE_STUDENT = ['B12345678', "sample@example.com", "John", "Doe", "FR", '0', '0', '0']
SAMPLE_RATING = ['B12345678', 'April 2nd, 2025 3PM', 'TRUE', 'TRUE', '5']