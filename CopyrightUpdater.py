# Copyright (c) 2019 Germán Méndez Bravo (Kronuz). All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import

import re
import datetime

import sublime_plugin


COPYRIGHT_RE_PATTERN = r'(Copyright (?:\([cC]\)|©) )([-0-9]+(?:, ?[-0-9]+)*)(.+)'
COPYRIGHT_RE = re.compile(COPYRIGHT_RE_PATTERN)


class CopyrightUpdaterCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        region = view.find(COPYRIGHT_RE_PATTERN, 0)
        copyright = view.substr(region)
        m = COPYRIGHT_RE.search(copyright)
        if m:
            prefix, years, suffix = m.groups()
            dashed = '-' in years
            comma = ', ' if ', ' in years else ','
            years_set = set()
            for year in years.split(','):
                start, dash, end = year.strip().partition('-')
                if dash:
                    year = int(end)
                    years_set.update(range(int(start), year))
                else:
                    year = int(start)
                years_set.add(year)
            years_set.add(datetime.datetime.now().year)
            years_tuples = []
            for year in sorted(years_set):
                if dashed and years_tuples and year == years_tuples[-1][-1] + 1:
                    years_tuples[-1] = (years_tuples[-1][0], year)
                else:
                    years_tuples.append((year,))
            years_strings = []
            for year in years_tuples:
                if len(year) == 1:
                    years_strings.append('{}'.format(year[0]))
                else:
                    if year[1] == year[0] + 1:
                        years_strings.append('{}'.format(year[0]))
                        years_strings.append('{}'.format(year[1]))
                    else:
                        years_strings.append('-'.join('{}'.format(y) for y in year))
            years = comma.join(years_strings)
            new_copyright = prefix + years + suffix
            if new_copyright != copyright:
                view.replace(edit, region, new_copyright)


class CopyrightUpdater(sublime_plugin.EventListener):
    updated = {}

    def on_pre_save(self, view):
        if view.is_dirty():
            copyright_updated = self.updated.get(view.buffer_id(), False)
            if not copyright_updated:
                view.run_command('copyright_updater')

    def on_modified(self, view):
        sel = view.sel()
        if sel:
            region = view.line(sel[0])
            copyright = view.substr(region)
            m = COPYRIGHT_RE.search(copyright)
            copyright_updated = bool(m)
            if copyright_updated or view.buffer_id() in self.updated:
                self.updated[view.buffer_id()] = copyright_updated

    def on_close(self, view):
        self.updated.pop(view.buffer_id(), None)
