import datetime
import time

from protorpc import message_types
from protorpc import remote
from protorpc import messages

import rpcapp


class Note(messages.Message):

    text = messages.StringField(1, required=True)
    when = messages.IntegerField(2)


class Notes(messages.Message):
    notes = messages.MessageField(Note, 1, repeated=True)


class GetNotesRequest(messages.Message):
    limit = messages.IntegerField(1, default=10)
    on_or_before = messages.IntegerField(2)

    class Order(messages.Enum):
        WHEN = 1
        TEXT = 2
    order = messages.EnumField(Order, 3, default=Order.WHEN)


class PostService(remote.Service):

    # Add the remote decorator to indicate the service methods
    @remote.method(Note, message_types.VoidMessage)
    def post_note(self, request):

        # If the Note instance has a timestamp, use that timestamp
        if request.when is not None:
            when = datetime.datetime.utcfromtimestamp(request.when)

        # Else use the current time
        else:
            when = datetime.datetime.now()
        note = rpcapp.Greeting(content=request.text, date=when, parent=rpcapp.guestbook_key())
        note.put()
        return message_types.VoidMessage()

    @remote.method(GetNotesRequest, Notes)
    def get_notes(self, request):
        query = rpcapp.Greeting.query().order(-rpcapp.Greeting.date)

        if request.on_or_before:
            when = datetime.datetime.utcfromtimestamp(
                request.on_or_before)
            query = query.filter(rpcapp.Greeting.date <= when)

        notes = []
        for note_model in query.fetch(request.limit):
            if note_model.date:
                when = int(time.mktime(note_model.date.utctimetuple()))
            else:
                when = None
            note = Note(text=note_model.content, when=when)
            notes.append(note)

        if request.order == GetNotesRequest.Order.TEXT:
            notes.sort(key=lambda note: note.text)

        return Notes(notes=notes)
