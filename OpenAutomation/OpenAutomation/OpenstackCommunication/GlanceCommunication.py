from glanceclient import Client as glance_client


class GlanceCommunication:
    def __init__(self, sess):
        self.session = sess

    def get_image_list(self):
        glance = glance_client(version="2", session=self.session)
        images = glance.images.list()
        image_list = [image["name"] for image in images]
        return image_list
