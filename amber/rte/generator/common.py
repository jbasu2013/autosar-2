import cfile as C

def beginExternCBlock():
    code = C.sequence()
    code.append(C.line('#ifdef __cplusplus'))
    code.append(C.line('extern "C"'))
    code.append(C.line('{'))
    code.append(C.line('#endif /* __cplusplus */'))
    return code

def endExternCBlock():
    code = C.sequence()
    code.append(C.line('#ifdef __cplusplus'))    
    code.append(C.line('}'))
    code.append(C.line('#endif /* __cplusplus */'))
    return code

def genCommentHeader(comment):
    """
    Returns a comment header
    """
    code = C.sequence()
    code.append(C.line('/*********************************************************************************************************************'))
    code.append(C.line('* {}'.format(comment)))
    code.append(C.line('*********************************************************************************************************************/'))
    return code
