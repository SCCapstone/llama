# helper functions used in creation of each view
BASE_TEMPLATE_DIR = "coldcall/"
MOBILE_TEMPLATE_DIR = "mobile/"
def get_template_dir(in_str, mobile):
    if mobile:
        return BASE_TEMPLATE_DIR + MOBILE_TEMPLATE_DIR + in_str + ".html"
    else:
        return BASE_TEMPLATE_DIR + in_str + ".html"