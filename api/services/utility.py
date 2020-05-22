import re


def emailValidator(email):
    regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if(re.search(regex,email)):  
        return True     
    else:  
        return False


def passwordValidator(password):
    if (len(password)<8): 
        return False
    elif not re.search(r"[a-z]", password): 
        return False
    elif not re.search(r"[A-Z]", password): 
        return False
    elif not re.search(r"[0-9]", password): 
        return False
    elif not re.search(r"[_@$]", password): 
        return False
    elif re.search(r"\s", password): 
        return False
    else:
        return True
