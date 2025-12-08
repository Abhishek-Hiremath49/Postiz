# class BaseProvider:
#     def __init__(self, account_doc):
#         self.account = account_doc

#     def post(self, content, attachments):
#         raise NotImplementedError()

#     def refresh_token(self):
#         # default refresh using channel.token_url
#         pass

class BaseProvider:
    def post(self, content, media=None):
        raise NotImplementedError
