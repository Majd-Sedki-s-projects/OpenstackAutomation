from keystoneauth1.identity import v3
from keystoneauth1 import session


class Authenticate(object):
    def __init__(self, auth, user, passwd, proj_name, user_domain, project_domain):
        self.auth_url = auth
        self.username = user
        self.password = passwd
        self.project_name = proj_name
        self.user_domain_id = user_domain
        self.project_domain_id = project_domain

    def start_auth(self):
        auth = v3.Password(auth_url=self.auth_url, username=self.username, password=self.password,
                           project_name=self.project_name, user_domain_id=self.user_domain_id,
                           project_domain_id=self.project_domain_id)
        sess = session.Session(auth=auth)
        return sess
