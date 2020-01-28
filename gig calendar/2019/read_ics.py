import csv

from ics import Calendar

with open('events.ics', 'r') as f:
    data = f.read()

c = Calendar(data)

with open('2019 Events.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Event', 'Location', 'Start', 'End'])
    writer.writeheader()

    for e in c.timeline:
        print(f"Event '{e.name}' at {e.location} started {e.begin.humanize()}")
        if str(e.begin)[:4] == '2019':
            writer.writerow(
                {'Event': e.name, 'Start': e.begin, 'End': e.end, 'Location': e.location}
            )

