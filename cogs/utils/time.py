import datetime
import parsedatetime as pdt
from dateutil.relativedelta import relativedelta
from .formats import plural, human_join
from discord.ext import commands
import re



class ShortTime:
    compiled = re.compile("""(?:(?P<years>[0-9])(?:years?|y)[ ]?)?
                             (?:(?P<months>[0-9]{1,2})(?:months?|mo)[ ]?)? 
                             (?:(?P<weeks>[0-9]{1,4})(?:weeks?|w)[ ]?)? 
                             (?:(?P<days>[0-9]{1,5})(?:days?|d)[ ]?)?
                             (?:(?P<hours>[0-9]{1,5})(?:hours?|h)[ ]?)? 
                             (?:(?P<minutes>[0-9]{1,5})(?:minutes?|m)[ ]?)? 
                             (?:(?P<seconds>[0-9]{1,5})(?:seconds?|s)[ ]?)? 
                          """, re.VERBOSE)


async def regex(string):
    match = ShortTime.compiled.match(string)
    a = re.sub(ShortTime.compiled,"",match.string)
    return "a", a

    #if match is not None and match.group(0):
        #time_list.append(match.group())
        #remaining = string[match.end():].strip()
        #return await check_constraints(remaining)
    #print(result)
    #return result


async def duration(ctx, string):
    match = ShortTime.compiled.match(string)
    times = match.groupdict()
    reason = re.sub(ShortTime.compiled,"",match.string)
    years = 0
    months = 0
    weeks = 0
    days = 0
    hours = 0
    minutes = 0
    seconds = 0
    if match.group(0) is not '':
        if times['years'] is not None:
            years = int(times['years'])
        elif times['months'] is not None:
            months = int(times['months'])
        elif times['weeks'] is not None:
            weeks = int(times['weeks'])
        elif times['days'] is not None:
            days = int(times['days'])
        elif times['hours'] is not None:
            hours = int(times['hours'])
        elif times['minutes'] is not None:
            minutes = int(times['minutes'])
        elif times['seconds'] is not None:
            seconds = int(times["seconds"])
    else:
        raise commands.BadArgument("Your time format was incorrect or you did not include one")
    time = relativedelta(years=years, months=months, weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)
    now = datetime.datetime.now()
    time = (now + time) - now
    return time, reason

def human_timedelta(dt, *, source=None, accuracy=3, brief=False, suffix=True):
    now = source or datetime.datetime.utcnow()
    # Microsecond free zone
    now = now.replace(microsecond=0)
    dt = dt.replace(microsecond=0)

    # This implementation uses relativedelta instead of the much more obvious
    # divmod approach with seconds because the seconds approach is not entirely
    # accurate once you go over 1 week in terms of accuracy since you have to
    # hardcode a month as 30 or 31 days.
    # A query like "11 months" can be interpreted as "!1 months and 6 days"
    if dt > now:
        delta = relativedelta(dt, now)
        suffix = ''
    else:
        delta = relativedelta(now, dt)
        suffix = ' ago' if suffix else ''

    attrs = [
        ('year', 'y'),
        ('month', 'mo'),
        ('day', 'd'),
        ('hour', 'h'),
        ('minute', 'm'),
        ('second', 's'),
    ]

    output = []
    for attr, brief_attr in attrs:
        elem = getattr(delta, attr + 's')
        if not elem:
            continue

        if attr == 'day':
            weeks = delta.weeks
            if weeks:
                elem -= weeks * 7
                if not brief:
                    output.append(format(plural(weeks), 'week'))
                else:
                    output.append(f'{weeks}w')

        if elem <= 0:
            continue

        if brief:
            output.append(f'{elem}{brief_attr}')
        else:
            output.append(format(plural(elem), attr))

    if accuracy is not None:
        output = output[:accuracy]

    if len(output) == 0:
        return 'now'
    else:
        if not brief:
            return human_join(output, final='and') + suffix
        else:
            return ' '.join(output) + suffix
