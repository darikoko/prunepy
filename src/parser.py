def extract_loop(text:str):
    formated = text.replace("(", "").replace(")", "").replace(" ","").split(",")
    local_scope = "{" + ",".join( [f"'{x}': {x}" for x in formated]) + "}"
    return local_scope
