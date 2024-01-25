from mongoengine import connect, Document, StringField


class SampleDocument(Document):
    name = StringField()


def connect_to_mongodb(database_name, mongodb_uri):
    connect(database_name, host=mongodb_uri)


def get_data_from_mongodb():
    return SampleDocument.objects.all().to_json()
