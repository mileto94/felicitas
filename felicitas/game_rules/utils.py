import json

from game_rules.forms import AddPollForm


def upload_polls_from_file(game_id, file):
    data = json.load(file)
    for poll_data in data['results']:
        poll_form = AddPollForm(data=poll_data)
        if poll_form.is_valid():
            # TODO: Handle polls and answer creation here
            # poll_form.save()
            pass
        print(poll_form.errors)
        # poll = Poll.objects.create(
        #     **poll_data
        # )
        pass
