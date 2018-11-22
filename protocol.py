messageType = {'Init': 1, 'Block': 2, 'Prepare': 3, 'Commit': 4, 'Transaction': 5, 'Help': 6, 'Answer': 7}


# return type, id/body
def init_message(id_num):
    return {"type": messageType['Init'], "id_num": id_num}


def block_message(body):
    return {"type": messageType['Block'], "body": body}


def prepare_message(body):
    return {"type": messageType['Prepare'], "body": body}


def commit_message(body):
    return {"type": messageType['Commit'], "body": body}


def transaction_message(body):
    return {"type": messageType['Transaction'], "body": body}


def help_message(body):
    return {"type": messageType['Help'], "body": body}


def answer_message(body):
    return {"type": messageType['Answer'], "body": body}
