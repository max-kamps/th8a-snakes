import re
import traceback as tb
from datetime import datetime
from collections import namedtuple

import discord
import discord.ext.commands as cmd
from dateutil import tz

from helper.common import *


nl = '\n'
locations = {
    'Twitch Channel': ('https://i.imgur.com/DKfwzn4.png', 0x6441a4, 'https://www.twitch.tv/nearlyonred')
}


class Event:
    def __init__(self):
        self.title = None
        self.description = None
        self.start_time = None
        self.end_time = None
        self.location = None

    def __repr__(self):
        return f'({self.title} @ {self.location} @ {self.start_time} - {self.end_time})'


class EventsCog(cmd.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.events = []
        self.reload_events()

    @cmd.group(name='events', invoke_without_command=True)
    @is_superuser()
    async def events_cmd(self, ctx):
        await ctx.send(content="__***Upcoming Events:***__")

        for event in sorted(self.events, key=lambda x: x.start_time):
            loc_img, loc_color, loc_url = locations.get(event.location)

            embed = discord.Embed(
                title=event.title.strip(),
                colour=discord.Colour(loc_color),
                url=loc_url,
                description=event.description.strip() + f'\n\n*{event.end_time - event.start_time}, starting at:*',
                timestamp=event.start_time)

            embed.set_author(name=event.location, url=loc_url, icon_url=loc_img)
            await ctx.send(embed=embed)
        

    @events_cmd.command(name='reload')
    @is_superuser()
    async def reload_cmd(self, ctx):
        self.reload_events()

    def reload_events(self):
        # www.nearlyonred.com/events/list/?ical=1&tribe_display=custom&start_date=2019&end_date=2100
        ical = open('/home/max/Downloads/events.ics').read()

        ical_elements = [tuple(line.split(':', maxsplit=1)) for line in ical.split('\n')]

        curr_event = None
        for element in ical_elements:
            k, v  = element

            if element == ('BEGIN', 'VEVENT'):
                curr_event = Event()

            elif element == ('END', 'VEVENT'):
                self.events.append(curr_event)

            elif k == 'SUMMARY':
                curr_event.title = v

            elif k == 'DESCRIPTION':
                curr_event.description = v.replace('\\n', '\n')

            elif k.startswith('DTSTART'):
                time_zone = tz.gettz(dict(x.split('=', maxsplit=1) for x in k.split(';', maxsplit=1)[1:])['TZID'])
                time = datetime.strptime(v, '%Y%m%dT%H%M%S').astimezone(time_zone)

                curr_event.start_time = time

            elif k.startswith('DTEND'):
                time_zone = tz.gettz(dict(x.split('=', maxsplit=1) for x in k.split(';', maxsplit=1)[1:])['TZID'])
                time = datetime.strptime(v, '%Y%m%dT%H%M%S').astimezone(time_zone)

                curr_event.end_time = time

            elif k == 'LOCATION':
                curr_event.location = v


def setup(bot):
    cog = EventsCog(bot)
    bot.add_cog(cog)
